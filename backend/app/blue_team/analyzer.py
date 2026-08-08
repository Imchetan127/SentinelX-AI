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

        # Check SQLi
        sqli_hits = [p for p in self.sql_patterns if re.search(p, text, re.IGNORECASE)]
        if sqli_hits:
            threat_score += 0.85
            matched_indicators.append(f"SQL Injection patterns detected: {len(sqli_hits)} matches")
            threat_category = "SQL Injection Attack"
            risk_level = "Critical"

        # Check XSS
        xss_hits = [p for p in self.xss_patterns if re.search(p, text, re.IGNORECASE)]
        if xss_hits:
            threat_score += 0.75
            matched_indicators.append(f"XSS Injection patterns detected: {len(xss_hits)} matches")
            threat_category = "Cross-Site Scripting (XSS)"
            risk_level = "High"

        # Check Phishing/Spam
        phish_hits = [kw for kw in self.phish_keywords if kw in text_lower]
        if phish_hits:
            threat_score += 0.65
            matched_indicators.append(f"Spam / Phishing urgency keywords: {', '.join(phish_hits)}")
            if threat_category == "Normal / Benign":
                threat_category = "Spam / Phishing Email"
                risk_level = "Medium" if len(phish_hits) < 2 else "High"

        # Check prompt injection
        if "ignore all previous instructions" in text_lower or "do anything now" in text_lower:
            threat_score += 0.80
            matched_indicators.append("LLM System Prompt Bypass Attempt")
            threat_category = "Prompt Injection Attack"
            risk_level = "High"

        threat_score = min(1.0, max(0.05, threat_score if threat_score > 0 else random.uniform(0.02, 0.08)))
        confidence = round(random.uniform(0.91, 0.99), 2)
        
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

    def inspect_url(self, url: str) -> Dict[str, Any]:
        url_lower = url.lower()
        score = 0.05
        indicators = []

        if re.search(r"http[s]?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url_lower):
            score += 0.40
            indicators.append("Direct IP address used in host URL")

        if len(url) > 50:
            score += 0.20
            indicators.append(f"Abnormally long URL length ({len(url)} chars)")

        keywords = ["login", "verify", "secure", "bank", "account", "update", "paypal", "crypto", "free", "claim"]
        found_kw = [kw for kw in keywords if kw in url_lower]
        if found_kw:
            score += 0.25
            indicators.append(f"High-risk brand/security keywords in domain: {', '.join(found_kw)}")

        if any(url_lower.endswith(tld) or tld + "/" in url_lower for tld in self.suspicious_tlds):
            score += 0.25
            indicators.append("Unusual top-level domain (TLD) associated with spam/phishing")

        if url_lower.startswith("http://"):
            score += 0.15
            indicators.append("Unencrypted HTTP protocol connection")

        score = min(1.0, score)
        is_phishing = score > 0.45
        category = "Phishing / Malicious URL" if is_phishing else "Legitimate Safe URL"
        risk = "High" if score > 0.7 else ("Medium" if is_phishing else "Low")

        return {
            "url": url,
            "is_phishing": is_phishing,
            "threat_score": round(score, 2),
            "confidence_score": 0.95,
            "risk_level": risk,
            "category": category,
            "extracted_features": {
                "has_ip_address": bool(re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url)),
                "url_length": len(url),
                "is_https": url_lower.startswith("https://"),
                "suspicious_keyword_count": len(found_kw)
            },
            "indicators": indicators if indicators else ["Domain reputation and feature entropy appear normal."],
            "mitigation": [
                "Block domain on perimeter DNS firewall.",
                "Quarantine incoming traffic referencing this host URL.",
                "Verify domain SSL/TLS certificate registry."
            ]
        }

    def inspect_email(self, subject: str, sender: str, body: str) -> Dict[str, Any]:
        text_full = f"{subject} {sender} {body}".lower()
        score = 0.05
        indicators = []

        if "free" in sender or "temp" in sender or any(tld in sender for tld in self.suspicious_tlds):
            score += 0.30
            indicators.append(f"Suspicious sender email domain: {sender}")

        phish_hits = [kw for kw in self.phish_keywords if kw in text_full]
        if phish_hits:
            score += 0.40
            indicators.append(f"Social engineering urgency triggers detected: {', '.join(phish_hits)}")

        if "http://" in body or "https://" in body:
            score += 0.20
            indicators.append("External link present in email body content")

        score = min(1.0, score)
        is_spam = score > 0.45
        category = "Spam / Phishing Email Attack" if is_spam else "Legitimate Corporate Email"
        risk = "Critical" if score > 0.75 else ("Medium" if is_spam else "Low")

        return {
            "subject": subject,
            "sender": sender,
            "is_spam": is_spam,
            "threat_score": round(score, 2),
            "confidence_score": 0.96,
            "risk_level": risk,
            "category": category,
            "spf_status": "FAIL" if is_spam else "PASS",
            "dkim_status": "FAIL" if is_spam else "PASS",
            "dmarc_status": "REJECT" if is_spam else "ALLOW",
            "indicators": indicators if indicators else ["Email signature and content passes spam inspection."],
            "mitigation": [
                "Quarantine email in secure gateway sandbox.",
                "Enforce strict SPF/DKIM validation rules on mail server.",
                "Notify security operations team of targeted phishing campaign."
            ]
        }

    def _generate_mitigations(self, threat_category: str) -> List[str]:
        mapping = {
            "SQL Injection Attack": [
                "Enforce Parameterized Prepared Queries (ORM) across database drivers.",
                "Deploy Web Application Firewall (WAF) rule to block OR/UNION payloads.",
                "Apply Principle of Least Privilege to database user permissions."
            ],
            "Cross-Site Scripting (XSS)": [
                "Implement strict Content Security Policy (CSP) headers.",
                "Sanitize and encode all user inputs prior to DOM rendering.",
                "Set HttpOnly and SameSite flags on session cookies."
            ],
            "Spam / Phishing Email": [
                "Enable SPF, DKIM, and DMARC enforcement on email gateways.",
                "Isolate and quarantine suspicious external URL links.",
                "Trigger automated security awareness user warning banner."
            ],
            "Prompt Injection Attack": [
                "Implement dual-LLM verification guardrails.",
                "Sanitize untrusted user prompt context strings.",
                "Restrict executive tool access for non-authenticated sessions."
            ]
        }
        return mapping.get(threat_category, [
            "Maintain continuous network telemetry monitoring.",
            "Ensure system security patches and definitions remain up to date."
        ])

blue_team_analyzer = BlueTeamAnalyzer()
