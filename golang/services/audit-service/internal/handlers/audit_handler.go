package handlers

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/ram/audit-microservice/internal/services"
)

type AuditHandler struct {
	svc services.AuditService
}

func NewAuditHandler(svc services.AuditService) *AuditHandler {
	return &AuditHandler{svc: svc}
}

type createAuditRequest struct {
	EventType  string `json:"event_type"`
	EntityType string `json:"entity_type"`
	EntityID   string `json:"entity_id"`
	Message    string `json:"message"`
}

func (h *AuditHandler) RegisterRoutes(r chi.Router) {
	r.Post("/", h.CreateAuditEvent)
	r.Get("/", h.ListAuditEvents)
	r.Get("/count", h.CountAuditEvents)
}

func (h *AuditHandler) CreateAuditEvent(w http.ResponseWriter, r *http.Request) {
	var req createAuditRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		log.Printf("CreateAuditEvent: invalid body: %v", err)
		http.Error(w, "invalid body", http.StatusBadRequest)
		return
	}

	ev, err := h.svc.CreateEvent(req.EventType, req.EntityType, req.EntityID, req.Message)
	if err != nil {
		log.Printf("CreateAuditEvent: could not create event: %v", err)
		http.Error(w, "could not create event", http.StatusInternalServerError)
		return
	}

	log.Printf("CreateAuditEvent: Audit event created!")

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(ev)
}

func (h *AuditHandler) ListAuditEvents(w http.ResponseWriter, r *http.Request) {
	evs, err := h.svc.ListEvents()
	if err != nil {
		http.Error(w, "could not list events", http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(evs)
}

func (h *AuditHandler) CountAuditEvents(w http.ResponseWriter, r *http.Request) {
	count, err := h.svc.CountEvents()
	if err != nil {
		http.Error(w, "could not count events", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]int{"count": count})
}
