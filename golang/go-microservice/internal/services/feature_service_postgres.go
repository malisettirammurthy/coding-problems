package services

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/ram/microservice/internal/models"
)

type PostgresFeatureService struct {
	db *pgxpool.Pool
}

func NewPostgresFeatureService(db *pgxpool.Pool) *PostgresFeatureService {
	return &PostgresFeatureService{db: db}
}

func (s *PostgresFeatureService) CreateFeature(name, description string) (*models.Feature, error) {
	now := time.Now().UTC()

	f := &models.Feature{
		ID:          uuid.NewString(),
		Name:        name,
		Description: description,
		Status:      models.StatusDisabled,
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	_, err := s.db.Exec(
		context.Background(),
		`INSERT INTO features (id, name, description, status, created_at, updated_at)
		 VALUES ($1, $2, $3, $4, $5, $6)`,
		f.ID, f.Name, f.Description, string(f.Status), f.CreatedAt, f.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}

	return f, nil
}

func (s *PostgresFeatureService) CreateBatchFeatures(batchFeatures map[string]string) ([]*models.Feature, error) {
	if len(batchFeatures) == 0 {
		// no-op, but not an error
		return []*models.Feature{}, nil
	}

	ctx := context.Background()

	tx, err := s.db.BeginTx(ctx, pgx.TxOptions{})
	if err != nil {
		return nil, err
	}

	now := time.Now().UTC()
	features := make([]*models.Feature, 0, len(batchFeatures))

	for name, desc := range batchFeatures {
		f := &models.Feature{
			ID:          uuid.NewString(),
			Name:        name,
			Description: desc,
			Status:      models.StatusDisabled,
			CreatedAt:   now,
			UpdatedAt:   now,
		}

		_, err = tx.Exec(
			ctx,
			`INSERT INTO features (id, name, description, status, created_at, updated_at)
             VALUES ($1, $2, $3, $4, $5, $6)`,
			f.ID, f.Name, f.Description, string(f.Status), f.CreatedAt, f.UpdatedAt,
		)
		if err != nil {
			_ = tx.Rollback(ctx)
			return nil, err
		}

		features = append(features, f)
	}

	if err := tx.Commit(ctx); err != nil {
		return nil, err
	}

	return features, nil
}

func (s *PostgresFeatureService) GetFeature(id string) (*models.Feature, error) {
	row := s.db.QueryRow(
		context.Background(),
		`SELECT id, name, description, status, created_at, updated_at
		 FROM features WHERE id = $1`,
		id,
	)

	var f models.Feature
	var status string

	err := row.Scan(
		&f.ID,
		&f.Name,
		&f.Description,
		&status,
		&f.CreatedAt,
		&f.UpdatedAt,
	)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, ErrFeatureNotFound
		}
		return nil, err
	}

	f.Status = models.FeatureStatus(status)
	return &f, nil
}

func (s *PostgresFeatureService) ListFeatures() ([]*models.Feature, error) {
	rows, err := s.db.Query(
		context.Background(),
		`SELECT id, name, description, status, created_at, updated_at
		 FROM features
		 ORDER BY created_at ASC`,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var out []*models.Feature

	for rows.Next() {
		var f models.Feature
		var status string

		if err := rows.Scan(
			&f.ID,
			&f.Name,
			&f.Description,
			&status,
			&f.CreatedAt,
			&f.UpdatedAt,
		); err != nil {
			return nil, err
		}

		f.Status = models.FeatureStatus(status)
		out = append(out, &f)
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return out, nil
}
