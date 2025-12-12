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

func (s *InMemoryFeatureService) CreateBatchFeatures(batchFeatures map[string]string) ([]*models.Feature, error) {
	features := make([]*models.Feature, 0, len(batchFeatures))

	for name, desc := range batchFeatures {
		f, err := s.CreateFeature(name, desc)
		if err != nil {
			return nil, err
		}
		features = append(features, f)
	}

	return features, nil
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
