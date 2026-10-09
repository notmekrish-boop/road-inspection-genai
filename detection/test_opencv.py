import cv2
import argparse
import os


def main():

    # -----------------------------
    # 1. Take image path from user
    # -----------------------------
    parser = argparse.ArgumentParser(
        description="RoadGuard AI - OpenCV Image Test"
    )

    parser.add_argument("--image", type=str, default="demo/input/test.jpg", help="Path to input image")
    

    args = parser.parse_args()

    image_path = args.image

    # -----------------------------
    # 2. Check whether file exists
    # -----------------------------
    if not os.path.exists(image_path):

        print("ERROR: Image file does not exist.")
        print("Path:", image_path)

        return

    # -----------------------------
    # 3. Read image using OpenCV
    # -----------------------------
    image = cv2.imread(image_path)

    # -----------------------------
    # 4. Check whether OpenCV
    #    successfully read image
    # -----------------------------
    if image is None:

        print("ERROR: OpenCV could not read the image.")

        return

    # -----------------------------
    # 5. Get image information
    # -----------------------------
    height, width, channels = image.shape

    print("\n========== ROADGUARD OPENCV TEST ==========")

    print("Image loaded successfully!")

    print("Image path :", image_path)

    print("Width      :", width)

    print("Height     :", height)

    print("Channels   :", channels)

    print("===========================================\n")

    # -----------------------------
    # 6. Display image
    # -----------------------------
    cv2.imshow(
        "RoadGuard AI - OpenCV Test",
        image
    )

    # Wait until user presses a key
    cv2.waitKey(0)

    # Close all OpenCV windows
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()