import cv2
from ultralytics import YOLO
from pathlib import Path


# ==========================================
# ROADGUARD AI
# VIDEO POTHOLE DETECTION
# ==========================================

MODEL_PATH = "models/pothole_best.pt"

INPUT_VIDEO = "demo/input/road_test.mp4"

OUTPUT_FOLDER = Path("demo/output/videos")

OUTPUT_VIDEO = OUTPUT_FOLDER / "road_detection.mp4"

CONFIDENCE_THRESHOLD = 0.25


def main():

    print()
    print("=" * 60)
    print("       ROADGUARD AI - VIDEO DETECTION")
    print("=" * 60)
    print()

    # ------------------------------------------
    # Check model
    # ------------------------------------------

    if not Path(MODEL_PATH).exists():

        print("ERROR: Model not found:")
        print(MODEL_PATH)

        return

    # ------------------------------------------
    # Check video
    # ------------------------------------------

    if not Path(INPUT_VIDEO).exists():

        print("ERROR: Input video not found:")
        print(INPUT_VIDEO)

        print()
        print("Put your road video here:")
        print(Path(INPUT_VIDEO).resolve())

        return

    # ------------------------------------------
    # Create output folder
    # ------------------------------------------

    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    # ------------------------------------------
    # Load YOLO model
    # ------------------------------------------

    print("Loading RoadGuard AI model...")
    print()

    model = YOLO(MODEL_PATH)

    print("Model loaded successfully.")
    print()

    # ------------------------------------------
    # Open video
    # ------------------------------------------

    cap = cv2.VideoCapture(
        INPUT_VIDEO
    )

    if not cap.isOpened():

        print("ERROR: Could not open video.")

        return

    # ------------------------------------------
    # Read video properties
    # ------------------------------------------

    width = int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    duration = (
        total_frames / fps
        if fps > 0
        else 0
    )

    print("Video information:")
    print("Width        :", width)
    print("Height       :", height)
    print("FPS          :", fps)
    print("Total frames :", total_frames)
    print("Duration     :", round(duration, 2), "seconds")
    print()

    # ------------------------------------------
    # Create video writer
    # ------------------------------------------

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(

        str(OUTPUT_VIDEO),

        fourcc,

        fps,

        (width, height)

    )

    if not writer.isOpened():

        print("ERROR: Could not create output video.")

        cap.release()

        return

    # ------------------------------------------
    # Processing counters
    # ------------------------------------------

    frame_number = 0

    frames_with_potholes = 0

    total_detections = 0

    # ------------------------------------------
    # Process video
    # ------------------------------------------

    print("=" * 60)
    print("STARTING VIDEO PROCESSING")
    print("=" * 60)
    print()

    while True:

        success, frame = cap.read()

        if not success:

            break

        frame_number += 1

        # --------------------------------------
        # Run YOLO
        # --------------------------------------

        results = model.predict(

            source=frame,

            imgsz=640,

            conf=CONFIDENCE_THRESHOLD,

            verbose=False

        )

        result = results[0]

        boxes = result.boxes

        detection_count = len(boxes)

        if detection_count > 0:

            frames_with_potholes += 1

            total_detections += detection_count

        # --------------------------------------
        # Draw YOLO detections
        # --------------------------------------

        annotated_frame = result.plot()

        # --------------------------------------
        # Add RoadGuard information
        # --------------------------------------

        cv2.putText(

            annotated_frame,

            f"RoadGuard AI | Frame: {frame_number}",

            (20, 35),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (255, 255, 255),

            2

        )

        cv2.putText(

            annotated_frame,

            f"Potholes: {detection_count}",

            (20, 70),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (255, 255, 255),

            2

        )

        # --------------------------------------
        # Save frame
        # --------------------------------------

        writer.write(
            annotated_frame
        )

        # --------------------------------------
        # Progress display
        # --------------------------------------

        if frame_number % 30 == 0:

            percentage = (

                frame_number
                / total_frames
                * 100

                if total_frames > 0
                else 0

            )

            print(

                f"Processed "
                f"{frame_number}/{total_frames} "
                f"frames "
                f"({percentage:.1f}%)"

            )

    # ------------------------------------------
    # Release resources
    # ------------------------------------------

    cap.release()

    writer.release()

    # ------------------------------------------
    # Final statistics
    # ------------------------------------------

    print()
    print("=" * 60)
    print("VIDEO PROCESSING COMPLETED")
    print("=" * 60)
    print()

    print("Frames processed       :", frame_number)

    print(
        "Frames with potholes   :",
        frames_with_potholes
    )

    print(
        "Total raw detections   :",
        total_detections
    )

    print()

    print("Output video:")
    print(OUTPUT_VIDEO.resolve())

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()