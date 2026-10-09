"""
RoadGuard AI - Incident Manager

Converts a YOLO detection + Risk Engine result
into a standardized RoadGuard incident.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional
import json


@dataclass
class Incident:
    """
    Represents one detected road incident.
    """

    incident_id: str

    timestamp: str

    object_type: str

    confidence: float

    x1: float
    y1: float
    x2: float
    y2: float

    risk_score: float
    risk_level: str

    image_path: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    source: str = "image"


def create_incident(
    object_type: str,
    confidence: float,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    risk_score: float,
    risk_level: str,
    image_path: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    source: str = "image"
) -> Incident:
    """
    Create a standardized RoadGuard incident.
    """

    # Create a timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # Create a unique incident ID
    incident_id = (
        "RG-"
        + datetime.now(timezone.utc).strftime(
            "%Y%m%d%H%M%S%f"
        )
    )

    incident = Incident(
        incident_id=incident_id,

        timestamp=timestamp,

        object_type=object_type,

        confidence=round(confidence, 4),

        x1=round(x1, 2),
        y1=round(y1, 2),
        x2=round(x2, 2),
        y2=round(y2, 2),

        risk_score=round(risk_score, 2),

        risk_level=risk_level,

        image_path=image_path,

        latitude=latitude,
        longitude=longitude,

        source=source
    )

    return incident


def incident_to_dict(incident: Incident) -> dict:
    """
    Convert Incident object into a Python dictionary.
    """

    return asdict(incident)


def incident_to_json(incident: Incident) -> str:
    """
    Convert Incident object into JSON.
    """

    return json.dumps(
        asdict(incident),
        indent=4
    )


if __name__ == "__main__":

    # Simple standalone test
    incident = create_incident(
        object_type="pothole",

        confidence=0.9011,

        x1=83.6,
        y1=94.4,
        x2=208.0,
        y2=144.2,

        risk_score=60.5,

        risk_level="MEDIUM",

        image_path="demo/input/test.jpg"
    )

    print()
    print("==========================================")
    print("       ROADGUARD INCIDENT TEST")
    print("==========================================")

    print(incident_to_json(incident))

    print("==========================================")