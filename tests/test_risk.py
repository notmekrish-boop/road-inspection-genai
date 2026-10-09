import sys
from pathlib import Path

# --------------------------------------------------
# Add RoadGuardAI project root to Python path
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# --------------------------------------------------
# Import Risk Engine
# --------------------------------------------------

from risk_engine.risk import calculate_visual_risk


# --------------------------------------------------
# Main test
# --------------------------------------------------

def main():

    # Example image size
    image_width = 640
    image_height = 480

    # Example YOLO detection
    confidence = 0.90

    x1 = 100
    y1 = 150
    x2 = 300
    y2 = 250

    # Calculate visual risk
    result = calculate_visual_risk(
        confidence=confidence,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
        image_width=image_width,
        image_height=image_height
    )

    # --------------------------------------------------
    # Display result
    # --------------------------------------------------

    print()
    print("======================================")
    print("       ROADGUARD RISK ENGINE")
    print("======================================")

    print(f"YOLO Confidence : {result.confidence * 100:.2f}%")

    print(f"Relative Area   : {result.relative_area}")

    print(f"Vertical Pos.   : {result.vertical_position}")

    print("--------------------------------------")

    print(f"Confidence Score: {result.confidence_score:.2f}")

    print(f"Size Score      : {result.size_score:.2f}")

    print(f"Position Score  : {result.position_score:.2f}")

    print("--------------------------------------")

    print(f"TOTAL RISK      : {result.score:.2f}/100")

    print(f"RISK LEVEL      : {result.level}")

    print("======================================")
    print()


# --------------------------------------------------
# Run program
# --------------------------------------------------

if __name__ == "__main__":
    main()