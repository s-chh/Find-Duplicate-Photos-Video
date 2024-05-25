import os
import numpy as np
import time
from PIL import Image
from tqdm import tqdm
import argparse


# Calculate distances among arrays
def find_duplicates(image, thresh=1e-3):
    image_unit = image / np.linalg.norm(image, ord=2, axis=1, keepdims=True)  # Convert images to unit vectors
    image_distances = 1 - image_unit @ image_unit.T  # Calculate cosine distance among images
    return image_distances < thresh  # Using 0.0001 distance as threshold to call it a duplicate image


def check_folder(folder, compare_size):
    print("Checking folder → " + folder)
    files = os.listdir(folder)  # Get all files in a folder
    files.sort()

    images_name = []
    all_images = []
    to_delete = []

    time.sleep(0.1)  # Otherwise TQDM's output are messed up
    for file_name in tqdm(files):
        try:  # Try to read each file as an image
            image = Image.open(os.path.join(folder, file_name)).convert('L')  # Convert to grayscale after reading
            if image is not None:
                image = image.resize((compare_size, compare_size))  # Resize image to compare size
                image = np.array(image).reshape(-1)  # Convert 2D images to 1D array for easier computation
                all_images.append(image)
                images_name.append(file_name)
        except:
            pass
    time.sleep(0.1)

    m = len(all_images)
    print("Total images found = " + str(m))

    if m < 2:
        print()
        return to_delete

    # Get all image arrays together and calculate distances among them
    all_images = np.stack(all_images)
    print(f"Finding duplicate images within the folder {folder}...")
    images_duplicates = find_duplicates(all_images)

    def file_size(image):  # Function to get file size to decide which image to keep
        return os.path.getsize(os.path.join(folder, images_name[image]))

    visited = [False] * m  # To avoid unnecessary calls to duplicate images
    files_duplicates = []
    for i in tqdm(range(m)):
        if visited[i]:
            continue
        visited[i] = True
        image_duplicates = images_duplicates[i]
        if sum(image_duplicates) > 1:
            duplicate_idx = np.where(image_duplicates)[0].tolist()  # Get indexes of all duplicate images
            # Sort the list based on their size, Reverse is set based on which file size is preferred.
            duplicate_idx.sort(key=file_size, reverse=args.keep_largest == 1)
            for idx in duplicate_idx:  # Set visited of duplicate images to True to avoid unnecessary calls
                visited[idx] = True
            files_duplicates.append(duplicate_idx)
    time.sleep(0.1)

    if len(files_duplicates) > 0:
        # Display all duplicate files within a folder.
        print()
        print("Duplicates:")
        for i in range(len(files_duplicates)):
            for j in range(len(files_duplicates[i])):
                print(images_name[files_duplicates[i][j]], end="\t")
                if j > 0:
                    to_delete.append(os.path.join(folder, images_name[files_duplicates[i][j]]))
            print()
    else:
        print("No duplicates found.")
    print()

    return to_delete


def main(args):
    print(f"Folder to be explored: {args.folder}\n\n")

    # Find all folders recursively
    folders = [folder[0] for folder in os.walk(args.folder)]
    folders.sort()

    all_deletes = []  # Stores all files to deleted
    for folder in folders:
        all_deletes += check_folder(folder, args.compare_size)

    print('-----------------------------Overall Report----------------------------------')

    if len(all_deletes) == 0:
        print("No duplicates found.")
        exit()

    print("\nFiles marked for delete:")
    for file in all_deletes:
        print(file)

    print("Print Y to delete")
    inp = input()
    if inp.lower() == 'y':
        for file in all_deletes:
            os.remove(file)
        print("Done.")
    else:
        print("Files not deleted.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='find-exact-duplicate-images')
    parser.add_argument('--folder', type=str, default=".", help='Directory of images. Default is current directory.')
    parser.add_argument('--keep_largest', type=int, default=0,
                        help='0: keeps the smallest file among duplicates; 1: keeps the largest file among duplicates')
    parser.add_argument('--compare_size', type=int, default=300,
                        help='Size used for comparison. Found 300 to be best for performance and results.')
    args = parser.parse_args()

    main(args)
