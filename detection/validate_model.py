from ultralytics import YOLO
from pathlib import Path


# ==========================================
# ROADGUARD AI
# FINAL MODEL VALIDATION
# ==========================================

DATASET = "dataset/data.yaml"

MODEL = r"C:\Users\Lenovo\runs\detect\runs\roadguard_pothole\weights\best.pt"


def main():

    print()
    print("=" * 60)
    print("       ROADGUARD AI - MODEL VALIDATION")
    print("=" * 60)
    print()

    # ------------------------------------------
    # Check files
    # ------------------------------------------

    if not Path(DATASET).exists():

        print("ERROR: Dataset file not found:")
        print(DATASET)

        return

    if not Path(MODEL).exists():

        print("ERROR: Trained model not found:")
        print(MODEL)

        return

    print("Dataset:")
    print(DATASET)
    print()

    print("Model:")
    print(MODEL)
    print()

    # ------------------------------------------
    # Load trained model
    # ------------------------------------------

    print("Loading trained model...")
    print()

    model = YOLO(MODEL)

    print("Model loaded successfully.")
    print()

    # ------------------------------------------
    # Evaluate on TEST set
    # ------------------------------------------

    print("=" * 60)
    print("EVALUATING ON TEST SET")
    print("=" * 60)
    print()

    results = model.val(

        data=DATASET,

        split="test",

        imgsz=640,

        batch=8,

        workers=2,

        verbose=True

    )

    # ------------------------------------------
    # Display metrics
    # ------------------------------------------

    print()
    print("=" * 60)
    print("TEST SET RESULTS")
    print("=" * 60)
    print()

    print("Precision :", round(results.box.mp, 4))
    print("Recall    :", round(results.box.mr, 4))
    print("mAP@50    :", round(results.box.map50, 4))
    print("mAP@50-95 :", round(results.box.map, 4))

    # ------------------------------------------
    # F1 calculation
    # ------------------------------------------

    precision = results.box.mp
    recall = results.box.mr

    if precision + recall > 0:

        f1 = (
            2 * precision * recall
            / (precision + recall)
        )

    else:

        f1 = 0

    print("F1 Score  :", round(f1, 4))

    print()
    print("=" * 60)
    print("TEST EVALUATION COMPLETED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()