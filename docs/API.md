# SentinelX AI — REST API Reference Specification

## Overview

The SentinelX AI REST API is built with **FastAPI** and served by **Uvicorn** on port `8000`. All routes are versioned under the `/api/v1` prefix. The API uses JSON payloads for requests and responses, enforcing Pydantic schema validation.

---

## Global Authentication & Headers

Protected endpoints require a JSON Web Token (JWT) passed in the `Authorization` header:

```http
Authorization: Bearer <jwt_access_token>
Content-Type: application/json
```

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### 1.1 Login & Obtain Access Token
- **Route**: `POST /api/v1/auth/login`
- **Auth**: None (Public)
- **Request Body**:
```json
{
  "username": "admin",
  "password": "SuperSecretPassword123!"
}
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
    "username": "admin",
    "email": "admin@sentinelx.ai",
    "role": "admin"
  }
}
```
- **Errors**: `401 Unauthorized` (Invalid credentials).

---

### 1.2 Get Current Authenticated User Profile
- **Route**: `GET /api/v1/auth/me`
- **Auth**: Bearer Token
- **Response `200 OK`**:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "username": "admin",
  "email": "admin@sentinelx.ai",
  "role": "admin",
  "is_active": true
}
```

---

## 2. User Management (`/api/v1/users`)

### 2.1 List All Users
- **Route**: `GET /api/v1/users/`
- **Auth**: Admin
- **Response `200 OK`**: List of user objects.

### 2.2 Create User
- **Route**: `POST /api/v1/users/`
- **Auth**: Admin
- **Request Body**:
```json
{
  "username": "analyst1",
  "email": "analyst1@sentinelx.ai",
  "password": "SecurePassword123!",
  "role": "security_analyst"
}
```

---

## 3. Attack Simulation (`/api/v1/attacks`)

### 3.1 Execute Attack Simulation
- **Route**: `POST /api/v1/attacks/`
- **Auth**: Bearer Token (Red Team / Admin)
- **Request Body**:
```json
{
  "type": "SQL Injection",
  "payload": "UNION SELECT username, password_hash FROM users--",
  "target": "database_cluster_01",
  "severity": "HIGH"
}
```
- **Response `201 Created`**:
```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-2345678901bc",
  "type": "SQL Injection",
  "target": "database_cluster_01",
  "severity": "HIGH",
  "status": "COMPLETED",
  "timestamp": "2026-08-08T15:00:00Z"
}
```

---

## 4. Incident Management (`/api/v1/incidents`)

### 4.1 Create Incident from Attack
- **Route**: `POST /api/v1/incidents/`
- **Auth**: Bearer Token (Security Analyst / Admin)
- **Request Body**:
```json
{
  "attack_id": "b2c3d4e5-f6a7-8901-bcde-2345678901bc",
  "title": "CRITICAL: SQL Injection Alert on DB Cluster",
  "priority": "HIGH",
  "description": "Automated intrusion alert raised by SentinelX AI engine."
}
```

### 4.2 List Incidents
- **Route**: `GET /api/v1/incidents/`
- **Auth**: Bearer Token
- **Query Params**: `status`, `priority`, `limit`, `offset`

---

## 5. Model Governance Endpoints (`/api/v1/governance`)

### 5.1 List Registered Governance Models
- **Route**: `GET /api/v1/governance/models`
- **Auth**: Bearer Token
- **Response `200 OK`**: List of all models in the registry database.

### 5.2 Get Active Production Model Metadata
- **Route**: `GET /api/v1/governance/models/active`
- **Auth**: Bearer Token
- **Response `200 OK`**:
```json
{
  "model_id": "c3d4e5f6-a7b8-9012-cdef-3456789012cd",
  "name": "Random Forest Intrusion Classifier",
  "algorithm": "random_forest",
  "version": "1.0.0",
  "status": "PRODUCTION",
  "accuracy": 0.965,
  "f1_score": 0.958
}
```

### 5.3 Promote Model State
- **Route**: `POST /api/v1/governance/models/{model_id}/promote`
- **Auth**: Admin
- **Request Body**:
```json
{
  "target_status": "PRODUCTION",
  "min_accuracy": 0.85,
  "min_f1": 0.80
}
```

### 5.4 Rollback Production Model
- **Route**: `POST /api/v1/governance/models/rollback`
- **Auth**: Admin
- **Request Body**: `{"target_model_id": "uuid-string"}`

---

## 6. AI Validation & Benchmarking (`/api/v1/validation`)

### 6.1 Run Model Validation Experiment
- **Route**: `POST /api/v1/validation/run`
- **Auth**: Admin / Security Analyst
- **Request Body**:
```json
{
  "model_version": "1.0.0",
  "dataset_name": "cicids_test",
  "dataset_version": "v1.0"
}
```

### 6.2 Get Quality Gate Benchmarks
- **Route**: `GET /api/v1/validation/benchmarks/{model_id}`
- **Auth**: Bearer Token

---

## 7. Explainable AI (SHAP) (`/api/v1/explain`)

### 7.1 Generate Prediction Explanation
- **Route**: `POST /api/v1/explain/{prediction_id}`
- **Auth**: Bearer Token
- **Request Body**:
```json
{
  "features": {
    "Flow Duration": 12000,
    "Total Fwd Packets": 45,
    "Fwd Packet Length Max": 1100
  }
}
```
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "explanation_id": "d4e5f6a7-b8c9-0123-def0-4567890123de",
    "prediction_id": "e5f6a7b8-c9d0-1234-ef01-5678901234ef",
    "algorithm": "random_forest",
    "base_value": 0.459524,
    "shap_values": [0.104311, 0.115176, 0.020989],
    "feature_importance": [
      {"feature": "Total Fwd Packets", "shap_value": 0.115176, "direction": "positive"},
      {"feature": "Flow Duration", "shap_value": 0.104311, "direction": "positive"}
    ],
    "top_positive_contributors": [
      {"feature": "Total Fwd Packets", "shap_value": 0.115176}
    ],
    "top_negative_contributors": []
  }
}
```

### 7.2 Get Persisted Explanation
- **Route**: `GET /api/v1/explain/{prediction_id}`

### 7.3 List Recent Explanations
- **Route**: `GET /api/v1/explain/history`

---

## 8. Incident Reporting Engine (`/api/v1/reports`)

### 8.1 Generate PDF Incident Report
- **Route**: `POST /api/v1/reports/generate/{incident_id}`
- **Auth**: Admin, Security Analyst (`403 Forbidden` for other roles)
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "id": "f6a7b8c9-d0e1-2345-f012-6789012345fg",
    "incident_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
    "title": "Incident Report: CRITICAL: SQL Injection Alert on DB Cluster",
    "pdf_path": "../reports/report_incident_a1b2c3d4_1770560000.pdf",
    "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "version": 1,
    "created_at": "2026-08-08T15:30:00Z"
  }
}
```

### 8.2 Download PDF Report
- **Route**: `GET /api/v1/reports/{report_id}/download`
- **Auth**: Bearer Token
- **Response**: Binary PDF Stream (`application/pdf`). Logs `REPORT_DOWNLOADED` audit action.

### 8.3 Verify Report Cryptographic Integrity
- **Route**: `POST /api/v1/reports/{report_id}/verify`
- **Auth**: Bearer Token
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "status": "VALID",
    "report_id": "f6a7b8c9-d0e1-2345-f012-6789012345fg",
    "stored_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "computed_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "is_valid": true
  }
}
```

---

## 9. Platform Health & Diagnostics

### 9.1 Container Healthcheck Endpoint
- **Route**: `GET /health`
- **Auth**: Public
- **Response `200 OK`**: `{"status": "healthy", "success": true, "service": "backend"}`
