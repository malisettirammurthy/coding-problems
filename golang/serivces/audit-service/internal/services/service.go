package services

import (
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/ram/audit-microservice/internal/models"
)

type AuditService interface {
	CreateEvent(eventType, entityType, entityID, message string) (*models.AuditEvent, error)
	ListEvents() ([]*models.AuditEvent, error)
}

type InMemoryAuditService struct {
	mu     sync.RWMutex
	events []*models.AuditEvent
}

func NewInMemoryAuditService() *InMemoryAuditService {
	return &InMemoryAuditService{
		events: make([]*models.AuditEvent, 0),
	}
}

func (s *InMemoryAuditService) CreateEvent(eventType, entityType, entityID, message string) (*models.AuditEvent, error) {
	now := time.Now().UTC()
	ev := &models.AuditEvent{
		ID:         uuid.NewString(),
		EventType:  eventType,
		EntityID:   entityID,
		EntityType: entityType,
		Message:    message,
		CreatedAt:  now,
	}

	s.mu.Lock()
	defer s.mu.Unlock()
	s.events = append(s.events, ev)
	return ev, nil
}

func (s *InMemoryAuditService) ListEvents() ([]*models.AuditEvent, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]*models.AuditEvent, len(s.events))
	copy(out, s.events)
	return out, nil
}
