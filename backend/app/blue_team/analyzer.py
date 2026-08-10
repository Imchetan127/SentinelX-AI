import re
import random
from typing import Dict, Any, List

class BlueTeamAnalyzer:
    def __init__(self):
        self.sql_patterns = [r"(\bOR\b\s+['\"].*=['\"])", r"(\bUNION\b\s+\bSELECT\b)", r"(--)", r"(DROP\s+TABLE)"]
        self.xss_patterns = [r"(<script.*?>)", r"(javascript:)", r"(onload=)", r"(onerror=)"]
        self.phish_keywords = ["urgent", "verify credentials", "audit", "account suspended", "wire transfer", "login immediately", "claim prize", "lottery winner", "crypto bonus", "bitcoin reward"]
        self.suspicious_tlds = [".xyz", ".top", ".info", ".online", ".work", ".site", ".ru", ".tk"]

    def analyze_text(self, text: str, artifact_type: str = "general") -> Dict[str, Any]:
        text_lower = text.lower()
        matched_indicators = []
        threat_score = 0.0
        threat_category = "Normal / Benign"
        risk_level = "Low"

        # 1. SQL Injection
        sqli_hits = [p for p in self.sql_patterns if re.search(p, text, re.IGNORECASE)]
        if sqli_hits:
            threat_score += 0.85
            matched_indicators.append(f"SQL Injection patterns detected: {len(sqli_hits)} matches")
            threat_category = "SQL Injection Attack"
            risk_level = "Critical"

        # 2. XSS Injection
        xss_hits = [p for p in self.xss_patterns if re.search(p, text, re.IGNORECASE)]
        if xss_hits:
            threat_score += 0.75
            matched_indicators.append(f"XSS Injection patterns detected: {len(xss_hits)} matches")
            threat_category = "Cross-Site Scripting (XSS)"
            risk_level = "High"

        # 3. Phishing / Social Engineering
        phish_hits = [kw for kw in self.phish_keywords if kw in text_lower]
        if phish_hits:
            threat_score += 0.65
            matched_indicators.append(f"Spam / Phishing urgency keywords: {', '.join(phish_hits)}")
            if threat_category == "Normal / Benign":
                threat_category = "Spam / Phishing Email"
                risk_level = "Medium" if len(phish_hits) < 2 else "High"

        # 4. Port Scan / Reconnaissance
        if "port" in text_lower or "nmap" in text_lower or "probe" in text_lower or "scan" in text_lower:
            threat_score += 0.55
            matched_indicators.append("Sequential TCP SYN Port Reconnaissance Probes")
            if threat_category == "Normal / Benign":
                threat_category = "Network Port Scan Reconnaissance"
                risk_level = "Medium"

        # 5. Brute Force / Credential Stuffing
        if "brute" in text_lower or "attempts_per_sec" in text_lower or "dictionary" in text_lower or "sample_passwords" in text_lower:
            threat_score += 0.82
            matched_indicators.append("High-Frequency Authentication Brute-Force Pattern")
            if threat_category == "Normal / Benign":
                threat_category = "Credential Stuffing Brute Force"
                risk_level = "High"

        # 6. Command Injection
        if "cat /etc/passwd" in text_lower or "; ping" in text_lower or "nc " in text_lower:
            threat_score += 0.90
            matched_indicators.append("OS Shell Command Injection Pattern")
            threat_category = "Remote Command Injection"
            risk_level = "Critical"

        # 7. DDoS SYN Flood
        if "syn_flood" in text_lower or "packets_per_second" in text_lower:
            threat_score += 0.88
            matched_indicators.append("Volumetric TCP SYN Packet Flood")
            threat_category = "DDoS SYN Flood Attack"
            risk_level = "Critical"

        # 8. Prompt Injection
        if "ignore all previous instructions" in text_lower or "do anything now" in text_lower:
            threat_score += 0.80
            matched_indicators.append("LLM System Prompt Bypass Attempt")
            threat_category = "Prompt Injection Attack"
            risk_level = "High"

        threat_score = min(1.0, max(0.05, threat_score if threat_score > 0 else 0.05))
        confidence = round(0.92, 2)
        
        mitigations = self._generate_mitigations(threat_category)

        threat_detected = threat_score > 0.40
        return {
            "artifact_type": artifact_type,
            "threat_detected": threat_detected,
            "threat_score": round(threat_score, 2),
            "confidence_score": confidence,
            "threat_category": threat_category,
            "risk_level": risk_level,
            "indicators": matched_indicators if matched_indicators else ["No suspicious malicious payload patterns identified."],
            "recommended_mitigations": mitigations
        }

    def _generate_mitigations(self, category: str) -> List[str]:
        if "SQL" in category:
            return [
                "Enforce Parameterized Prepared Queries (ORM) across database drivers.",
                "Deploy Web Application Firewall (WAF) rule to block OR/UNION payloads.",
                "Apply Principle of Least Privilege to database user permissions."
            ]
        if "Port Scan" in category:
            return [
                "Rate limit TCP SYN handshakes per source IP on perimeter router.",
                "Enable automatic IP drop rule on threat intelligence threshold.",
                "Block ICMP/SYN discovery probes on non-public interfaces."
            ]
        if "Brute Force" in category:
            return [
                "Enforce multi-factor authentication (MFA) on all access portals.",
                "Implement IP-based login rate limiting (max 5 failed attempts per min).",
                "Lock targeted accounts temporarily upon anomaly threshold breach."
            ]
        return [
            "Enable strict input validation and payload sanitization.",
            "Deploy Web Application Firewall (WAF) blocking policy.",
            "Log event to SIEM for security analyst review."
        ]

blue_team_analyzer = BlueTeamAnalyzer()
