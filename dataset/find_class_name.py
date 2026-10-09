from pathlib import Path


# ==========================================
# ROADGUARD AI
# FIND DATASET CLASS NAME
# ==========================================

DATASET_PATH = Path("dataset")


def main():

    print()
    print("=" * 60)
    print("       ROADGUARD AI - FIND CLASS NAME")
    print("=" * 60)
    print()

    if not DATASET_PATH.exists():

        print("ERROR: Dataset folder was not found.")
        print(DATASET_PATH)
        return

    print("Searching dataset for class information...")
    print()

    # Files that commonly contain class names
    possible_files = []

    for file in DATASET_PATH.rglob("*"):

        if not file.is_file():
            continue

        name = file.name.lower()

        if name in {
            "data.yaml",
            "data.yml",
            "dataset.yaml",
            "dataset.yml",
            "classes.txt",
            "classes.names",
            "obj.names",
            "README.txt",
            "readme.txt"
        }:

            possible_files.append(file)

    # ------------------------------------------
    # Display discovered metadata files
    # ------------------------------------------

    if not possible_files:

        print("No obvious class-name metadata file was found.")
        print()
        print("We will need to inspect the dataset folder manually.")
        print()

        print("Dataset root contents:")
        print("-" * 60)

        for item in sorted(DATASET_PATH.iterdir()):

            if item.is_dir():
                print("[FOLDER]", item.name)
            else:
                print("[FILE]  ", item.name)

        print("-" * 60)

        return

    # ------------------------------------------
    # Read metadata files
    # ------------------------------------------

    print("Possible class information files found:")
    print()

    for file in possible_files:

        print("-" * 60)
        print("FILE:", file)
        print("-" * 60)

        try:

            with open(file, "r", encoding="utf-8", errors="ignore") as f:

                content = f.read()

            print(content[:5000])

        except Exception as e:

            print("Could not read file:", e)

        print()


if __name__ == "__main__":
    main()