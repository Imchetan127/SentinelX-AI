# SentinelX AI — Architecture Blueprint & Technical Specification

## 1. Event Correlation & Root Attack ID Scheme
Every event in SentinelX AI originates from a single root **Attack ID** (UUID format, e.g. `13a75057-dcba-4aca-a159-75ecbc2bfdbd`).
This root ID serves as the mandatory primary/foreign key joining all downstream records across the entire event lifecycle:

```
[Attack (id)] 
  ├── [Detection (attack_id)] 
  │     ├── [Prediction (detection_id)] 
  │     └── [Mitigation (detection_id, attack_id)]
  ├── [Explanation (prediction_id via Detection)]
  ├── [Incident (attack_id)] 
  │     └── [Report (incident_id)]
  └── [TimelineEvent (attack_id)]  (Append-Only Stream)
```

---

## 2. Multi-Model Consensus Formula
The multi-model consensus threat score (0.0 to 100.0) combines rule-based heuristic threat detection with ML model classification probabilities:

$$\text{Consensus Threat Score} = \min\left(100.0, \max\left(0.0, (\text{Rule Threat Score} \times 60.0) + (\text{ML Confidence Score} \times 40.0)\right)\right)$$

### Risk Threshold Mapping
- **CRITICAL** (80.0 – 100.0): Automated WAF Rule Block + High Priority Incident Auto-Creation.
- **HIGH** (40.0 – 79.9): Automated WAF Rule Block + Incident Auto-Creation.
- **MEDIUM** (20.0 – 39.9): Passthrough Logged for Anomaly Monitoring.
- **LOW / CLEAN** (0.0 – 19.9): Standard Telemetry Baseline Logged.

---

## 3. Real-Time Status & Polling Architecture
Because WebSocket infrastructure was not previously present, real-time pipeline progress is provided via a lightweight, low-overhead REST polling endpoint:

- **Endpoint**: `GET /api/v1/attacks/{attack_id}/status`
- **Response**:
```json
{
  "success": true,
  "attack_id": "13a75057-dcba-4aca-a159-75ecbc2bfdbd",
  "attack_type": "Spear Phishing Email - Executive Impersonation",
  "severity": "HIGH",
  "status": "COMPLETED",
  "detection_status": "completed",
  "detection_id": "782ea5fd-ea4f-4aec-a379-5c1146c9c901",
  "mitigation_status": "ACTIVE",
  "action_taken": "WAF_RULE_BLOCK",
  "incident_created": true,
  "incident_id": "ba420e44-4b68-4ad0-905a-5d743f846a64",
  "timeline_count": 5,
  "latest_stage": "INCIDENT"
}
```

---

## 4. End-to-End Pipeline Execution Flow

1. **Red Team Simulation Launch**: `POST /api/v1/red-team/simulate/{vector_id}` generates payload, creates `Attack` row, and invokes `EventPipelineService.process_attack(attack_id)`.
2. **Detection & Feature Extraction**: `blue_team_analyzer` extracts telemetry features and stores `Detection` row.
3. **Multi-Model Inference**: Models (XGBoost, Random Forest, Isolation Forest) execute predictions. Stores `Prediction` rows with real confidence/probability values. If a model is unavailable, records explicit status `"unavailable"`.
4. **SHAP/LIME Explainability**: `explainable_ai_engine` computes SHAP feature attributions and stores `Explanation` row.
5. **WAF Mitigation Rules**: Evaluates score against `THREAT_BLOCK_THRESHOLD = 0.40`. Applies `WAF_RULE_BLOCK` and stores `Mitigation` row.
6. **Incident Auto-Creation**: If threshold crossed, creates `Incident` row (`status="OPEN"`).
7. **Append-Only Timeline Stream**: Writes 5 distinct `TimelineEvent` records for `RED_TEAM`, `AI_ENGINE`, `XAI_ENGINE`, `BLUE_TEAM`, and `INCIDENT`.
