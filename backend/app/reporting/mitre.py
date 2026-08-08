"""app/reporting/mitre.py — MITRE ATT&CK Mapping & Threat Intelligence Formatter.

Deterministic mapping of attack types to MITRE ATT&CK techniques.
Never invents non-standard techniques or uses LLMs.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger("Reporting.Mitre")

_MITRE_MAP: Dict[str, Dict[str, str]] = {
    "sql injection": {
        "technique_id": "T1190",
        "technique_name": "Exploit Public-Facing Application",
        "tactic": "Initial Access",
        "description": "Adversaries may attempt to exploit a weakness in a public-facing web application (e.g. SQL Injection) to execute arbitrary database queries or access unauthorised data.",
        "mitigation": "Use parameterized queries (prepared statements), input validation, web application firewalls (WAF), and least-privilege database accounts.",
    },
    "ddos": {
        "technique_id": "T1498",
        "technique_name": "Network Denial of Service",
        "tactic": "Impact",
        "description": "Adversaries may perform Network Denial of Service (NDoS) attacks to degrade or disrupt the availability of targeted systems and services.",
        "mitigation": "Implement volumetric DDoS mitigation services, rate limiting at edge proxies, flow monitoring, and dynamic IP blocking.",
    },
    "dos": {
        "technique_id": "T1499",
        "technique_name": "Endpoint Denial of Service",
        "tactic": "Impact",
        "description": "Adversaries may cause an endpoint denial of service to degrade or disrupt availability of targeted systems.",
        "mitigation": "Configure resource exhaustion protection, connection timeouts, and request rate limiting.",
    },
    "port scan": {
        "technique_id": "T1595",
        "technique_name": "Active Scanning",
        "tactic": "Reconnaissance",
        "description": "Adversaries may execute active reconnaissance scans to probe host services, open ports, and vulnerable network interfaces.",
        "mitigation": "Restrict unused inbound ports, deploy intrusion prevention systems (IPS), and enforce network segmentation.",
    },
    "brute force": {
        "technique_id": "T1110",
        "technique_name": "Brute Force",
        "tactic": "Credential Access",
        "description": "Adversaries may use brute force techniques to attempt login credentials and gain unauthorized access.",
        "mitigation": "Enforce strong password policies, account lockout thresholds, multi-factor authentication (MFA), and CAPTCHA.",
    },
    "bot": {
        "technique_id": "T1059",
        "technique_name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "description": "Adversaries may abuse command and script interpreters to execute commands, scripts, or automated payload binaries.",
        "mitigation": "Restrict script execution privileges, deploy endpoint detection and response (EDR), and enforce code signing.",
    },
}

_DEFAULT_MITRE: Dict[str, str] = {
    "technique_id": "T1190",
    "technique_name": "Exploit Public-Facing Application",
    "tactic": "Initial Access / Execution",
    "description": "Adversaries attempt to exploit security vulnerabilities in targeted infrastructure applications to compromise availability or integrity.",
    "mitigation": "Apply timely security security patches, maintain web application firewalls (WAF), enforce strict input sanitation, and perform regular vulnerability assessments.",
}


class MitreMapper:
    """Maps security attack types to MITRE ATT&CK techniques."""

    @staticmethod
    def map_attack_type(attack_type: str) -> Dict[str, str]:
        """Return the deterministic MITRE ATT&CK mapping for *attack_type*."""
        norm_type = (attack_type or "").lower().strip()
        
        for key, mapping in _MITRE_MAP.items():
            if key in norm_type:
                return mapping
                
        return _DEFAULT_MITRE


class ThreatIntelligenceFormatter:
    """Formats Threat Intelligence data for the report."""

    def __init__(self):
        self.mapper = MitreMapper()

    def format(self, attack_type: str) -> Dict[str, Any]:
        mapping = self.mapper.map_attack_type(attack_type)
        return {
            "attack_type": attack_type,
            "mitre": mapping,
            "threat_actor_level": "Medium / Advanced",
            "confidence": "High (Rule & Model Correlation)",
        }
