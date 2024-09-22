import os
import time
import argparse
import numpy as np
from PIL import Image
from tqdm import tqdm


# Flag duplicates using cosine distance
def find_duplicates(image, thresh=1e-3):
    """
    Function for finding pair of duplicates in an array.
    As all samples combination pairs needs to be tested , I decided to use cosine distance among samples as it is fast to compute.
    A threshold is used for deciding if samples are same or not. Found 1e-3 to work the best.

    Parameters:
        image                         (numpy array) : 2D array of shape (n_files, flattened_image_pixels)
        threshold for cosine distance (float)       : threshold for deciding duplicate or not.

    Returns:
        bool numpy array of shape (n_files, n_files)
    """

    image_unit = image / np.linalg.norm(image, ord=2, axis=1, keepdims=True)    # Convert images to unit vectors
    image_distances = 1 - image_unit @ image_unit.T                             # Calculate cosine distance among images
    return image_distances < thresh                                             # Using 0.0001 distance as threshold to call it a duplicate image


def check_folder(folder, compare_size=300):
    """
    Function for reading all the files inside the folder and comparing them.

    Parameters:
        folder       (directory_path) : Path to the folder that needs to be checked.
        compare_size (int)            : All images will be resized to this size for comparison. 
                                        Higher consumes memory and Low can lead to inaccurate results. 
                                        300 is a good spot which means every image will be resized to 300 X 300.
    Returns:
        array of the file path that are duplicate.
    """

    print("Checking folder → " + folder)
    files = os.listdir(folder)                              # Get all files in a folder
    files.sort()

    images_name = []
    all_images  = []
    to_delete   = []

    # Read all images in the folder
    time.sleep(0.1)  # Otherwise TQDM's output are generally messed up
    for file_name in tqdm(files):
        # Try to read each file as an image
        try:  
            image = Image.open(os.path.join(folder, file_name)).convert('L')    # Convert to grayscale after reading
            if image is not None:
                image = image.resize((compare_size, compare_size))              # Resize image to compare size
                image = np.array(image).reshape(-1)                             # Convert 2D images to 1D array for easier computation
                all_images.append(image)
                images_name.append(file_name)
        except:
            pass
    time.sleep(0.1)

    m = len(all_images)
    print("Total images found = " + str(m))

    if m < 2:                                                                   # Duplicates not possible if the number of images are 0 or 1.
        print()
        return to_delete                                                        # Return empty array

    # Combine all image arrays together and flag duplicates
    all_images = np.stack(all_images)
    print(f"Finding duplicate images within the folder {folder}...")
    images_duplicates = find_duplicates(all_images)

    def file_size(image):                                                       # Function to get file size to decide which image to keep
        return os.path.getsize(os.path.join(folder, images_name[image]))

    # Collect all flagged duplicates and decide which files to keep.
    visited          = [False] * m                                              # To avoid unnecessary calls to duplicate images
    files_duplicates = []                                                       # Store duplicates for each file
    for i in tqdm(range(m)):
        if visited[i]:
            continue
        visited[i] = True

        image_duplicates = images_duplicates[i]                                 # Get flags of the file
        if sum(image_duplicates) > 1:                                           # If more than 1 file similar to the current file (including current file)
            duplicate_idx = np.where(image_duplicates)[0].tolist()              # Get indexes of all duplicate images
            duplicate_idx.sort(key=file_size, reverse=args.keep_largest == 1)   # Sort the list based on their size, Reverse is set based on which file size is preferred.
            
            for j, idx in enumerate(duplicate_idx):                             
                visited[idx] = True                                             # Set visited of duplicate images to True to avoid unnecessary calls
                if j > 0:
                    to_delete.append(os.path.join(folder, images_name[idx]))    # Add all duplicate files for deletion except the prefered original file
            files_duplicates.append(duplicate_idx)
    
    time.sleep(0.1)

    # Display all duplicate files within the folder.
    if len(files_duplicates) > 0:
        print("\nDuplicates:")
        for i in range(len(files_duplicates)):            
            for j in range(len(files_duplicates[i])):
                print(images_name[files_duplicates[i][j]], end="\t")

            print()
    else:
        print("No duplicates found.")
    print()

    return to_delete


def main(args):
    print(f"Folder to be explored: {args.folder}\n\n")

    folders = [folder[0] for folder in os.walk(args.folder)]        # Find all folders to be searched recursively
    folders.sort()

    all_deletes = []                                                # Stores all files to deleted
    for folder in folders:
        all_deletes += check_folder(folder, args.compare_size)

    print('-----------------------------Overall Report----------------------------------')

    if len(all_deletes) == 0:
        print("No duplicates found.")
        exit()

    # Display all files marked for delete
    print("\nFiles marked for delete:")
    for file in all_deletes:
        print(file)

    # Prompt to decide whether to delete
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
    parser.add_argument('--folder',       type=str, default="." , help='Directory of images. Default is current directory.')
    parser.add_argument('--keep_largest', type=int, default=0,    help='0: keeps the smallest file among duplicates; 1: keeps the largest file among duplicates')
    parser.add_argument('--compare_size', type=int, default=300,  help='Size used for comparison. Found 300 to be best for performance and results.')
    args = parser.parse_args()

    main(args)
