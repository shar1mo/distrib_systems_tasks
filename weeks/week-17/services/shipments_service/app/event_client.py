import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from app.settings import get_settings

logger = logging.getLogger(__name__)


def publish_shipment_event(event_type: str, shipment: dict[str, Any]) -> None:
    settings = get_settings()
    if not settings.audit_url:
        return

    payload = {
        "type": event_type,
        "shipment": shipment,
        "emitted_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        with httpx.Client(timeout=2.0) as client:
            client.post(f"{settings.audit_url}/internal/events", json=payload).raise_for_status()
    except Exception as exc:
        logger.warning("Shipment event delivery failed: %s", exc)
