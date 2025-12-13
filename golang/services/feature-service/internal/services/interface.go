package services

import "github.com/ram/microservice/internal/models"

type FeatureService interface {
	CreateFeature(name, description string) (*models.Feature, error)
	CreateBatchFeatures(batchFeatures map[string]string) ([]*models.Feature, error)
	GetFeature(id string) (*models.Feature, error)
	ListFeatures() ([]*models.Feature, error)
	CountFeatures() (int, error)
}
