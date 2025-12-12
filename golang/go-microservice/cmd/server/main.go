package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/ram/microservice/internal/handlers"
	"github.com/ram/microservice/internal/services"
)

func main() {
	// ---- DB setup ----
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		log.Fatal("DATABASE_URL is not set")
	}

	ctx := context.Background()
	pool, err := pgxpool.New(ctx, dbURL)
	if err != nil {
		log.Fatalf("failed to create db pool: %v", err)
	}
	defer pool.Close()

	if err := pool.Ping(ctx); err != nil {
		log.Fatalf("failed to ping db: %v", err)
	}

	// ---- Router + services ----
	r := chi.NewRouter()

	// Global middlewares
	r.Use(middleware.RequestID) // adds X-Request-ID
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger) // <-- logs every request
	r.Use(middleware.Recoverer)

	// Health check end point
	r.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("ok"))
	})

	// // Feature service + routes
	// featureSvc := services.NewInMemoryFeatureService()
	// featureHandler := handlers.NewFeatureService(featureSvc)

	// Postgres baked feature service + routes
	featureSvc := services.NewPostgresFeatureService(pool)
	featureHandler := handlers.NewFeatureServiceHandler(featureSvc)

	r.Route("/api/v1/features", func(r chi.Router) {
		featureHandler.RegisterRoutes(r)
	})

	// Port from env (default 8080)
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	srv := &http.Server{
		Addr:         ":" + port,
		Handler:      r,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// Start server
	go func() {
		log.Println("Server starting on :8080")
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Listen error: %v", err)
		}
	}()

	// Wait for interrupt - Graceful shutdown
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)

	<-stop
	log.Println("Shuttind down server...")

	// Graceful timeout context
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server Shutdown failed %v", err)
	}
	log.Println("Server exited properly")
}
