import os
from pathlib import Path


def print_folder_structure(folder, level=0, max_items=20):

    path = Path(folder)

    indent = "    " * level

    print(f"{indent}{path.name}/")

    try:

        items = sorted(path.iterdir())

    except PermissionError:

        print(f"{indent}    [Permission Denied]")

        return

    # Limit output so huge datasets don't flood terminal
    items = items[:max_items]

    for item in items:

        if item.is_dir():

            print_folder_structure(
                item,
                level + 1,
                max_items
            )

        else:

            print(
                f"{indent}    {item.name}"
            )


def count_files(folder):

    path = Path(folder)

    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    label_extensions = {
        ".txt",
        ".xml",
        ".json"
    }

    image_count = 0
    label_count = 0

    for file in path.rglob("*"):

        if not file.is_file():
            continue

        if file.suffix.lower() in image_extensions:

            image_count += 1

        if file.suffix.lower() in label_extensions:

            label_count += 1

    return image_count, label_count


def main():

    dataset_path = input(
        "Enter dataset folder path: "
    ).strip()

    if not os.path.exists(dataset_path):

        print("\nERROR: Dataset folder does not exist.")

        return

    print("\n===================================")
    print("ROADGUARD DATASET INSPECTION")
    print("===================================\n")

    print("DATASET STRUCTURE:\n")

    print_folder_structure(
        dataset_path
    )

    images, labels = count_files(
        dataset_path
    )

    print("\n===================================")

    print("Images found :", images)

    print("Labels found :", labels)

    print("===================================")


if __name__ == "__main__":
    main()