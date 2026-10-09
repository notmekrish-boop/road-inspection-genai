from pathlib import Path


# ==========================================
# ROADGUARD AI - DATASET VALIDATOR
# ==========================================

# Change this only if your dataset folder has a different name
DATASET_PATH = Path("dataset")

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


def find_images():
    """Find all images inside the dataset."""

    images = []

    for file in DATASET_PATH.rglob("*"):
        if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(file)

    return images


def find_labels():
    """Find all YOLO label files."""

    labels = []

    for file in DATASET_PATH.rglob("*.txt"):
        labels.append(file)

    return labels


def validate_label_file(label_file):
    """
    Check whether a label file follows YOLO format.

    YOLO format:

    class_id x_center y_center width height

    Example:

    0 0.523 0.481 0.210 0.154
    """

    errors = []

    try:
        with open(label_file, "r") as file:
            lines = file.readlines()

    except Exception as e:
        errors.append(f"Could not read file: {e}")
        return errors

    for line_number, line in enumerate(lines, start=1):

        line = line.strip()

        # Empty label files are allowed for images with no object
        if not line:
            continue

        values = line.split()

        # YOLO annotation should have exactly 5 values
        if len(values) != 5:
            errors.append(
                f"Line {line_number}: expected 5 values, found {len(values)}"
            )
            continue

        try:
            class_id = int(values[0])

            x_center = float(values[1])
            y_center = float(values[2])
            width = float(values[3])
            height = float(values[4])

        except ValueError:
            errors.append(
                f"Line {line_number}: contains non-numeric values"
            )
            continue

        # Class ID should not be negative
        if class_id < 0:
            errors.append(
                f"Line {line_number}: invalid class ID {class_id}"
            )

        # YOLO coordinates must normally be between 0 and 1
        if not (0 <= x_center <= 1):
            errors.append(
                f"Line {line_number}: x_center={x_center}"
            )

        if not (0 <= y_center <= 1):
            errors.append(
                f"Line {line_number}: y_center={y_center}"
            )

        if not (0 <= width <= 1):
            errors.append(
                f"Line {line_number}: width={width}"
            )

        if not (0 <= height <= 1):
            errors.append(
                f"Line {line_number}: height={height}"
            )

    return errors


def main():

    print()
    print("=" * 60)
    print("       ROADGUARD AI - DATASET VALIDATION")
    print("=" * 60)
    print()

    # ------------------------------------------
    # Check dataset folder
    # ------------------------------------------

    if not DATASET_PATH.exists():

        print("ERROR: Dataset folder was not found.")
        print()
        print("Expected location:")
        print(DATASET_PATH)

        return

    print("Dataset location:")
    print(DATASET_PATH.resolve())
    print()

    # ------------------------------------------
    # Find images and labels
    # ------------------------------------------

    images = find_images()
    labels = find_labels()

    print("Images found :", len(images))
    print("Labels found :", len(labels))
    print()

    # ------------------------------------------
    # Check image-label count
    # ------------------------------------------

    if len(images) == len(labels):

        print("PASS: Number of images and labels match.")

    else:

        print("WARNING: Image and label counts do not match.")

    print()

    # ------------------------------------------
    # Validate labels
    # ------------------------------------------

    print("Checking YOLO label format...")
    print()

    total_errors = 0
    valid_files = 0

    for label_file in labels:

        errors = validate_label_file(label_file)

        if errors:

            print()
            print("ERROR IN:", label_file)

            for error in errors:
                print("   ->", error)

            total_errors += len(errors)

        else:

            valid_files += 1

    print()
    print("=" * 60)

    print("VALIDATION RESULT")
    print("=" * 60)

    print()

    print("Total images       :", len(images))
    print("Total label files  :", len(labels))
    print("Valid label files  :", valid_files)
    print("Total errors       :", total_errors)

    print()

    if total_errors == 0:

        print("SUCCESS!")
        print("Your label files appear to be in YOLO format.")

    else:

        print("WARNING!")
        print("Some label files contain errors.")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()