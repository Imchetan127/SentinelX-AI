# SentinelX AI — Comprehensive Architecture & Data Flow Audit Report (`AUDIT_REPORT.md`)

**Audit Date**: August 9, 2026  
**Scope**: Frontend (`frontend/src`) and Backend (`backend/app`)  
**Objective**: Audit the codebase for (1) hardcoded / fabricated values and (2) Red Team ↔ Blue Team disconnect points without modifying source code.

---

## 1. Executive Summary

SentinelX AI possesses a functional FastAPI backend, Next.js 15 frontend, SQLAlchemy models, and real ML inference engines (Scikit-Learn/XGBoost, SHAP/LIME). However, the audit reveals two key architecture gaps:
1. **Hardcoded / Fabricated Data in UI**: Several UI components ignore live backend API data and display hardcoded static metrics (`99.4%`, `98.7%`, static SHAP weights, mock SHA-256 hashes).
2. **Execution Disconnect**: Red Team simulations create `Attack` records in PostgreSQL, but **do not automatically trigger Blue Team detection, ML inference, SHAP explainability, or incident creation**. Blue Team detection currently runs only when a human manually inputs a payload into the Threat Inspector.

---

## 2. Problem 1 Audit — Hardcoded & Fabricated Values

| Finding ID | Location (File & Line) | Code Snippet / Value | Description | Classification |
| :--- | :--- | :--- | :--- | :--- |
| **VAL-01** | [`frontend/src/components/blue_team/BlueTeamView.tsx:151`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/frontend/src/components/blue_team/BlueTeamView.tsx#L151) | `analysisResult.threat_detected ? '99.4% Malicious' : '0.4% Low Risk'` | Hardcoded confidence string ignoring live multi-model probabilities returned by backend. | **(b) Fabricated value — HIGH PRIORITY TO FIX** |
| **VAL-02** | [`frontend/src/components/blue_team/BlueTeamView.tsx:161`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/frontend/src/components/blue_team/BlueTeamView.tsx#L161) | `analysisResult.threat_detected ? '98.7% Malicious' : '0.6% Low Risk'` | Hardcoded confidence string for second model output ignoring backend model probabilities. | **(b) Fabricated value — HIGH PRIORITY TO FIX** |
| **VAL-03** | [`backend/app/blue_team/analyzer.py:52`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/backend/app/blue_team/analyzer.py#L52) | `confidence = round(random.uniform(0.91, 0.99), 2)` | Rule-based analyzer returns pseudo-random floats (`random.uniform`) instead of ML model probabilities. | **(b) Fabricated value — HIGH PRIORITY TO FIX** |
| **VAL-04** | [`backend/app/explainable_ai/explainer.py:5-24`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/backend/app/explainable_ai/explainer.py#L5-L24) | `features = [{"feature": "Payload Keyword Entropy", "weight": 0.35}, ...]` | `GET /api/v1/ml-engine/explain` returns hardcoded dummy SHAP feature weights (`0.35, 0.25, 0.20, 0.12, 0.08`) and fixed `0.94` threat score. | **(b) Fabricated value — HIGH PRIORITY TO FIX** |
| **VAL-05** | [`backend/app/api/ml_engine.py:21`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/backend/app/api/ml_engine.py#L21) | `threat_score: float = 0.94` | Endpoint default parameter hardcodes 94% threat score without referencing detection score. | **(b) Fabricated value — HIGH PRIORITY TO FIX** |
| **VAL-06** | [`frontend/src/components/about/AboutView.tsx:9-28`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/frontend/src/components/about/AboutView.tsx#L9-L28) | `hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'` | Hardcoded mock report list and static SHA-256 string (hash of empty string) with dummy 3s download timer. | **(b) Fabricated value — HIGH PRIORITY TO FIX** |
| **VAL-07** | [`frontend/src/components/dashboard/DashboardView.tsx:130`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/frontend/src/components/dashboard/DashboardView.tsx#L130) | `trend="+14.2% from baseline"` | Static metric trend string passed as prop to KPI card. | **(b) Fabricated value — HIGH PRIORITY TO FIX** |
| **VAL-08** | [`frontend/src/components/dashboard/DashboardView.tsx:143`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/frontend/src/components/dashboard/DashboardView.tsx#L143) | `trend="99.3% efficiency"` | Static metric trend string passed as prop to KPI card. | **(b) Fabricated value — HIGH PRIORITY TO FIX** |
| **VAL-09** | [`frontend/src/components/layout/NotificationCenter.tsx:19`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/frontend/src/components/layout/NotificationCenter.tsx#L19) | `desc: '...isolated payload with 98.7% confidence.'` | Static mock notification text. | **(b) Fabricated value — HIGH PRIORITY TO FIX** |
| **VAL-10** | [`backend/app/services/dashboard_service.py:176-177`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/backend/app/services/dashboard_service.py#L176-L177) | `"false_positives_percent": 1.2, "false_negatives_percent": 0.4` | Hardcoded static metrics in dashboard response. | **(b) Fabricated value — HIGH PRIORITY TO FIX** |
| **VAL-11** | [`backend/app/services/analysis_service.py:218`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/backend/app/services/analysis_service.py#L218) | `accuracy=0.98` | Hardcoded default accuracy when seeding fallback model row in database. | **(a) Legitimate fallback seed default** |
| **VAL-12** | [`frontend/src/components/landing/LandingPage.tsx:1132,1537`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/frontend/src/components/landing/LandingPage.tsx#L1132) | `'98.4% AI Accuracy'`, `'15+ Attack Simulations'` | Marketing statistics rendered on public landing page. | **(c) Ambiguous — Marketing display vs computed metric** |

---

## 3. Problem 2 Audit — Red Team / Blue Team Disconnect Points

### Attack Simulation Execution Path Walkthrough
1. **Triggering Simulation**: User selects an attack vector in [`RedTeamView.tsx:41`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/frontend/src/components/red_team/RedTeamView.tsx#L41) and clicks "Simulate Attack Vector".
2. **Frontend Call**: `RedTeamView.tsx` executes `authFetch('/red-team/simulate/${vector_id}', { method: 'POST' })`.
3. **Backend Persistence**: Endpoint [`POST /api/v1/red-team/simulate/{vector_id}`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/backend/app/api/red_team.py#L21) receives request, generates vector payload, calls `AttackService.create_attack()`, creates an `Attack` record in PostgreSQL with a unique `id` (UUID), and logs `LAUNCH_ATTACK` to `audit_logs`.
4. **Execution Stop Point**: Endpoint returns simulation result JSON directly to the frontend caller. **It does NOT invoke `AnalysisService`, does NOT run ML inference, does NOT calculate SHAP explainability, and does NOT evaluate incident creation criteria.**
5. **Blue Team Isolation**: Blue Team (`BlueTeamView.tsx`) operates in complete isolation. It only runs analysis when a human manually pastes text into a textarea and clicks "Inspect & Classify Threat".

---

### Disconnect Point Classification Matrix

| Architecture Link | Status | Exact Code Finding / Line Reference |
| :--- | :--- | :--- |
| **1. Frontend RedTeamView Call** | **CONNECTED** | [`RedTeamView.tsx:51`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/frontend/src/components/red_team/RedTeamView.tsx#L51) calls `POST /api/v1/red-team/simulate/{vector_id}`. |
| **2. Backend Attack Persistence** | **CONNECTED** | [`red_team.py:31`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/backend/app/api/red_team.py#L31) creates and commits `Attack` record in DB table `attacks`. |
| **3. Automated Detection & ML Inference** | **NOT CONNECTED** | [`red_team.py:21-53`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/backend/app/api/red_team.py#L21-L53) returns JSON to frontend without triggering `AnalysisService` or model inference. |
| **4. Foreign Key Linkage** | **PARTIALLY WIRED** | SQLAlchemy models define foreign keys (`Attack.id` -> `Detection.attack_id` -> `Prediction.detection_id` -> `Explanation.prediction_id` and `Attack.id` -> `Incident.attack_id`), but they are only populated during manual Blue Team inspection calls ([`analysis_service.py:158-260`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/backend/app/services/analysis_service.py#L158-L260)). |
| **5. Incident Auto-Creation** | **PARTIALLY WIRED** | Incident auto-creation logic exists inside [`analysis_service.py:247`](file:///Users/chetanbk/Desktop/Red%20team%20vs%20Blue%20team/backend/app/services/analysis_service.py#L247) for High/Critical threats, but is never invoked by Red Team attack simulations. |
| **6. Audit & Timeline Logging** | **PARTIALLY WIRED** | `AuditLog` table stores isolated actions (`LAUNCH_ATTACK`, `ANALYZE_THREAT`), but there is no append-only `TimelineEvent` table tracking the ordered stages of an attack chain. |
| **7. Real-Time Streaming (WebSocket/SSE)** | **NOT CONNECTED** | Zero WebSocket or SSE handlers exist in frontend or backend (`0` matches for `WebSocket`, `EventSource`, `@app.websocket`). |

---

## 4. Next Steps & Target Architectural State

To unify Red Team and Blue Team into a single connected event-driven SOC platform:
1. **Unify Red Team API Endpoint**: Update `POST /api/v1/red-team/simulate/{vector_id}` to execute an end-to-end event pipeline service:
   `Attack Creation` ➔ `Feature Extraction & Multi-Model Inference` ➔ `Consensus Risk Scoring` ➔ `SHAP Feature Attribution` ➔ `WAF Mitigation Rule Application` ➔ `Incident Auto-Creation (if threshold crossed)` ➔ `Timeline Event Stream Logging`.
2. **Replace Hardcoded UI Telemetry**: Update `BlueTeamView.tsx`, `ExplainabilityView.tsx`, and `AboutView.tsx` to bind directly to backend prediction, SHAP explanation, and report generation APIs.
3. **Cross-View Deep Linking**: Direct navigation from Red Team simulation to Blue Team Defense Center scoped to `?attack_id=<UUID>`.
