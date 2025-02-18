import os
import shutil
import random

# Define paths
SOURCE_DIR = r'C:\Users\USER\Desktop\DIESES\reduced_dataset'
TRAIN_DIR = r'C:\Users\USER\Desktop\DIESES\dataset\train'
VAL_DIR = r'C:\Users\USER\Desktop\DIESES\dataset\validation'
SPLIT_RATIO = 0.8  # 80% for training, 20% for validation

# Create directories
os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(VAL_DIR, exist_ok=True)

# Loop through each class folder
for class_name in os.listdir(SOURCE_DIR):
    class_path = os.path.join(SOURCE_DIR, class_name)
    if os.path.isdir(class_path):
        images = os.listdir(class_path)
        random.shuffle(images)

        # Split into train and validation
        train_images = images[:int(len(images) * SPLIT_RATIO)]
        val_images = images[int(len(images) * SPLIT_RATIO):]

        # Copy files to train directory
        os.makedirs(os.path.join(TRAIN_DIR, class_name), exist_ok=True)
        for img in train_images:
            shutil.copy(os.path.join(class_path, img), os.path.join(TRAIN_DIR, class_name, img))

        # Copy files to validation directory
        os.makedirs(os.path.join(VAL_DIR, class_name), exist_ok=True)
        for img in val_images:
            shutil.copy(os.path.join(class_path, img), os.path.join(VAL_DIR, class_name, img))

print("Dataset split into train and validation sets.")