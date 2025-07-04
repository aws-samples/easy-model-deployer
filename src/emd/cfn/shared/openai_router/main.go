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
	"github.com/aws/aws-sdk-go/service/secretsmanager"
	"github.com/gin-gonic/gin"
)

var (
	sagemakerClient   *sagemakerruntime.SageMakerRuntime
	cfnClient        *cloudformation.CloudFormation
	secretsClient    *secretsmanager.SecretsManager
	modelEndpointMap = make(map[string]string)
	modelApiKeyMap   = make(map[string]string) // Map to store model-name/api-key pairs
	modelMapMutex    sync.RWMutex
	apiKeyMapMutex   sync.RWMutex
	httpTransport    = &http.Transport{
		MaxIdleConns:        100,
		IdleConnTimeout:     90 * time.Second,
		DisableCompression:  false,
		MaxIdleConnsPerHost: 20,
		// Add buffer sizes to handle large responses
		ReadBufferSize:  32 * 1024,  // 32KB read buffer
		WriteBufferSize: 32 * 1024,  // 32KB write buffer
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
	logLevel := getEnv("LOG_LEVEL", "INFO")

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
	secretsClient = secretsmanager.New(sess)

	// Load API keys from AWS Secrets Manager
	if err := loadApiKeysFromSecrets(); err != nil {
		log.Printf("Warning: Failed to load API keys from secrets: %v", err)
	}

	// Discover initial model endpoints
	if err := discoverModelEndpoints(); err != nil {
		log.Fatalf("Failed to discover model endpoints: %v", err)
	}

	// Start background refresh of maps every hour
	go startPeriodicRefresh(1 * time.Hour)

	// Create router with ALB support
	router := gin.Default()

	// Add request logging middleware
	router.Use(func(c *gin.Context) {
		start := time.Now()

		// Trust X-Forwarded-For header
		if forwardedFor := c.GetHeader("X-Forwarded-For"); forwardedFor != "" {
			c.Request.RemoteAddr = strings.Split(forwardedFor, ",")[0]
		}

		c.Next()

		// Log request details after processing
		duration := time.Since(start)
		if logLevel == "DEBUG" {
			log.Printf("[DEBUG] %s %s - Status: %d, Duration: %v, Size: %d bytes",
				c.Request.Method, c.Request.URL.Path, c.Writer.Status(), duration, c.Writer.Size())
		}
	})

	// Health checks (ALB requires / and /health)
	router.GET("/", albHealthHandler)
	router.GET("/health", albHealthHandler)
	router.GET("/ping", pingHandler) // Kept for backward compatibility

	// API routes that can use either payload model or path parameters
	modelFieldApi := router.Group("/v1")
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


// loadApiKeysFromSecrets loads API keys from AWS Secrets Manager
func loadApiKeysFromSecrets() error {
	apiKeyMapMutex.Lock()
	defer apiKeyMapMutex.Unlock()

	// Clear existing map
	for k := range modelApiKeyMap {
		delete(modelApiKeyMap, k)
	}

	// Get the secret value
	secretName := "EMD-APIKey-Secrets"
	input := &secretsmanager.GetSecretValueInput{
		SecretId: aws.String(secretName),
	}

	result, err := secretsClient.GetSecretValue(input)
	if err != nil {
		return fmt.Errorf("failed to get secret value: %v", err)
	}

	// Parse the secret value as JSON
	var secretData map[string]string
	if err := json.Unmarshal([]byte(*result.SecretString), &secretData); err != nil {
		return fmt.Errorf("failed to parse secret value: %v", err)
	}

	// Store model-name/api-key pairs in the map
	for modelName, apiKey := range secretData {
		modelApiKeyMap[modelName] = apiKey
	}

	log.Printf("Loaded %d API keys from AWS Secrets Manager", len(modelApiKeyMap))
	return nil
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
				endpoint = "sagemaker:" + *output.OutputValue
			case "ECSServiceConnect":
				endpoint = "ecs:" + *output.OutputValue
			}
		}

		if model != "" && endpoint != "" {
			modelEndpointMap[model] = endpoint
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

	// log.Printf("[DEBUG] ECS proxy handler - URL: %s, Streaming: %v", endpointURL, streamRequest.Stream)

	client := &http.Client{
		Timeout: 15 * time.Minute,
		Transport: &http.Transport{
			MaxIdleConns:        100,
			IdleConnTimeout:     90 * time.Second,
			DisableCompression:  false,
			MaxIdleConnsPerHost: 20,
			// Add buffer sizes to handle large responses
			ReadBufferSize:      32 * 1024,  // 32KB read buffer
			WriteBufferSize:     32 * 1024,  // 32KB write buffer
			// Add response header timeout for better reliability
			ResponseHeaderTimeout: 30 * time.Second,
		},
	}

	// Preserve the original request path and append to endpoint URL
	baseURL := strings.TrimRight(endpointURL, "/")
	path := c.Request.URL.Path
	fullURL := baseURL + path
	// log.Printf("[DEBUG] Proxying request to URL %s", fullURL)

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

		// Create channel for streaming responses (same pattern as SageMaker)
		stream := make(chan []byte)
		closeOnce := sync.Once{}

		// Start streaming in a goroutine (same pattern as SageMaker)
		go func() {
			defer closeOnce.Do(func() { close(stream) })

			// Buffer for accumulating partial chunks (same as SageMaker)
			var buffer strings.Builder
			readBuffer := make([]byte, 4096)

			for {
				n, err := resp.Body.Read(readBuffer)
				if n > 0 {
					chunk := string(readBuffer[:n])
					// log.Printf("[DEBUG] ECS received chunk: %s", chunk)

					// Add chunk to buffer
					buffer.WriteString(chunk)
					bufferContent := buffer.String()

					// Process complete lines from buffer (same logic as SageMaker)
					for strings.Contains(bufferContent, "\n") {
						lines := strings.SplitN(bufferContent, "\n", 2)
						if len(lines) < 2 {
							break
						}

						line := strings.TrimSpace(lines[0])
						if line != "" {
							// Check if it's SSE data line with JSON
							if strings.HasPrefix(line, "data: ") {
								jsonPart := strings.TrimPrefix(line, "data: ")
								if jsonPart != "[DONE]" && jsonPart != "" {
									// Validate JSON content
									if !json.Valid([]byte(jsonPart)) {
										log.Printf("[WARNING] Invalid JSON in ECS SSE: %s", jsonPart)
										// Skip invalid JSON to prevent client parsing errors
										bufferContent = lines[1]
										buffer.Reset()
										buffer.WriteString(bufferContent)
										continue
									}
								}
							}

							// Forward the complete line as-is
							stream <- []byte(line + "\n")
						} else {
							// Forward empty lines (important for SSE format)
							stream <- []byte("\n")
						}

						// Update buffer with remaining content
						bufferContent = lines[1]
						buffer.Reset()
						buffer.WriteString(bufferContent)
					}
				}

				if err != nil {
					if err == io.EOF {
						// Process any remaining data in buffer
						if buffer.Len() > 0 {
							remaining := strings.TrimSpace(buffer.String())
							if remaining != "" {
								stream <- []byte(remaining + "\n")
							}
						}
						return // End of stream
					}
					log.Printf("[ERROR] Error reading from ECS stream: %v", err)
					return
				}
			}
		}()

		// Stream responses to client (same pattern as SageMaker)
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

		// Forward the response with better error handling
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			c.JSON(500, gin.H{"error": fmt.Sprintf("Failed to read response body: %v", err)})
			return
		}

		// Check for empty response
		if len(body) == 0 {
			log.Printf("[ERROR] Empty response from ECS endpoint")
			c.JSON(500, gin.H{"error": "Empty response from ECS endpoint"})
			return
		}

		// Validate JSON response if content type is application/json
		contentType := resp.Header.Get("Content-Type")
		if strings.Contains(contentType, "application/json") {
			if !json.Valid(body) {
				bodyStr := string(body)
				log.Printf("[ERROR] Invalid JSON response from ECS endpoint: %s", bodyStr)
				if isPartialJSON(bodyStr) {
					log.Printf("[ERROR] Detected partial JSON response from ECS, likely truncated")
					c.JSON(500, gin.H{"error": "Response was truncated, please try again"})
				} else {
					c.JSON(500, gin.H{"error": "Invalid JSON response from backend"})
				}
				return
			}
			// log.Printf("[DEBUG] ECS response length: %d bytes", len(body))
		}

		// Copy response headers
		for k, v := range resp.Header {
			if k != "Content-Length" { // Let Gin handle Content-Length
				c.Header(k, strings.Join(v, ","))
			}
		}

		c.Data(resp.StatusCode, contentType, body)
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

// findCompleteJSON finds the end position of the first complete JSON object in the string
// Returns -1 if no complete JSON object is found
func findCompleteJSON(s string) int {
	if len(s) == 0 {
		return -1
	}

	// Track brace/bracket depth
	depth := 0
	inString := false
	escaped := false

	for i, char := range s {
		if escaped {
			escaped = false
			continue
		}

		switch char {
		case '\\':
			if inString {
				escaped = true
			}
		case '"':
			if !escaped {
				inString = !inString
			}
		case '{', '[':
			if !inString {
				depth++
			}
		case '}', ']':
			if !inString {
				depth--
				if depth == 0 {
					// Found complete JSON object, return position after the closing brace
					return i + 1
				}
			}
		}
	}

	// No complete JSON object found
	return -1
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

// startPeriodicRefresh runs a background goroutine that refreshes the model maps at the specified interval
func startPeriodicRefresh(interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			log.Println("Refreshing model maps...")

			// Refresh API keys
			if err := loadApiKeysFromSecrets(); err != nil {
				log.Printf("Warning: Failed to refresh API keys: %v", err)
			} else {
				log.Printf("Successfully refreshed API keys, loaded %d keys", len(modelApiKeyMap))
			}

			// Refresh endpoints
			if err := discoverModelEndpoints(); err != nil {
				log.Printf("Warning: Failed to refresh model endpoints: %v", err)
			} else {
				log.Printf("Successfully refreshed model endpoints, loaded %d endpoints", len(modelEndpointMap))
			}
		}
	}
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

	// Authentication check
	// Check if the model requires authentication
	apiKeyMapMutex.RLock()
	apiKey, requiresAuth := modelApiKeyMap[modelKey]
	apiKeyMapMutex.RUnlock()

	if requiresAuth {
		// Model requires authentication, validate the token
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(401, gin.H{"error": "Authorization header required for this model"})
			return
		}

		// Validate Bearer token against model-specific API key
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" || parts[1] != apiKey {
			c.JSON(401, gin.H{"error": "Invalid API key for this model"})
			return
		}
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

	// Parse endpoint type
	var endpointType, endpointAddress string
	if strings.HasPrefix(endpointName, "sagemaker:") {
		endpointType = "sagemaker"
		endpointAddress = strings.TrimPrefix(endpointName, "sagemaker:")
	} else if strings.HasPrefix(endpointName, "ecs:") {
		endpointType = "ecs"
		endpointAddress = strings.TrimPrefix(endpointName, "ecs:")
	} else {
		c.JSON(500, gin.H{"error": "invalid endpoint format"})
		return
	}

	// Check if streaming request by looking for "stream":true in JSON
	var streamRequest struct {
		Stream bool `json:"stream"`
	}
	_ = json.Unmarshal(modifiedBytes, &streamRequest) // Best effort check

	if endpointType == "sagemaker" {
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
					EndpointName: aws.String(endpointAddress),
					ContentType:  aws.String("application/json"),
					Body:         modifiedBytes,
				}

				resp, err := sagemakerClient.InvokeEndpointWithResponseStreamWithContext(ctx, input)
				if err != nil {
					log.Printf("[ERROR] Failed to invoke endpoint: %v", err)
					stream <- []byte(`data: {"error": "` + err.Error() + `"}` + "\n\n")
					return
				}
				// log.Println("[DEBUG] Successfully established streaming connection")

				eventStream := resp.GetStream()
				defer eventStream.Close()

				// Enhanced buffer for accumulating partial chunks with better handling
				var buffer strings.Builder
				var lastValidJSON string
				chunkCount := 0

				for event := range eventStream.Events() {
					switch e := event.(type) {
					case *sagemakerruntime.PayloadPart:
						if len(e.Bytes) == 0 {
							// log.Printf("[WARNING] Received empty payload chunk")
							continue
						}

						chunk := string(e.Bytes)
						chunkCount++
						// log.Printf("[DEBUG] Received chunk #%d: %s", chunkCount, chunk)

						// Add chunk to buffer
						buffer.WriteString(chunk)
						bufferContent := buffer.String()

						// Process complete lines from buffer with enhanced validation
						for strings.Contains(bufferContent, "\n") {
							lines := strings.SplitN(bufferContent, "\n", 2)
							if len(lines) < 2 {
								break
							}

							line := strings.TrimSpace(lines[0])
							if line != "" {
								// Enhanced JSON validation with recovery mechanisms
								if json.Valid([]byte(line)) {
									lastValidJSON = line
									// Format as proper SSE event and send
									formattedChunk := "data: " + line

									// Check for finish_reason to end stream (including length limit)
									if strings.Contains(line, `"finish_reason":"stop"`) ||
									   strings.Contains(line, `"finish_reason": "stop"`) ||
									   strings.Contains(line, `"finish_reason":"length"`) ||
									   strings.Contains(line, `"finish_reason": "length"`) {
										// log.Printf("[DEBUG] Detected finish_reason, ending stream")
										stream <- []byte(formattedChunk + "\n\n")
										return // Exit the goroutine completely
									}

									// Forward as properly formatted SSE event
									stream <- []byte(formattedChunk + "\n\n")
								} else {
									log.Printf("[WARNING] Invalid JSON line (chunk #%d): %s", chunkCount, line)
									// Try to recover by checking if it's a partial JSON that can be completed
									if isPartialJSON(line) {
										log.Printf("[WARNING] Detected partial JSON, attempting recovery")
										// Don't forward partial JSON, wait for more data
									} else {
										log.Printf("[WARNING] Completely invalid JSON, skipping")
									}
								}
							}

							// Update buffer with remaining content
							bufferContent = lines[1]
							buffer.Reset()
							buffer.WriteString(bufferContent)
						}

					case *sagemakerruntime.InternalStreamFailure:
						log.Printf("[ERROR] SageMaker stream failure: %v", e.Error())
						stream <- []byte(`data: {"error": "` + e.Error() + `"}` + "\n\n")
						return
					}
				}

				// Process any remaining data in buffer with enhanced validation
				if buffer.Len() > 0 {
					remaining := strings.TrimSpace(buffer.String())
					if remaining != "" {
						if json.Valid([]byte(remaining)) {
							stream <- []byte("data: " + remaining + "\n\n")
						} else {
							log.Printf("[WARNING] Discarding invalid JSON remainder (total chunks: %d): %s", chunkCount, remaining)
							// If we have a last valid JSON and this looks like a partial, try to recover
							if isPartialJSON(remaining) && lastValidJSON != "" {
								log.Printf("[WARNING] Final chunk appears to be partial JSON, stream may have been truncated")
							}
						}
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
			// Non-streaming request with timeout context
			ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Minute)
			defer cancel()

			output, err := sagemakerClient.InvokeEndpointWithContext(ctx, &sagemakerruntime.InvokeEndpointInput{
				EndpointName: aws.String(endpointAddress),
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

			// Validate JSON before forwarding to catch truncation issues
			responseStr := string(output.Body)
			if !json.Valid(output.Body) {
				log.Printf("[ERROR] Invalid JSON response from SageMaker: %s", responseStr)
				// Try to detect if it's a partial JSON
				if isPartialJSON(responseStr) {
					log.Printf("[ERROR] Detected partial JSON response, likely truncated")
					c.JSON(500, gin.H{"error": "Response was truncated, please try again"})
				} else {
					c.JSON(500, gin.H{"error": "Invalid JSON response from backend"})
				}
				return
			}

			// log.Printf("[DEBUG] SageMaker response length: %d bytes", len(output.Body))
			// Set proper headers and forward response
			c.Header("Content-Type", "application/json")
			c.Header("Content-Length", fmt.Sprintf("%d", len(output.Body)))
			c.Data(200, "application/json", output.Body)
		}
	} else if endpointType == "ecs" {
		// Handle ECS endpoint
		baseURL := endpointAddress
		// log.Printf("[DEBUG] Proxying request to ECS endpoint %s", baseURL)
		httpProxyHandler(c, baseURL, modifiedBytes)
	}
}
