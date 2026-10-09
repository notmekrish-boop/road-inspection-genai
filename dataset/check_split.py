from pathlib import Path


DATASET_PATH = Path("dataset")

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


def count_images(folder):

    if not folder.exists():
        return 0

    return sum(
        1
        for file in folder.iterdir()
        if file.is_file()
        and file.suffix.lower() in IMAGE_EXTENSIONS
    )


def count_labels(folder):

    if not folder.exists():
        return 0

    return sum(
        1
        for file in folder.iterdir()
        if file.is_file()
        and file.suffix.lower() == ".txt"
    )


def main():

    print()
    print("=" * 55)
    print("       ROADGUARD AI - DATASET SPLIT CHECK")
    print("=" * 55)
    print()

    total_images = 0
    total_labels = 0

    for split in ["train", "val", "test"]:

        image_folder = DATASET_PATH / "images" / split
        label_folder = DATASET_PATH / "labels" / split

        images = count_images(image_folder)
        labels = count_labels(label_folder)

        total_images += images
        total_labels += labels

        print(f"{split.upper():<8} images : {images}")
        print(f"{'':<8} labels : {labels}")
        print()

    print("-" * 55)

    print(f"TOTAL    images : {total_images}")
    print(f"TOTAL    labels : {total_labels}")

    print()
    print("=" * 55)

    if total_images == total_labels:
        print("PASS: Total images and labels match.")
    else:
        print("WARNING: Total images and labels do not match.")

    print("=" * 55)
    print()


if __name__ == "__main__":
    main()