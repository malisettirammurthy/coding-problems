package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/ram/microservice/internal/services"
)

type FeatureHandler struct {
	svc services.FeatureService
}

func NewFeatureService(svc services.FeatureService) *FeatureHandler {
	return &FeatureHandler{svc: svc}
}

func (h *FeatureHandler) RegisterRoutes(r chi.Router) {
	r.Post("/", h.CreateFeature)
	r.Get("/", h.ListFeatures)
	r.Get("/{id}", h.GetFeature)
}

type createFeatureRequest struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func (h *FeatureHandler) CreateFeature(w http.ResponseWriter, r *http.Request) {
	var req createFeatureRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "invalid request body", http.StatusBadRequest)
		return
	}
	if req.Name == "" {
		http.Error(w, "name is required", http.StatusBadRequest)
		return
	}
	feature, err := h.svc.CreateFeature(req.Name, req.Description)
	if err != nil {
		http.Error(w, "could not create feature", http.StatusInternalServerError)
		return
	}
	writeJSON(w, http.StatusOK, feature)
}

func (h *FeatureHandler) GetFeature(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if id == "" {
		http.Error(w, "id is requried", http.StatusBadRequest)
		return
	}
	feature, err := h.svc.GetFeature(id)
	if err != nil {
		if err == services.ErrFeatureNotFound {
			http.Error(w, "feature not found", http.StatusNotFound)
			return
		}
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}
	writeJSON(w, http.StatusOK, feature)
}

func (h *FeatureHandler) ListFeatures(w http.ResponseWriter, r *http.Request) {
	features, err := h.svc.ListFeatures()
	if err != nil {
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}
	writeJSON(w, http.StatusOK, features)
}
