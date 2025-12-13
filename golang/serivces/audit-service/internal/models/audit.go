package models

import "time"

type AuditEvent struct {
	ID         string    `json:"id"`
	EventType  string    `json:"event_type"`
	EntityID   string    `json:"entity_id"`
	EntityType string    `json:"entity_type"`
	Message    string    `json:"message"`
	CreatedAt  time.Time `json:"created_at"`
}
