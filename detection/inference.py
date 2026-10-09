"""
RoadGuard AI - Reusable Image Inference

This module allows the Streamlit dashboard
to send an uploaded image directly to YOLO.

Pipeline:

Uploaded Image
      ↓
OpenCV
      ↓
YOLO11n
      ↓
Risk Engine
      ↓
Incident Manager
      ↓
SQLite
      ↓
Annotated Image
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import cv2
from ultralytics import YOLO

from risk_engine.risk import calculate_visual_risk
from incident.incident_manager import create_incident
from database.db import initialize_database, insert_incident


# =========================================================
# CONFIGURATION
# =========================================================

MODEL_PATH = (
    r"C:\Users\Lenovo\runs\detect\runs"
    r"\roadguard_pothole\weights\best.pt"
)

CONFIDENCE_THRESHOLD = 0.25


# =========================================================
# LOAD MODEL
# =========================================================

_model = None


def get_model():
    """
    Load the YOLO model only when required.

    The model is kept in memory after the first load.
    """

    global _model

    if _model is None:

        print("Loading RoadGuard YOLO model...")

        _model = YOLO(MODEL_PATH)

        print("YOLO model loaded successfully.")

    return _model


# =========================================================
# IMAGE DETECTION
# =========================================================

def detect_image(
    image_path,
    output_path
):
    """
    Detect potholes in an image.

    Parameters
    ----------
    image_path : str or Path
        Input image.

    output_path : str or Path
        Where annotated image should be saved.

    Returns
    -------
    dict
        Detection results.
    """

    image_path = Path(image_path)
    output_path = Path(output_path)

    # -----------------------------------------------------
    # Check input image
    # -----------------------------------------------------

    if not image_path.exists():

        raise FileNotFoundError(
            f"Input image not found: {image_path}"
        )


    # -----------------------------------------------------
    # Read image using OpenCV
    # -----------------------------------------------------

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        raise ValueError(
            "OpenCV could not read the image."
        )


    image_height, image_width = image.shape[:2]


    # -----------------------------------------------------
    # Initialize database
    # -----------------------------------------------------

    initialize_database()


    # -----------------------------------------------------
    # Load YOLO
    # -----------------------------------------------------

    model = get_model()


    # -----------------------------------------------------
    # Run detection
    # -----------------------------------------------------

    results = model.predict(
        source=image,
        conf=CONFIDENCE_THRESHOLD,
        verbose=False
    )


    detections = []


    # -----------------------------------------------------
    # Process detections
    # -----------------------------------------------------

    for result in results:

        boxes = result.boxes


        if boxes is None:
            continue


        for box in boxes:

            # ---------------------------------------------
            # Bounding box
            # ---------------------------------------------

            coordinates = (
                box.xyxy[0]
                .cpu()
                .numpy()
            )

            x1, y1, x2, y2 = coordinates


            # ---------------------------------------------
            # Confidence
            # ---------------------------------------------

            confidence = float(
                box.conf[0]
                .cpu()
                .item()
            )


            # ---------------------------------------------
            # Class
            # ---------------------------------------------

            class_id = int(
                box.cls[0]
                .cpu()
                .item()
            )


            object_type = "pothole"


            # ---------------------------------------------
            # Risk calculation
            # ---------------------------------------------

            risk = calculate_visual_risk(
                confidence=confidence,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                image_width=image_width,
                image_height=image_height
            )


            # ---------------------------------------------
            # Create RoadGuard incident
            # ---------------------------------------------

            incident = create_incident(
                object_type=object_type,
                confidence=confidence,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                risk_score=risk.score,
                risk_level=risk.level,
                image_path=str(image_path),
                source="dashboard_upload"
            )


            # ---------------------------------------------
            # Save incident to SQLite
            # ---------------------------------------------

            insert_incident(
                incident
            )


            # ---------------------------------------------
            # Store detection information
            # ---------------------------------------------

            detections.append(
                {
                    "incident_id": incident.incident_id,
                    "object_type": object_type,
                    "confidence": confidence,
                    "risk_score": risk.score,
                    "risk_level": risk.level,
                    "x1": float(x1),
                    "y1": float(y1),
                    "x2": float(x2),
                    "y2": float(y2)
                }
            )


            # ---------------------------------------------
            # Draw bounding box
            # ---------------------------------------------

            cv2.rectangle(
                image,
                (
                    int(x1),
                    int(y1)
                ),
                (
                    int(x2),
                    int(y2)
                ),
                (0, 255, 0),
                2
            )


            # ---------------------------------------------
            # Label
            # ---------------------------------------------

            label = (
                f"Pothole "
                f"{confidence * 100:.1f}% "
                f"| {risk.level}"
            )


            cv2.putText(
                image,
                label,
                (
                    int(x1),
                    max(
                        int(y1) - 10,
                        20
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2
            )


    # -----------------------------------------------------
    # Save annotated image
    # -----------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    cv2.imwrite(
        str(output_path),
        image
    )


    # -----------------------------------------------------
    # Return results
    # -----------------------------------------------------

    return {
        "image_path": str(image_path),
        "output_path": str(output_path),
        "image_width": image_width,
        "image_height": image_height,
        "detection_count": len(detections),
        "detections": detections
    }