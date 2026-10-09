from pathlib import Path
from collections import Counter


# ==========================================
# ROADGUARD AI
# DATASET CLASS INSPECTOR
# ==========================================

DATASET_PATH = Path("dataset")


def find_label_files():
    """Find all YOLO label files."""

    label_files = []

    for file in DATASET_PATH.rglob("*.txt"):
        label_files.append(file)

    return label_files


def inspect_classes(label_files):
    """
    Read every YOLO annotation and count
    how many times each class ID appears.
    """

    class_counter = Counter()

    for label_file in label_files:

        try:

            with open(label_file, "r") as file:

                lines = file.readlines()

            for line in lines:

                line = line.strip()

                # Ignore empty lines
                if not line:
                    continue

                values = line.split()

                # YOLO format:
                # class_id x_center y_center width height

                if len(values) != 5:
                    continue

                class_id = int(values[0])

                class_counter[class_id] += 1

        except Exception as e:

            print("Could not read:", label_file)
            print("Error:", e)

    return class_counter


def main():

    print()
    print("=" * 60)
    print("       ROADGUARD AI - CLASS INSPECTION")
    print("=" * 60)
    print()

    # ------------------------------------------
    # Check dataset
    # ------------------------------------------

    if not DATASET_PATH.exists():

        print("ERROR: Dataset folder was not found.")
        print()
        print("Expected:")
        print(DATASET_PATH)

        return

    # ------------------------------------------
    # Find labels
    # ------------------------------------------

    label_files = find_label_files()

    print("Dataset:")
    print(DATASET_PATH.resolve())
    print()

    print("Label files found:", len(label_files))
    print()

    # ------------------------------------------
    # Count classes
    # ------------------------------------------

    class_counter = inspect_classes(label_files)

    # ------------------------------------------
    # Display result
    # ------------------------------------------

    print("=" * 60)
    print("CLASS IDs FOUND")
    print("=" * 60)
    print()

    if not class_counter:

        print("No class IDs were found.")
        return

    for class_id in sorted(class_counter):

        print(
            f"Class ID {class_id} "
            f"-> {class_counter[class_id]} annotations"
        )

    print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print()

    print("Number of different classes:", len(class_counter))

    print()

    print("Class IDs:")

    for class_id in sorted(class_counter):

        print(" ", class_id)

    print()

    print("=" * 60)

    print()
    print("IMPORTANT:")
    print("Class IDs tell us which classes exist,")
    print("but they do NOT tell us their names.")
    print()
    print("We will determine the class names from")
    print("the original dataset information before")
    print("creating data.yaml.")
    print()


if __name__ == "__main__":
    main()