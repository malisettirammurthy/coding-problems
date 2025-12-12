package services

import (
	"errors"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/ram/microservice/internal/models"
)

var (
	ErrFeatureNotFound = errors.New("feature not found")
)

type FeatureService interface {
	CreateFeature(name, description string) (*models.Feature, error)
	CreateBatchFeatures(map[string]string) ([]*models.Feature, error)
	GetFeature(id string) (*models.Feature, error)
	ListFeatures() ([]*models.Feature, error)
}

type InMemoryFeatureService struct {
	mu    sync.RWMutex
	store map[string]*models.Feature
}

func NewInMemoryFeatureService() *InMemoryFeatureService {
	return &InMemoryFeatureService{
		store: make(map[string]*models.Feature),
	}
}

func (s *InMemoryFeatureService) CreateFeature(name, description string) (*models.Feature, error) {
	now := time.Now().UTC()
	f := &models.Feature{
		ID:          uuid.NewString(),
		Name:        name,
		Description: description,
		Status:      models.StatusDisabled,
		CreatedAt:   now,
		UpdatedAt:   now,
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	s.store[f.ID] = f
	return f, nil
}

func (s *InMemoryFeatureService) CreateBatchFeatures(batch map[string]string) ([]*models.Feature, error) {
	now := time.Now().UTC()
	s.mu.Lock()
	defer s.mu.Unlock()
	out := make([]*models.Feature, 0, len(batch))

	for name, descr := range batch {
		f := &models.Feature{
			ID:          uuid.NewString(),
			Name:        name,
			Description: descr,
			Status:      models.StatusDisabled,
			CreatedAt:   now,
			UpdatedAt:   now,
		}
		s.store[f.ID] = f
		out = append(out, f)
	}
	return out, nil
}

func (s *InMemoryFeatureService) GetFeature(id string) (*models.Feature, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	f, ok := s.store[id]
	if !ok {
		return nil, ErrFeatureNotFound
	}
	return f, nil
}

func (s *InMemoryFeatureService) ListFeatures() ([]*models.Feature, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]*models.Feature, 0, len(s.store))
	for _, f := range s.store {
		out = append(out, f)
	}
	return out, nil
}
