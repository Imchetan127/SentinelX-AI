import re
import json
import math
from typing import Dict, Any, List, Union

FEATURE_NAMES = [
    "sqli_keyword_entropy",
    "xss_script_score",
    "phish_urgency_score",
    "cmd_injection_score",
    "path_traversal_score",
    "user_agent_anomaly",
    "payload_length",
    "special_char_ratio",
    "header_spf_dkim_fail",
    "volumetric_rate_ratio"
]

def extract_features_dict(payload_data: Union[str, Dict[str, Any]]) -> Dict[str, float]:
    """
    Unified domain-matched feature extraction function for SentinelX AI.
    Used IDENTICALLY during dataset generation, training, and live inference.
    """
    if isinstance(payload_data, dict):
        text_content = json.dumps(payload_data)
        raw_dict = payload_data
    else:
        text_content = str(payload_data)
        raw_dict = {}

    text_lower = text_content.lower()

    # 1. SQL Injection Keyword / Pattern Score
    sqli_patterns = [
        r"\bor\b\s+['\"].*=['\"]", r"\bunion\b\s+\bselect\b", r"--", r"drop\s+table", r"select\s+.*\s+from",
        r"sleep\(", r"benchmark\(", r"waitfor\s+delay", r"extractvalue", r"updatexml", r"\$gt", r"\$ne", r"\$where",
        r"exec\s+sp_", r"information_schema"
    ]
    sqli_hits = sum(1 for p in sqli_patterns if re.search(p, text_content, re.IGNORECASE))
    sqli_score = min(1.0, sqli_hits * 0.35)

    # 2. XSS Script Score
    xss_patterns = [
        r"<script.*?>", r"javascript:", r"onload=", r"onerror=", r"document\.cookie", r"fetch\(",
        r"on\w+=", r"<svg", r"srcdoc=", r"<iframe", r"eval\(", r"atob\(", r"xlink:href", r"<math"
    ]
    xss_hits = sum(1 for p in xss_patterns if re.search(p, text_content, re.IGNORECASE))
    xss_score = min(1.0, xss_hits * 0.35)

    # 3. Phishing Urgency Score
    phish_keywords = [
        "urgent", "verify credentials", "audit", "account suspended", "wire transfer", "login immediately",
        "claim prize", "lottery winner", "crypto bonus", "bitcoin reward", "action required", "helpdesk",
        "mfa fatigue", "password reset", "invoice payment", "package delivery", "unrecognized device", "security alert",
        "mandatory hr", "suspicious activity", "verify identity"
    ]
    phish_hits = sum(1 for kw in phish_keywords if kw in text_lower)
    phish_score = min(1.0, phish_hits * 0.3)

    # 4. Command Injection Score
    cmd_patterns = [
        r";\s*cat\s+", r"|\s*nc\s+", r"vssadmin\.exe", r"powershell\.exe", r"cmd\.exe", r";\s*ping",
        r"base64", r"\$\(", r"curl\s+", r"wget\s+", r"bash\s+", r"sh\s+", r"/bin/sh", r"exec\(",
        r"export\s+cmd=", r"wmic\s+", r"bcdedit"
    ]
    cmd_hits = sum(1 for p in cmd_patterns if re.search(p, text_content, re.IGNORECASE))
    cmd_score = min(1.0, cmd_hits * 0.4)

    # 5. Path Traversal Score
    path_hits = len(re.findall(r"\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|\.\.%2f|\.\.%5c", text_content, re.IGNORECASE))
    path_score = min(1.0, path_hits * 0.5)

    # 6. User Agent Anomaly Flag
    ua_scanners = ["sqlmap", "nmap", "nikto", "masscan", "python-urllib", "gobuster", "dirbuster", "ffuf", "wfuzz", "hydra", "zgrab"]
    ua_anomaly = 1.0 if any(s in text_lower for s in ua_scanners) else 0.0

    # 7. Payload Length (Normalized)
    length = len(text_content)
    length_norm = min(1.0, length / 2000.0)

    # 8. Special Character Ratio
    if length > 0:
        special_chars = sum(1 for c in text_content if not c.isalnum() and not c.isspace())
        special_ratio = min(1.0, special_chars / length)
    else:
        special_ratio = 0.0

    # 9. Header SPF/DKIM Fail Flag
    spf_dkim_fail = 0.0
    headers = raw_dict.get("headers", {}) if isinstance(raw_dict, dict) else {}
    if isinstance(headers, dict):
        if headers.get("SPF") == "FAIL" or headers.get("DKIM") == "FAIL":
            spf_dkim_fail = 1.0
    if "spf=fail" in text_lower or "dkim=fail" in text_lower:
        spf_dkim_fail = 1.0

    # 10. Volumetric Rate Ratio (DDoS / Brute Force)
    volumetric = 0.0
    if "packets_per_second" in text_lower or "attempts_per_sec" in text_lower or "file_access_rate" in text_lower:
        volumetric = 1.0

    return {
        "sqli_keyword_entropy": sqli_score,
        "xss_script_score": xss_score,
        "phish_urgency_score": phish_score,
        "cmd_injection_score": cmd_score,
        "path_traversal_score": path_score,
        "user_agent_anomaly": ua_anomaly,
        "payload_length": length_norm,
        "special_char_ratio": special_ratio,
        "header_spf_dkim_fail": spf_dkim_fail,
        "volumetric_rate_ratio": volumetric
    }

def extract_features_vector(payload_data: Union[str, Dict[str, Any]]) -> List[float]:
    feat_dict = extract_features_dict(payload_data)
    return [feat_dict[name] for name in FEATURE_NAMES]
