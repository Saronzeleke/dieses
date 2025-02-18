import os
import random
import shutil

# Define paths
SOURCE_DIR = r'C:\Users\USER\Downloads\archive\PlantVillage'
TARGET_DIR = r'C:\Users\USER\Desktop\dieses\reduced_dataset'
NUM_IMAGES_PER_CLASS = 38

# Create target directory
os.makedirs(TARGET_DIR, exist_ok=True)

# Supported image extensions
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

# Loop through each class folder
for class_name in os.listdir(SOURCE_DIR):
    class_path = os.path.join(SOURCE_DIR, class_name)
    if os.path.isdir(class_path):  # Ensure it's a directory
        print(f"Processing class: {class_name}")
        images = [img for img in os.listdir(class_path) if os.path.splitext(img)[1].lower() in IMAGE_EXTENSIONS]
        random.shuffle(images)

        # Select NUM_IMAGES_PER_CLASS images
        selected_images = images[:NUM_IMAGES_PER_CLASS]

        # Create a subdirectory for the class in the target directory
        target_class_dir = os.path.join(TARGET_DIR, class_name)
        os.makedirs(target_class_dir, exist_ok=True)

        # Copy selected images to the target directory
        for img in selected_images:
            src_path = os.path.join(class_path, img)
            dst_path = os.path.join(target_class_dir, img)
            print(f"Copying: {src_path} -> {dst_path}")
            try:
                shutil.copy(src_path, dst_path)
            except Exception as e:
                print(f"Error copying {src_path}: {e}")

print(f"Reduced dataset created with {NUM_IMAGES_PER_CLASS} images per class.")