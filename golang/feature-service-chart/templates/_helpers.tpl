{{- define "feature-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "feature-service.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "feature-service.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end }}
{{- end }}

{{- define "feature-service.databaseUrl" -}}
{{ printf "postgres://%s:%s@%s-postgres:%d/%s?sslmode=disable" .Values.postgres.username .Values.postgres.password (include "feature-service.fullname" .) .Values.postgres.port .Values.postgres.database }}
{{- end }}

