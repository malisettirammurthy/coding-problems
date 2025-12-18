# -----------------------------
# Global config
# -----------------------------
DATE_TAG := $(shell date +%Y%m%d-%H%M)

FEATURE_IMAGE := rammurthymalisetti/feature-service
AUDIT_IMAGE   := rammurthymalisetti/audit-service

FEATURE_DIR := services/feature-service
AUDIT_DIR   := services/audit-service

# -----------------------------
# Default target
# -----------------------------
.PHONY: build
build: build-feature build-audit

# -----------------------------
# Build targets
# -----------------------------
.PHONY: build-feature
build-feature:
	@echo "Building feature-service image with tag $(DATE_TAG)"
	docker build \
		-t $(FEATURE_IMAGE):$(DATE_TAG) \
		$(FEATURE_DIR)

.PHONY: build-audit
build-audit:
	@echo "Building audit-service image with tag $(DATE_TAG)"
	docker build \
		-t $(AUDIT_IMAGE):$(DATE_TAG) \
		$(AUDIT_DIR)

# -----------------------------
# Push targets (optional)
# -----------------------------
.PHONY: push-feature
push-feature:
	@echo "Pushing feature-service image $(DATE_TAG)"
	docker push $(FEATURE_IMAGE):$(DATE_TAG)

.PHONY: push-audit
push-audit:
	@echo "Pushing audit-service image $(DATE_TAG)"
	docker push $(AUDIT_IMAGE):$(DATE_TAG)

.PHONY: push-all
push-all: push-feature push-audit

# -----------------------------
# Build + Push convenience
# -----------------------------
release: build push-all


# -----------------------------
# Helm config
# -----------------------------
K8S_NAMESPACE := feature-service

AUDIT_CHART_DIR   := ./charts/audit-service
FEATURE_CHART_DIR := ./charts/feature-service


# Helm confdig - update docker image tags
AUDIT_VALUES_FILE   := ./charts/audit-service/values.yaml
FEATURE_VALUES_FILE := ./charts/feature-service/values.yaml


.PHONY: helm-update-tag
helm-update-tag:
	@echo "Updating Helm image tags to $(DATE_TAG)"
	@sed -i 's/^  tag: .*/  tag: "$(DATE_TAG)"/' $(AUDIT_VALUES_FILE)
	@sed -i 's/^  tag: .*/  tag: "$(DATE_TAG)"/' $(FEATURE_VALUES_FILE)


# -----------------------------
# Helm upgrade targets
# -----------------------------
.PHONY: helm-upgrade-audit
helm-upgrade-audit:
	@echo "Upgrading audit-service Helm release"
	microk8s helm upgrade audit-service $(AUDIT_CHART_DIR) \
		--namespace $(K8S_NAMESPACE)

.PHONY: helm-upgrade-feature
helm-upgrade-feature:
	@echo "Upgrading feature-service Helm release"
	microk8s helm upgrade feature-service $(FEATURE_CHART_DIR) \
		--namespace $(K8S_NAMESPACE)

.PHONY: helm-upgrade-all
helm-upgrade-all:  helm-upgrade-audit helm-upgrade-feature


.PHONY: all
all: release helm-update-tag helm-upgrade-all



