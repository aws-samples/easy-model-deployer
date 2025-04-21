# Stage 1: Build with optimizations
FROM public.ecr.aws/docker/library/golang:1.23-alpine3.21 AS builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev git

WORKDIR /app
COPY go.mod go.sum ./

ARG GOPROXY=direct
ENV GOPROXY=${GOPROXY}

RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-w -s -extldflags '-static'" \
    -trimpath -buildvcs=false \
    -o /app/proxy

# Stage 2: Minimal runtime image
FROM public.ecr.aws/docker/library/alpine:3.21

# Security hardening
RUN apk add --no-cache ca-certificates tzdata && \
    addgroup -S app && adduser -S app -G app && \
    mkdir -p /app && chown app:app /app

WORKDIR /app
COPY --from=builder --chown=app:app /app/proxy /app/proxy
COPY --from=builder --chown=app:app /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

USER app

# Environment variables
ENV PORT=8080 \
    HOST=0.0.0.0 \
    LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=5s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

EXPOSE 8080
ENTRYPOINT ["/app/proxy"]
