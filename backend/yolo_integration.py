"""Glue between the YOLO/risk pipeline and the database.

Your teammates call `save_detection(...)` right after a pothole is detected
and its risk has been calculated. GenAI and the dashboard then see it
automatically because they both read from MySQL.

    from yolo_integration import save_detection

    detections = model(frame)
    ...
    save_detection(
        route="Route A",
        confidence=0.91,
        risk_level="HIGH",
        severity_score=0.87,
        latitude=23.2599,
        longitude=77.4126,
    )

Alternative (no shared Python code): POST the same fields as JSON to
http://127.0.0.1:8000/incidents
"""
import queries


def save_detection(route, confidence, risk_level, severity_score,
                   latitude, longitude, timestamp=None):
    return queries.insert_pothole(
        route=route,
        confidence=float(confidence),
        risk_level=risk_level,
        severity_score=float(severity_score),
        latitude=float(latitude),
        longitude=float(longitude),
        timestamp=timestamp,
    )


if __name__ == "__main__":
    new_id = save_detection("Route A", 0.91, "HIGH", 0.87, 23.2599, 77.4126)
    print(f"Inserted test detection with id {new_id}")
