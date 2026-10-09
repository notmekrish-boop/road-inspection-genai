import sys
from pathlib import Path

# ============================================================
# ADD ROADGUARD AI PROJECT ROOT TO PYTHON PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT LIBRARIES
# ============================================================

import cv2
from ultralytics import YOLO

from risk_engine.risk import calculate_visual_risk
from incident.incident_manager import create_incident
from database.db import initialize_database, insert_incident


# ============================================================
# CONFIGURATION
# ============================================================

# YOLO trained model
MODEL_PATH = r"C:\Users\Lenovo\runs\detect\runs\roadguard_pothole\weights\best.pt"

# Input image
IMAGE_PATH = r"D:\RoadGuardAI\demo\input\road1.jpg"

# Output directory
OUTPUT_DIR = Path(
    r"D:\RoadGuardAI\demo\output\detections"
)

# Output image
OUTPUT_PATH = OUTPUT_DIR / "risk_detected_test.jpg"

# Minimum YOLO confidence
CONFIDENCE_THRESHOLD = 0.25


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():

    print()
    print("==============================================")
    print("        ROADGUARD AI IMAGE DETECTION")
    print("==============================================")

        # --------------------------------------------------------
    # Initialize RoadGuard database
    # --------------------------------------------------------

    initialize_database()

    print()
    print("RoadGuard database initialized.")

    # --------------------------------------------------------
    # 1. Check YOLO model
    # --------------------------------------------------------

    if not Path(MODEL_PATH).exists():

        print()
        print("ERROR: YOLO model not found.")
        print("Model path:")
        print(MODEL_PATH)
        return

    # --------------------------------------------------------
    # 2. Check input image
    # --------------------------------------------------------

    if not Path(IMAGE_PATH).exists():

        print()
        print("ERROR: Input image not found.")
        print("Image path:")
        print(IMAGE_PATH)
        return

    # --------------------------------------------------------
    # 3. Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 4. Load YOLO model
    # --------------------------------------------------------

    print()
    print("Loading YOLO model...")

    model = YOLO(MODEL_PATH)

    print("YOLO model loaded successfully.")

    # --------------------------------------------------------
    # 5. Read image using OpenCV
    # --------------------------------------------------------

    image = cv2.imread(IMAGE_PATH)

    if image is None:

        print()
        print("ERROR: OpenCV could not read the image.")
        return

    image_height, image_width = image.shape[:2]

    print()
    print("Image information:")
    print("Width  :", image_width)
    print("Height :", image_height)

    # --------------------------------------------------------
    # 6. Run YOLO detection
    # --------------------------------------------------------

    print()
    print("Running YOLO detection...")

    results = model.predict(
        source=image,
        conf=CONFIDENCE_THRESHOLD,
        verbose=False
    )

    # --------------------------------------------------------
    # 7. Detection counter
    # --------------------------------------------------------

    total_detections = 0

    # --------------------------------------------------------
    # 8. Process every YOLO result
    # --------------------------------------------------------

    for result in results:

        # ----------------------------------------------------
        # Check whether boxes exist
        # ----------------------------------------------------

        if result.boxes is None:
            continue

        boxes = result.boxes

        # ----------------------------------------------------
        # Process every detected object
        # ----------------------------------------------------

        for box in boxes:

            # ------------------------------------------------
            # Get confidence
            # ------------------------------------------------

            confidence = float(
                box.conf[0].item()
            )

            # ------------------------------------------------
            # Get class ID
            # ------------------------------------------------

            class_id = int(
                box.cls[0].item()
            )

            # ------------------------------------------------
            # Get class name
            # ------------------------------------------------

            class_name = model.names[class_id]

            # ------------------------------------------------
            # Get bounding box coordinates
            # ------------------------------------------------

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # ------------------------------------------------
            # Calculate visual risk
            # ------------------------------------------------

            risk_result = calculate_visual_risk(
                confidence=confidence,

                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,

                image_width=image_width,
                image_height=image_height
            )

            # ------------------------------------------------
            # Increase detection count
            # ------------------------------------------------

            total_detections += 1

            # ------------------------------------------------
            # Create RoadGuard Incident
            # ------------------------------------------------

            incident = create_incident(             # 

                object_type=class_name,

                confidence=confidence,

                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,

                risk_score=risk_result.score,

                risk_level=risk_result.level,

                image_path=IMAGE_PATH,

                latitude=None,
                longitude=None,

                source="image"
            )
                        # ------------------------------------------------
            # Save incident to SQLite
            # ------------------------------------------------

            insert_incident(incident)

            print()
            print("Incident saved to SQLite database.")

            # ------------------------------------------------
            # Print detection information
            # ------------------------------------------------

            print()
            print("----------------------------------------------")
            print(f"Detection #{total_detections}")
            print("----------------------------------------------")

            print(
                "Object          :",
                class_name
            )

            print(
                f"Confidence      : "
                f"{confidence * 100:.2f}%"
            )

            print(
                f"Bounding Box    : "
                f"({x1:.1f}, {y1:.1f}) -> "
                f"({x2:.1f}, {y2:.1f})"
            )

            # ------------------------------------------------
            # Risk information
            # ------------------------------------------------

            print(
                f"Risk Score      : "
                f"{risk_result.score:.2f}/100"
            )

            print(
                f"Risk Level      : "
                f"{risk_result.level}"
            )

            print(
                f"Confidence Part : "
                f"{risk_result.confidence_score:.2f}"
            )

            print(
                f"Size Part       : "
                f"{risk_result.size_score:.2f}"
            )

            print(
                f"Position Part   : "
                f"{risk_result.position_score:.2f}"
            )

            # ------------------------------------------------
            # Incident information
            # ------------------------------------------------

            print()
            print("RoadGuard Incident Created")
            print("----------------------------------------------")

            print(
                "Incident ID     :",
                incident.incident_id
            )

            print(
                "Timestamp       :",
                incident.timestamp
            )

            print(
                "Object          :",
                incident.object_type
            )

            print(
                f"Confidence      : "
                f"{incident.confidence * 100:.2f}%"
            )

            print(
                "Risk Score      :",
                incident.risk_score
            )

            print(
                "Risk Level      :",
                incident.risk_level
            )

            print(
                "Source          :",
                incident.source
            )

            print(
                "Image           :",
                incident.image_path
            )

            print("----------------------------------------------")

            # ------------------------------------------------
            # Convert bounding box to integer coordinates
            # ------------------------------------------------

            x1_int = int(x1)
            y1_int = int(y1)
            x2_int = int(x2)
            y2_int = int(y2)

            # ------------------------------------------------
            # Draw bounding box
            # ------------------------------------------------

            cv2.rectangle(
                image,

                (x1_int, y1_int),

                (x2_int, y2_int),

                (0, 255, 0),

                2
            )

            # ------------------------------------------------
            # Create detection label
            # ------------------------------------------------

            label_1 = (
                f"{class_name} "
                f"{confidence * 100:.1f}%"
            )

            # ------------------------------------------------
            # Create risk label
            # ------------------------------------------------

            label_2 = (
                f"Risk: {risk_result.level} "
                f"({risk_result.score:.1f})"
            )

            # ------------------------------------------------
            # Position first label
            # ------------------------------------------------

            text_y = max(
                y1_int - 25,
                20
            )

            # ------------------------------------------------
            # Draw detection label
            # ------------------------------------------------

            cv2.putText(

                image,

                label_1,

                (x1_int, text_y),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (0, 255, 0),

                2
            )

            # ------------------------------------------------
            # Position risk label
            # ------------------------------------------------

            risk_text_y = max(
                y1_int - 5,
                40
            )

            # ------------------------------------------------
            # Draw risk label
            # ------------------------------------------------

            cv2.putText(

                image,

                label_2,

                (x1_int, risk_text_y),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (0, 255, 255),

                2
            )

    # ========================================================
    # 9. Save annotated image
    # ========================================================

    cv2.imwrite(
        str(OUTPUT_PATH),
        image
    )

    # ========================================================
    # 10. Final summary
    # ========================================================

    print()
    print("==============================================")
    print("              DETECTION SUMMARY")
    print("==============================================")

    print(
        "Total detections :",
        total_detections
    )

    print(
        "Output image     :",
        OUTPUT_PATH
    )

    print("==============================================")
    print()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()