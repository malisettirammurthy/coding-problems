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
	"github.com/ram/audit-microservice/internal/handlers"
	"github.com/ram/audit-microservice/internal/services"
)

func main() {

	log.Println("Audit Server starting in IN-MEMORY mode...")

	// ---- Router + services ----
	r := chi.NewRouter()

	// Global middlewares
	r.Use(middleware.RequestID) // adds X-Request-ID
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger) // <-- logs every request
	r.Use(middleware.Recoverer)

	// Liveness and Readiness probe endpoint.
	r.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("ok"))
	})

	// Audit service + routes
	auditSvc := services.NewInMemoryAuditService()
	auditHandler := handlers.NewAuditHandler(auditSvc)

	r.Route("/api/v1/audits", func(r chi.Router) {
		auditHandler.RegisterRoutes(r)
	})

	// Port from env (default 8080)
	port := os.Getenv("PORT")
	if port == "" {
		port = "8081"
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
		log.Printf("Audit Server starting on :%s", port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Listen error: %v", err)
		}
	}()

	// Wait for interrupt - Graceful shutdown
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)

	<-stop
	log.Println("Shutting down Audit server...")

	// Graceful timeout context
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Audit Server Shutdown failed %v", err)
	}
	log.Println("Audit Server exited properly")
}
