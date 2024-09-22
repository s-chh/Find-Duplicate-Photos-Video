import os
import numpy as np
import time
from PIL import Image
from tqdm import tqdm
import argparse
import cv2


video_extensions = ['.mov', '.avi', '.mp4', '.wmv', '.flv', '.mkv']

# Calculate distances among arrays
def find_duplicates(video, thresh=1e-3):
    """
    Function for finding pair of duplicates in an array.
    As all samples combination pairs needs to be tested , I decided to use cosine distance among samples as it is fast to compute.
    A threshold is used for deciding if samples are same or not. Found 1e-3 to work the best.

    Parameters:
        video                         (numpy array) : 2D array of shape (n_files, flattened_frame_pixels)
        threshold for cosine distance (float)       : threshold for deciding duplicate or not.

    Returns:
        bool numpy array of shape (n_files, n_files)
    """

    video_unit = video / np.linalg.norm(video, ord=2, axis=1, keepdims=True)            # Convert videos to unit vectors
    video_distances = 1 - video_unit @ video_unit.T                                     # Calculate cosine distance among videos
    return video_distances < thresh                                                     # Using 0.0001 distance as threshold to call it a duplicate video


# Find videos with same number of frames
def find_duplicate_frames(n_frames):
    m = n_frames.shape[0]
    frame_duplicates = n_frames.reshape(1, -1).repeat(m, 0) - n_frames.reshape(-1, 1)   # N, N  -  N, N  =  N, N
    frame_duplicates = frame_duplicates == 0                                            # Idenitfy where number of frames are the same
    return frame_duplicates


def check_folder(folder, compare_size):
    """
    Function for reading all the files inside the folder and comparing them.

    Parameters:
        folder       (directory_path) : Path to the folder that needs to be checked.
        compare_size (int)            : The first frame will be resized to this size for comparison. 
                                        Higher consumes memory and Low can lead to inaccurate results. 
                                        300 is a good spot which means every image will be resized to 300 X 300.
    Returns:
        array of the file path that are duplicate.
    """

    print("Checking folder → " + folder)
    files = os.listdir(folder)                                                                  # Get all files in a folder
    files.sort()

    videos_name = []
    all_videos = []
    all_videos_length = []
    to_delete = []

    # Read all videos in the folder
    time.sleep(0.1)  # Otherwise TQDM's output are messed up
    for file_name in tqdm(files):
        extension_match = [extension in file_name.lower() for extension in video_extensions]    # Filter file extensions to limit scope
        if any(extension_match):
            # Try to read each file as a video
            try:  
                video = cv2.VideoCapture(os.path.join(folder, file_name))                       # Read video
                success, first_image = video.read()                                             # Get the first frame
                if first_image is not None:
                    video_length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))                     # Get number of frames in the video

                    if video_length > 1:                                                        # Must have more than 1 frame to be a video
                        first_image = cv2.cvtColor(first_image, cv2.COLOR_BGR2GRAY)             # Compatibility conversion
                        first_image = Image.fromarray(first_image).convert('L')                 # Convert to grayscale after reading
                        first_image = first_image.resize((compare_size, compare_size))          # Resize image to compare size
                        first_image = np.array(first_image).reshape(-1)                         # Convert 2D frame to 1D array for easier computation

                        videos_name.append(file_name)
                        all_videos.append(first_image)
                        all_videos_length.append(video_length)

            except Exception as e:
                print(f"Failed to read file {file_name} due to {e}")
    time.sleep(0.1)

    m = len(all_videos)
    print("Total videos found = " + str(m))

    if m < 2:                                                                           # Duplicates not possible if the number of videos are 0 or 1.
        print()
        return to_delete                                                                # Return empty array

    # Combine video arrays together and flag duplicates
    all_videos = np.stack(all_videos)
    print(f"Finding duplicate videos within the folder {folder}...")
    videos_duplicates = find_duplicates(all_videos)                                             
    
    # Combine video lengths and flag videos with same length
    all_videos_length = np.stack(all_videos_length)                                             
    frames_duplicates = find_duplicate_frames(all_videos_length)                                
    
    # Combine video level and frame level duplicates
    videos_duplicates = np.logical_and(videos_duplicates, frames_duplicates)

    def video_size(video):
        """
        Function to get file size to decide which video to keep

        Parameters:
            video : index of video

        Returns:
            file size
        """
        return os.path.getsize(os.path.join(folder, videos_name[video]))

    # Collect all flagged duplicates and decide which files to keep.
    visited = [False] * m                                                               # To avoid unnecessary calls to duplicate videos
    files_duplicates = []                                                               # Store duplicates for each file
    for i in tqdm(range(m)):
        if visited[i]:
            continue
        visited[i] = True

        video_duplicates = videos_duplicates[i]                                         # Get files with duplicates flags for the current file
        if sum(video_duplicates) > 1:                                                   # If more than 1 file similar to the current file (including current file)
            duplicate_idx = np.where(video_duplicates)[0].tolist()                      # Get indexes of all duplicate videos
            duplicate_idx.sort(key=video_size, reverse=args.keep_largest == 1)          # Sort the list based on their size, Reverse is set based on which file size is preferred.
            
            for j, idx in enumerate(duplicate_idx):                                     
                visited[idx] = True                                                     # Set visited of duplicate videos to True to avoid unnecessary calls
                if j > 0:
                    to_delete.append(os.path.join(folder, images_name[idx]))            # Add all duplicate files for deletion except the prefered first file
            files_duplicates.append(duplicate_idx)
    time.sleep(0.1)

    # Display all duplicate files within the folder.
    if len(files_duplicates) > 0:
        print("\nDuplicates:")
        for i in range(len(files_duplicates)):
            for j in range(len(files_duplicates[i])):
                print(videos_name[files_duplicates[i][j]], end="\t")
            
            print()
    else:
        print("No duplicates found.")
    print()

    return to_delete


def main(args):
    print(f"Folder to be explored: {args.folder}\n\n")

    folders = [folder[0] for folder in os.walk(args.folder)]                            # Find all folders to be searched recursively
    folders.sort()

    all_deletes = []                                                                    # Stores all files to deleted
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
    parser = argparse.ArgumentParser(description='find-exact-duplicate-videos')
    parser.add_argument('--folder',       type=str, default=".", help='Directory of videos. Default is current directory.')
    parser.add_argument('--keep_largest', type=int, default=0,   help='0: keeps the smallest file among duplicates; 1: keeps the largest file among duplicates')
    parser.add_argument('--compare_size', type=int, default=300, help='Size used for comparison. Found 300 to be best for performance and results.')
    args = parser.parse_args()

    main(args)
