package clients

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type AuditClient struct {
	baseURL    string
	httpClient *http.Client
}

func NewAuditClient(baseURL string) *AuditClient {
	return &AuditClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 2 * time.Second,
		},
	}
}

type createAuditRequest struct {
	EventType  string `json:"event_type"`
	EntityType string `json:"entity_type"`
	EntityID   string `json:"entity_id"`
	Message    string `json:"message"`
}

func (c *AuditClient) FeatureCreated(featureID, featureName string) error {
	body := createAuditRequest{
		EventType:  "feature_created",
		EntityType: "feature",
		EntityID:   featureID,
		Message:    fmt.Sprintf("Feature created: %s", featureName),
	}

	data, err := json.Marshal(body)
	if err != nil {
		return err
	}

	req, err := http.NewRequest(http.MethodPost, c.baseURL+"/api/v1/audit", bytes.NewReader(data))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// you can choose to ignore non-2xx or log it
	if resp.StatusCode >= 300 {
		return fmt.Errorf("audit service returned status %d", resp.StatusCode)
	}
	return nil
}
