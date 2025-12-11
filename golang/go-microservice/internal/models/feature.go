package models

import "time"

type FeatureStatus string

const (
	StatusDisabled FeatureStatus = "disabled"
	StatusEnabled  FeatureStatus = "enabled"
)

type Feature struct {
	ID          string        `json:"id"`
	Name        string        `json:"name"`
	Description string        `json:"description,omitempty"`
	Status      FeatureStatus `json:"status"`
	CreatedAt   time.Time     `json:"created_at"`
	UpdatedAt   time.Time     `json:"updated_at"`
}
