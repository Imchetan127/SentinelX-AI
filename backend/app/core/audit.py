import logging
from typing import Optional

# Setup standard logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinelx.auth")


def log_auth_event(
    username: Optional[str],
    ip_address: str,
    event_type: str,
    status: str,
    details: str,
) -> None:
    """Logs authentication attempts and safety violation events."""
    message = (
        f"Auth Event - Type: {event_type}, "
        f"User: {username or 'unknown'}, "
        f"IP: {ip_address}, "
        f"Status: {status}, "
        f"Details: {details}"
    )
    logger.info(message)
