import cv2
from pathlib import Path


# ==========================================
# ROADGUARD AI
# YOLO ANNOTATION VISUALIZER
# ==========================================

DATASET_PATH = Path("dataset")

IMAGE_FOLDER = DATASET_PATH / "images" / "train"
LABEL_FOLDER = DATASET_PATH / "labels" / "train"

OUTPUT_FOLDER = Path("demo/output/annotations")

# Number of images to visualize
NUMBER_OF_IMAGES = 10


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


def find_images():

    images = []

    for file in sorted(IMAGE_FOLDER.iterdir()):

        if (
            file.is_file()
            and file.suffix.lower() in IMAGE_EXTENSIONS
        ):
            images.append(file)

    return images


def draw_annotations(image, label_file):

    height, width = image.shape[:2]

    if not label_file.exists():

        print("WARNING: Label not found:")
        print(label_file)

        return image

    with open(label_file, "r") as file:

        lines = file.readlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        values = line.split()

        if len(values) != 5:
            continue

        class_id = int(values[0])

        x_center = float(values[1])
        y_center = float(values[2])
        box_width = float(values[3])
        box_height = float(values[4])

        # --------------------------------------
        # Convert YOLO coordinates to pixels
        # --------------------------------------

        x_center_pixel = int(x_center * width)
        y_center_pixel = int(y_center * height)

        box_width_pixel = int(box_width * width)
        box_height_pixel = int(box_height * height)

        # --------------------------------------
        # Calculate bounding box corners
        # --------------------------------------

        x1 = int(
            x_center_pixel - box_width_pixel / 2
        )

        y1 = int(
            y_center_pixel - box_height_pixel / 2
        )

        x2 = int(
            x_center_pixel + box_width_pixel / 2
        )

        y2 = int(
            y_center_pixel + box_height_pixel / 2
        )

        # --------------------------------------
        # Keep coordinates inside image
        # --------------------------------------

        x1 = max(0, x1)
        y1 = max(0, y1)

        x2 = min(width - 1, x2)
        y2 = min(height - 1, y2)

        # --------------------------------------
        # Draw bounding box
        # --------------------------------------

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        # --------------------------------------
        # Class name
        # --------------------------------------

        if class_id == 0:

            class_name = "POTHOLE"

        else:

            class_name = f"CLASS {class_id}"

        # --------------------------------------
        # Draw label background
        # --------------------------------------

        text = class_name

        text_size = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            2
        )

        text_width = text_size[0][0]
        text_height = text_size[0][1]

        cv2.rectangle(
            image,
            (x1, max(0, y1 - text_height - 10)),
            (x1 + text_width + 10, y1),
            (0, 255, 0),
            -1
        )

        # --------------------------------------
        # Draw text
        # --------------------------------------

        cv2.putText(
            image,
            text,
            (x1 + 5, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            2
        )

    return image


def main():

    print()
    print("=" * 60)
    print("      ROADGUARD AI - ANNOTATION VISUALIZER")
    print("=" * 60)
    print()

    # --------------------------------------
    # Check folders
    # --------------------------------------

    if not IMAGE_FOLDER.exists():

        print("ERROR: Image folder does not exist:")
        print(IMAGE_FOLDER)

        return

    if not LABEL_FOLDER.exists():

        print("ERROR: Label folder does not exist:")
        print(LABEL_FOLDER)

        return

    # --------------------------------------
    # Create output folder
    # --------------------------------------

    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------
    # Find images
    # --------------------------------------

    images = find_images()

    print("Training images found:", len(images))
    print()

    if not images:

        print("ERROR: No images found.")

        return

    # --------------------------------------
    # Select images
    # --------------------------------------

    selected_images = images[:NUMBER_OF_IMAGES]

    print(
        f"Visualizing first "
        f"{len(selected_images)} images..."
    )

    print()

    successful = 0

    # --------------------------------------
    # Process images
    # --------------------------------------

    for image_path in selected_images:

        label_path = LABEL_FOLDER / (
            image_path.stem + ".txt"
        )

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            print(
                "Could not read:",
                image_path.name
            )

            continue

        image = draw_annotations(
            image,
            label_path
        )

        output_path = OUTPUT_FOLDER / (
            "annotated_" + image_path.name
        )

        cv2.imwrite(
            str(output_path),
            image
        )

        print(
            "Saved:",
            output_path
        )

        successful += 1

    print()
    print("=" * 60)

    print(
        "Successfully visualized:",
        successful
    )

    print()
    print("Output folder:")
    print(OUTPUT_FOLDER.resolve())

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()