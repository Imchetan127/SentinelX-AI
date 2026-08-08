# SentinelX AI — Release Changelog

All notable changes to the **SentinelX AI** platform are documented in this file. Versioning adheres to [Semantic Versioning (SemVer)](https://semver.org/).

---

## [v0.8.0] - 2026-08-08 (Milestone 6, Sprint 6.1)
### Added
- Complete containerization infrastructure (`Dockerfile` for Backend & Frontend).
- Multi-stage Next.js frontend build with `output: 'standalone'`.
- Production `python:3.11-slim` backend Dockerfile with non-root security (`appuser` UID 10001).
- Healthcheck-based container dependency orchestration in `docker-compose.yml` (`postgres` → `backend` → `frontend`).
- Automated Alembic database migration startup in `backend/entrypoint.sh`.
- Five named local Docker volumes (`postgres-data`, `models`, `datasets`, `reports`, `logs`).
- Centralized `.env` environment variable management.
- Optional Adminer DB web interface under `dev` compose profile.

---

## [v0.7.0] - 2026-08-08 (Milestone 5, Sprint 5.1)
### Added
- Enterprise Incident Reporting Engine (`ReportService`).
- 11-section ReportLab PDF renderer with dynamic `NumberedCanvas` page numbering (`Page X of Y`).
- Chronological timeline builder from immutable audit logs.
- Deterministic MITRE ATT&CK technique mapper (`T1190`, `T1498`, `T1595`, `T1110`, `T1059`).
- Deterministic remediation recommendation engine (non-LLM).
- Cryptographic SHA256 PDF integrity verification (`VALID` vs `TAMPERED`).
- API endpoints: `/api/v1/reports/generate/{incident_id}`, `/api/v1/reports/{report_id}/download`, `/api/v1/reports/{report_id}/verify`.
- RBAC protection restricting report generation to Admin and Security Analyst roles.

---

## [v0.6.0] - 2026-08-08 (Milestone 4, Sprint 4.1)
### Added
- Explainable AI (XAI) framework integrating `shap.TreeExplainer`.
- Output shape normalizer (`_extract_row_shap`) supporting Random Forest and XGBoost arrays.
- Structural explanation validator enforcing 5 integrity rules.
- Append-only `explanations` database persistence.
- REST API endpoint `/api/v1/explain/{prediction_id}`.

---

## [v0.5.0] - 2026-08-08 (Milestone 3, Sprint 3.5)
### Added
- AI Validation & Quality Gate framework (`ValidationService`).
- 5-fold Stratified K-Fold cross-validation (`CrossValidator`).
- Metric Analyzer (`MetricsAnalyzer`) and Quality Gate Threshold Evaluator (`ThresholdEvaluator`).
- Benchmarking report generation.

---

## [v0.4.0] - 2026-08-08 (Milestone 3, Sprint 3.4)
### Added
- Model Governance Service (`ModelGovernanceService`).
- 6-state lifecycle state machine (`TRAINING`, `VALIDATED`, `STAGING`, `PRODUCTION`, `ARCHIVED`, `FAILED`).
- Single production active model policy invariant.
- Automated Model Card generation (`ModelCardGenerator`).
- Transactional promotion and rollback flows with database-first commits.
- Application startup diagnostic validation checks.

---

## [v0.3.0] - 2026-08-08 (Milestone 3, Sprint 3.1 - 3.3)
### Added
- Machine learning inference engine (`InferenceService`) with class-level memory caching.
- Dataset preprocessing pipeline (`DatasetPipeline`).
- Model training pipeline (`TrainingService`) supporting Random Forest and XGBoost.

---

## [v0.2.0] - 2026-08-08 (Milestone 2)
### Added
- Red Team attack simulation engine and payload execution handlers.
- Blue Team SOC incident management and alert triage.
- Audit logging service (`AuditService`).

---

## [v0.1.0] - 2026-08-08 (Milestone 1)
### Added
- Platform database models (`User`, `Dataset`, `Model`, `Attack`, `Detection`, `Prediction`, `Incident`, `Report`, `AuditLog`).
- JWT authentication system, password hashing (bcrypt), and API router foundations.
