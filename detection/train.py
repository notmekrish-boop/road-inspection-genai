from ultralytics import YOLO
from pathlib import Path


# ==========================================
# ROADGUARD AI
# YOLO POTHOLE DETECTOR TRAINING
# ==========================================

# Dataset configuration
DATASET = "dataset/data.yaml"

# Pre-trained YOLO model
MODEL = "yolo11n.pt"

# Training settings
EPOCHS = 50
IMAGE_SIZE = 640
BATCH_SIZE = 8

# Output location
PROJECT_NAME = "runs"
RUN_NAME = "roadguard_pothole"


def main():

    print()
    print("=" * 60)
    print("       ROADGUARD AI - YOLO TRAINING")
    print("=" * 60)
    print()

    # ------------------------------------------
    # Check dataset
    # ------------------------------------------

    if not Path(DATASET).exists():

        print("ERROR: Dataset configuration not found.")
        print()
        print("Expected:")
        print(DATASET)

        return

    print("Dataset:")
    print(DATASET)
    print()

    print("Model:")
    print(MODEL)
    print()

    print("Training configuration:")
    print("Epochs     :", EPOCHS)
    print("Image size :", IMAGE_SIZE)
    print("Batch size :", BATCH_SIZE)
    print()

    # ------------------------------------------
    # Load pretrained YOLO
    # ------------------------------------------

    print("Loading pretrained YOLO model...")
    print()

    model = YOLO(MODEL)

    print("Model loaded successfully.")
    print()

    # ------------------------------------------
    # Start training
    # ------------------------------------------

    print("=" * 60)
    print("STARTING TRAINING")
    print("=" * 60)
    print()

    results = model.train(

        data=DATASET,

        epochs=EPOCHS,

        imgsz=IMAGE_SIZE,

        batch=BATCH_SIZE,

        project=PROJECT_NAME,

        name=RUN_NAME,

        pretrained=True,

        patience=10,

        workers=2,

        verbose=True

    )

    # ------------------------------------------
    # Training completed
    # ------------------------------------------

    print()
    print("=" * 60)
    print("TRAINING COMPLETED")
    print("=" * 60)
    print()

    print("Training results saved in:")

    print(
        f"{PROJECT_NAME}/{RUN_NAME}"
    )

    print()

    print("Best model should be located at:")

    print(
        f"{PROJECT_NAME}/{RUN_NAME}/weights/best.pt"
    )

    print()


if __name__ == "__main__":
    main()