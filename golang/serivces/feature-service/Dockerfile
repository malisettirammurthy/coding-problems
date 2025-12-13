# =========================
# Stage 1: Build
# =========================
FROM golang:1.25.3-alpine AS builder

# Install build tools (just in case)
RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app

# Pre-copy go.mod/go.sum for dependency caching
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the source
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o server ./cmd/server

# =========================
# Stage 2: Runtime
# =========================
FROM alpine:3.20

# Add CA certificates & timezone data (for outbound HTTPS / logs)
RUN apk add --no-cache ca-certificates tzdata

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/server /app/server

# Expose port (for documentation purposes)
EXPOSE 8080

# Drop privileges
USER appuser

# Default PORT (can be overridden)
ENV PORT=8080

# Run the server
ENTRYPOINT ["/app/server"]
