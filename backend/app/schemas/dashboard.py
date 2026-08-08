from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional


class TimelineEvent(BaseModel):
    time: str
    event: str
    severity: str


class RecentAttack(BaseModel):
    id: str
    attack_type: str
    target: Optional[str]
    severity: str
    status: str
    created_at: Optional[str]


class RecentIncident(BaseModel):
    id: str
    title: str
    priority: str
    status: str
    created_at: Optional[str]


class DashboardMetrics(BaseModel):
    # Frontend expected keys
    total_threats_analyzed: int
    threats_detected: int
    threats_blocked: int
    attack_success_rate_percent: float
    detection_accuracy_percent: float
    false_positives_percent: float
    false_negatives_percent: float
    system_health: str
    active_defenses: List[str]
    recent_activity_timeline: List[TimelineEvent]

    # Specification requested keys
    total_attacks: int
    attacks_today: int
    active_incidents: int
    critical_incidents: int
    predictions_performed: int
    detections_performed: int
    registered_users: int
    models_available: int
    attack_severity_distribution: Dict[str, int]
    incident_status_distribution: Dict[str, int]
    latest_attacks: List[RecentAttack]
    latest_incidents: List[RecentIncident]

    model_config = ConfigDict(from_attributes=True)
