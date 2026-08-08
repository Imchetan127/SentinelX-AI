"""app/reporting/formatters.py — AI Metrics, SHAP, and Recommendation Engine formatters.

All recommendation mappings are strictly deterministic.
Never uses LLMs or natural language generation.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("Reporting.Formatters")


class AIAnalysisFormatter:
    """Formats model metadata, validation metrics, and quality gate results."""

    def format(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        prediction_data = evidence.get("prediction", {})
        model_data = evidence.get("model", {})

        return {
            "algorithm": model_data.get("algorithm", "N/A"),
            "model_version": model_data.get("version", "N/A"),
            "dataset_version": model_data.get("dataset_name", "cicids_test_v1.0"),
            "pipeline_version": "p1.0",
            "prediction": prediction_data.get("label", "N/A"),
            "confidence": prediction_data.get("confidence", 0.0),
            "probability": prediction_data.get("probability", 0.0),
            "metrics": {
                "accuracy": model_data.get("accuracy", 0.0),
                "precision": model_data.get("precision", 0.0),
                "recall": model_data.get("recall", 0.0),
                "f1_score": model_data.get("f1_score", 0.0),
            },
            "validation_status": "VALIDATED" if model_data.get("status") in ("VALIDATED", "PRODUCTION", "ACTIVE") else "UNVALIDATED",
            "quality_gate": "PASSED" if model_data.get("f1_score", 0.0) >= 0.70 else "WARNING",
        }


class SHAPFormatter:
    """Formats SHAP base values, feature contributions, and importance tables."""

    def format(self, explanation_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not explanation_data:
            return {
                "status": "UNAVAILABLE",
                "base_value": "N/A",
                "top_positive": [],
                "top_negative": [],
                "importance_table": [],
                "warnings": ["No SHAP explanation generated for this prediction."],
            }

        return {
            "status": "AVAILABLE",
            "explanation_id": explanation_data.get("id", "N/A"),
            "base_value": explanation_data.get("base_value", 0.0),
            "top_positive": explanation_data.get("top_positive_contributors", []),
            "top_negative": explanation_data.get("top_negative_contributors", []),
            "importance_table": explanation_data.get("feature_importance", []),
            "warnings": explanation_data.get("warnings", []),
            "explained_at": explanation_data.get("explained_at", "N/A"),
        }


_DETERMINISTIC_RECOMMENDATIONS: Dict[str, List[Dict[str, str]]] = {
    "sql injection": [
        {
            "category": "Code Fix",
            "recommendation": "Implement Parameterized Queries / Prepared Statements",
            "detail": "Ensure all database queries use bound parameters to eliminate SQL payload execution.",
        },
        {
            "category": "Edge Control",
            "recommendation": "Configure Web Application Firewall (WAF) SQLi Rules",
            "detail": "Enable WAF inspection rules targeting UNION, SELECT, and quote injection patterns.",
        },
        {
            "category": "Input Validation",
            "recommendation": "Enforce Strict Type & Schema Validation",
            "detail": "Validate and sanitize all user-supplied HTTP parameters prior to application processing.",
        },
    ],
    "ddos": [
        {
            "category": "Network Control",
            "recommendation": "Enable Rate Limiting & Connection Throttling",
            "detail": "Configure ingress proxy rules to cap incoming request bursts per IP subnet.",
        },
        {
            "category": "Edge Control",
            "recommendation": "Activate Volumetric Cloud Scrubbing",
            "detail": "Reroute incoming traffic through DDoS mitigation providers to absorb high-bandwidth traffic.",
        },
        {
            "category": "Monitoring",
            "recommendation": "Monitor NetFlow / IPFIX Anomaly Alerts",
            "detail": "Set up real-time packet-rate thresholds on boundary routers.",
        },
    ],
    "port scan": [
        {
            "category": "Network Control",
            "recommendation": "Block Origin IP at Boundary Firewall",
            "detail": "Add offending source IP addresses to automated dynamic drop lists.",
        },
        {
            "category": "Hardening",
            "recommendation": "Close Unnecessary Inbound Ports",
            "detail": "Audit firewall rules and shut down unneeded public-facing listening services.",
        },
    ],
}

_DEFAULT_RECOMMENDATIONS: List[Dict[str, str]] = [
    {
        "category": "Incident Response",
        "recommendation": "Isolate Affected Infrastructure Host",
        "detail": "Quarantine the impacted host from the corporate production network pending forensic analysis.",
    },
    {
        "category": "Access Control",
        "recommendation": "Revoke Compromised Session Tokens",
        "detail": "Force-expire active user authentication sessions associated with the flagged detection.",
    },
    {
        "category": "Hardening",
        "recommendation": "Apply Emergency Vendor Security Patches",
        "detail": "Patch identified software vulnerabilities and update endpoint intrusion signatures.",
    },
]


class RecommendationEngine:
    """Generates deterministic remediation recommendations based on attack type."""

    def generate_recommendations(self, attack_type: str) -> List[Dict[str, str]]:
        """Return deterministic recommendation list matching *attack_type*."""
        norm_type = (attack_type or "").lower().strip()
        for key, recs in _DETERMINISTIC_RECOMMENDATIONS.items():
            if key in norm_type:
                return recs
        return _DEFAULT_RECOMMENDATIONS
