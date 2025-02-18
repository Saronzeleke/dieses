import os
from PIL import Image

def check_images(directory):
    corrupted_images = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Attempt to open the image
                with Image.open(file_path) as img:
                    img.verify()  # Verify that it is, in fact, an image
            except Exception as e:
                print(f"Corrupted or invalid image: {file_path} - {e}")
                corrupted_images.append(file_path)
    return corrupted_images

if __name__ == "__main__":
    TRAIN_DIR = r'C:\Users\USER\Desktop\dieses\dataset\train'
    VAL_DIR = r'C:\Users\USER\Desktop\dieses\dataset\validation'

    print("Checking training dataset...")
    corrupted_train = check_images(TRAIN_DIR)

    print("\nChecking validation dataset...")
    corrupted_val = check_images(VAL_DIR)

    if corrupted_train or corrupted_val:
        print("\nCorrupted or invalid images found:")
        for img in corrupted_train + corrupted_val:
            print(img)
    else:
        print("\nNo corrupted or invalid images found.")