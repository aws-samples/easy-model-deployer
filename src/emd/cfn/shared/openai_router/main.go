package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cloudformation"
	"github.com/aws/aws-sdk-go/service/sagemakerruntime"
	"github.com/gin-gonic/gin"
)

var (
	sagemakerClient   *sagemakerruntime.SageMakerRuntime
	cfnClient        *cloudformation.CloudFormation
	modelEndpointMap = make(map[string]string)
	modelMapMutex    sync.RWMutex
	httpTransport    = &http.Transport{
		MaxIdleConns:        100,
		IdleConnTimeout:     90 * time.Second,
		DisableCompression:  false,
		MaxIdleConnsPerHost: 20,
	}
	httpClient = &http.Client{
		Transport: httpTransport,
		Timeout:   15 * time.Minute, // Extended for long-running LLM requests
	}
)

func main() {
	// Load configuration from environment
	port := getEnv("PORT", "8080")
	host := getEnv("HOST", "0.0.0.0")
	logLevel := getEnv("LOG_LEVEL", "DEBUG")

	// Configure logging
	if logLevel == "DEBUG" {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	// Initialize AWS session with default region
	sess, err := session.NewSession()
	if err != nil {
		log.Fatalf("Failed to create AWS session: %v", err)
	}
	sagemakerClient = sagemakerruntime.New(sess)
	cfnClient = cloudformation.New(sess)

	// Discover initial model endpoints
	if err := discoverModelEndpoints(); err != nil {
		log.Fatalf("Failed to discover model endpoints: %v", err)
	}

	// Create router with ALB support
	router := gin.Default()
	router.Use(func(c *gin.Context) {
		// Trust X-Forwarded-For header
		if forwardedFor := c.GetHeader("X-Forwarded-For"); forwardedFor != "" {
			c.Request.RemoteAddr = strings.Split(forwardedFor, ",")[0]
		}
		c.Next()
	})

	// Health checks (ALB requires / and /health)
	router.GET("/", albHealthHandler)
	router.GET("/health", albHealthHandler)
	router.GET("/ping", pingHandler) // Kept for backward compatibility

	// API routes that can use either payload model or path parameters
	modelFieldApi := router.Group("/v1")
	modelFieldApi.Use(authMiddleware())
	{
		modelFieldApi.GET("/models", modelsHandler)
		modelFieldApi.POST("/chat/completions", requestHandler)
		modelFieldApi.POST("/embeddings", requestHandler)
		modelFieldApi.POST("/rerank", requestHandler)
		modelFieldApi.POST("/invocations", requestHandler)
	}

	// Create server with timeouts
	srv := &http.Server{
		Addr:         host + ":" + port,
		Handler:      router,
		ReadTimeout:  10 * time.Minute,  // LLM requests can be long
		WriteTimeout: 10 * time.Minute,  // LLM responses can be large
		IdleTimeout:  120 * time.Second, // Keep-alive connections
	}

	// Run server in goroutine
	go func() {
		log.Printf("Starting server on %s:%s", host, port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed: %v", err)
		}
	}()

	// Graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server shutdown failed: %v", err)
	}
	log.Println("Server exited properly")
}

func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func pingHandler(c *gin.Context) {
	c.JSON(200, gin.H{"status": "ok"})
}

func albHealthHandler(c *gin.Context) {
	// ALB requires simple 200 response without body
	c.Status(200)
}

func healthHandler(c *gin.Context) {
	c.JSON(200, gin.H{"status": "healthy"})
}

// modelsHandler returns a list of available models in OpenAI-compatible format
func modelsHandler(c *gin.Context) {
	modelMapMutex.RLock()
	defer modelMapMutex.RUnlock()

	models := make([]map[string]string, 0)
	for modelKey := range modelEndpointMap {
		models = append(models, map[string]string{
			"id":        modelKey,
			"object":    "model",
			"owned_by": "easy-model-deployer",
		})
	}

	c.JSON(200, gin.H{
		"object": "list",
		"data":   models,
	})
}

// authMiddleware checks for valid API key if Authorization header is present
func authMiddleware() gin.HandlerFunc {
	apiKey := getEnv("API_KEY", "")
	return func(c *gin.Context) {
		// Skip validation if no API key configured
		if apiKey == "" {
			c.Next()
			return
		}

		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(401, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}

		// Validate Bearer token
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" || parts[1] != apiKey {
			c.JSON(401, gin.H{"error": "Invalid API key"})
			c.Abort()
			return
		}

		c.Next()
	}
}

func discoverModelEndpoints() error {
	modelMapMutex.Lock()
	defer modelMapMutex.Unlock()

	resp, err := cfnClient.ListStacks(&cloudformation.ListStacksInput{
		StackStatusFilter: []*string{
			aws.String("CREATE_COMPLETE"),
			aws.String("UPDATE_COMPLETE"),
		},
	})
	if err != nil {
		return err
	}

	for _, stack := range resp.StackSummaries {
		if !strings.HasPrefix(*stack.StackName, "EMD-Model-") {
			continue
		}

		desc, err := cfnClient.DescribeStacks(&cloudformation.DescribeStacksInput{
			StackName: stack.StackName,
		})
		if err != nil {
			log.Printf("Error describing stack %s: %v", *stack.StackName, err)
			continue
		}

		if len(desc.Stacks) == 0 {
			continue
		}

		var model, endpoint string
		for _, output := range desc.Stacks[0].Outputs {
			switch *output.OutputKey {
			case "Model":
				model = *output.OutputValue
			case "SageMakerEndpointName":
				endpoint = *output.OutputValue
			case "PublicLoadBalancerDNSName":
				endpoint = *output.OutputValue
			}
		}

		if model != "" && endpoint != "" {
			modelEndpointMap[model] = endpoint
			log.Printf("Discovered model %s -> endpoint %s", model, endpoint)
		}
	}
	return nil
}

// httpProxyHandler handles HTTP proxy requests to external endpoints
func httpProxyHandler(c *gin.Context, endpointURL string, inputBytes []byte) {
	// Check if streaming request
	var streamRequest struct {
		Stream bool `json:"stream"`
	}
	_ = json.Unmarshal(inputBytes, &streamRequest) // Best effort check

	client := &http.Client{
		Timeout: 15 * time.Minute,
		Transport: &http.Transport{
			MaxIdleConns:        100,
			IdleConnTimeout:     90 * time.Second,
			DisableCompression:  false,
			MaxIdleConnsPerHost: 20,
		},
	}

	// Preserve the original request path and append to endpoint URL
	baseURL := strings.TrimRight(endpointURL, "/")
	path := c.Request.URL.Path
	fullURL := baseURL + path

	req, err := http.NewRequest(c.Request.Method, fullURL, bytes.NewReader(inputBytes))
	if err != nil {
		c.JSON(500, gin.H{"error": fmt.Sprintf("Failed to create HTTP request: %v", err)})
		return
	}

	// Copy headers from original request
	for k, v := range c.Request.Header {
		req.Header[k] = v
	}

	if streamRequest.Stream {
		// Set streaming headers
		c.Header("Content-Type", "text/event-stream")
		c.Header("Cache-Control", "no-cache")
		c.Header("Connection", "keep-alive")

		// Make the request
		resp, err := client.Do(req)
		if err != nil {
			c.JSON(500, gin.H{"error": fmt.Sprintf("HTTP request failed: %v", err)})
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			body, _ := io.ReadAll(resp.Body)
			c.JSON(resp.StatusCode, gin.H{"error": string(body)})
			return
		}

		// Stream the response
		c.Stream(func(w io.Writer) bool {
			_, err := io.Copy(w, resp.Body)
			return err == nil
		})
	} else {
		// Non-streaming request
		resp, err := client.Do(req)
		if err != nil {
			c.JSON(500, gin.H{"error": fmt.Sprintf("HTTP request failed: %v", err)})
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			body, _ := io.ReadAll(resp.Body)
			c.JSON(resp.StatusCode, gin.H{"error": string(body)})
			return
		}

		// Forward the response
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			c.JSON(500, gin.H{"error": fmt.Sprintf("Failed to read response body: %v", err)})
			return
		}

		c.Data(resp.StatusCode, resp.Header.Get("Content-Type"), body)
	}
}

// isPartialJSON checks if a string might be a partial JSON document
func isPartialJSON(s string) bool {
	// Check for common partial JSON patterns
	if strings.HasPrefix(s, "{") && !strings.HasSuffix(s, "}") {
		return true
	}
	if strings.HasPrefix(s, "[") && !strings.HasSuffix(s, "]") {
		return true
	}

	// Count open vs close braces
	openBraces := strings.Count(s, "{") + strings.Count(s, "[")
	closeBraces := strings.Count(s, "}") + strings.Count(s, "]")
	return openBraces > closeBraces
}

func getEndpointForModel(modelKey string) (string, error) {
	// Only accept model_id/model_tag format
	if !strings.Contains(modelKey, "/") {
		return "", fmt.Errorf("model key must be in format model_id/model_tag")
	}

	modelMapMutex.RLock()
	endpoint, exists := modelEndpointMap[modelKey]
	modelMapMutex.RUnlock()

	if exists {
		return endpoint, nil
	}

	// Refresh mapping and try again
	if err := discoverModelEndpoints(); err != nil {
		return "", err
	}

	modelMapMutex.RLock()
	endpoint, exists = modelEndpointMap[modelKey]
	modelMapMutex.RUnlock()

	if !exists {
		return "", fmt.Errorf("model %s not found in any endpoint", modelKey)
	}
	return endpoint, nil
}

func requestHandler(c *gin.Context) {
	// Read raw body once and reuse it
	inputBytes, err := c.GetRawData()
	if err != nil {
		c.JSON(500, gin.H{"error": "Failed to read request body"})
		return
	}

	var modelKey string
	var payload struct {
		Model string `json:"model"`
	}

	// Try to parse model from payload
	if err := json.Unmarshal(inputBytes, &payload); err == nil && payload.Model != "" {
		// Use model from payload if present
		if !strings.Contains(payload.Model, "/") {
			modelKey = payload.Model + "/dev"
		} else {
			modelKey = payload.Model
		}
	} else {
		c.JSON(400, gin.H{"error": "Model field in payload is required"})
		return
	}

	// Get endpoint for model
	endpointName, err := getEndpointForModel(modelKey)
	if err != nil {
		c.JSON(404, gin.H{"error": err.Error()})
		return
	}

	// Create modified payload with just modelID (no modelTag)
	var payloadData map[string]interface{}
	if err := json.Unmarshal(inputBytes, &payloadData); err != nil {
		c.JSON(400, gin.H{"error": "Invalid JSON payload"})
		return
	}

	// Extract modelID from model field (remove modelTag if present)
	if modelVal, ok := payloadData["model"].(string); ok {
		modelParts := strings.Split(modelVal, "/")
		payloadData["model"] = modelParts[0] // Keep only modelID
	}

	modifiedBytes, err := json.Marshal(payloadData)
	if err != nil {
		c.JSON(500, gin.H{"error": "Failed to modify payload"})
		return
	}

	// Check if endpoint is HTTP URL
	if strings.HasPrefix(endpointName, "http://") || strings.HasPrefix(endpointName, "https://") {
		log.Printf("[DEBUG] Proxying request to external endpoint %s", endpointName)
		httpProxyHandler(c, endpointName, modifiedBytes)
		return
	}

	// Check if streaming request by looking for "stream":true in JSON
	var streamRequest struct {
		Stream bool `json:"stream"`
	}
	_ = json.Unmarshal(modifiedBytes, &streamRequest) // Best effort check

	if streamRequest.Stream {
		// Set streaming headers
		c.Header("Content-Type", "text/event-stream")
		c.Header("Cache-Control", "no-cache")
		c.Header("Connection", "keep-alive")

		// Create channel for streaming responses
		stream := make(chan []byte)
		closeOnce := sync.Once{}

			// Start streaming in a goroutine
			go func() {
				defer closeOnce.Do(func() { close(stream) })

				ctx, cancel := context.WithTimeout(c.Request.Context(), 5*time.Minute)
				defer cancel()

				input := &sagemakerruntime.InvokeEndpointWithResponseStreamInput{
					EndpointName: aws.String(endpointName),
					ContentType:  aws.String("application/json"),
					Body:         modifiedBytes,
				}

				resp, err := sagemakerClient.InvokeEndpointWithResponseStreamWithContext(ctx, input)
				if err != nil {
					log.Printf("[ERROR] Failed to invoke endpoint: %v", err)
					stream <- []byte(`data: {"error": "` + err.Error() + `"}` + "\n\n")
					return
				}
				log.Println("[DEBUG] Successfully established streaming connection")

				eventStream := resp.GetStream()
				defer eventStream.Close()


				for event := range eventStream.Events() {
					switch e := event.(type) {
					case *sagemakerruntime.PayloadPart:
						if len(e.Bytes) == 0 {
							log.Printf("[WARNING] Received empty payload chunk")
							continue
						}

						chunk := string(e.Bytes)
						log.Printf("[DEBUG] Received chunk: %s", chunk)

						// Check for finish_reason=stop to end stream
						if strings.Contains(chunk, `"finish_reason":"stop"`) ||
						   strings.Contains(chunk, `"finish_reason": "stop"`) {
							log.Printf("[DEBUG] Detected finish_reason=stop, ending stream")
							// stream <- []byte("data: " + chunk + "\n\n")
							break
						}

						// Forward chunk as-is in SSE format
						stream <- []byte(chunk + "\n\n")
					case *sagemakerruntime.InternalStreamFailure:
						stream <- []byte(`data: {"error": "` + e.Error() + `"}` + "\n\n")
						return
					}
				}
				// Send final done message
				stream <- []byte("data: [DONE]\n\n")
			}()

		// Stream responses to client
		c.Stream(func(w io.Writer) bool {
			if msg, ok := <-stream; ok {
				_, err := w.Write(msg)
				if err != nil {
					return false
				}
				return true
			}
			return false
		})
	} else {
		// Non-streaming request
		output, err := sagemakerClient.InvokeEndpoint(&sagemakerruntime.InvokeEndpointInput{
			EndpointName: aws.String(endpointName),
			ContentType:  aws.String("application/json"),
			Body:         modifiedBytes,
		})

		if err != nil {
			log.Printf("[ERROR] SageMaker invocation failed: %v", err)
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}

		if len(output.Body) == 0 {
			log.Printf("[ERROR] Empty response from SageMaker endpoint")
			c.JSON(500, gin.H{"error": "empty response from SageMaker endpoint"})
			return
		}

		log.Printf("[DEBUG] SageMaker response: %s", string(output.Body))
		// Forward raw SageMaker response
		c.Data(200, "application/json", output.Body)
	}
}
