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
    video_unit = video / np.linalg.norm(video, ord=2, axis=1, keepdims=True)  # Convert videos to unit vectors
    video_distances = 1 - video_unit @ video_unit.T  # Calculate cosine distance among videos
    return video_distances < thresh  # Using 0.0001 distance as threshold to call it a duplicate video


# Find videos with same number of frames
def find_duplicate_frames(n_frames):
    m = n_frames.shape[0]
    frame_duplicates = n_frames.reshape(1, -1).repeat(m, 0) - n_frames.reshape(-1, 1)
    frame_duplicates = frame_duplicates == 0
    return frame_duplicates


def check_folder(folder, compare_size):
    print("Checking folder → " + folder)
    files = os.listdir(folder)  # Get all files in a folder
    files.sort()

    videos_name = []
    all_videos = []
    all_videos_length = []
    to_delete = []

    time.sleep(0.1)  # Otherwise TQDM's output are messed up
    for file_name in tqdm(files):
        extension_match = [extension in file_name.lower() for extension in video_extensions]
        if any(extension_match):
            try:  # Try to read each file as a video
                video = cv2.VideoCapture(os.path.join(folder, file_name))
                success, first_image = video.read()
                if first_image is not None:
                    video_length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                    if video_length > 1:
                        first_image = cv2.cvtColor(first_image, cv2.COLOR_BGR2GRAY)
                        first_image = Image.fromarray(first_image).convert('L')
                        first_image = first_image.resize((compare_size, compare_size))
                        first_image = np.array(first_image).reshape(-1)

                        videos_name.append(file_name)
                        all_videos.append(first_image)
                        all_videos_length.append(video_length)
            except Exception as e:
                print(f"Failed to read file {file_name} due to {e}")
    time.sleep(0.1)

    m = len(all_videos)
    print("Total videos found = " + str(m))

    if m < 2:
        print()
        return to_delete

    # Get all video arrays together and calculate distances among them
    all_videos = np.stack(all_videos)
    print(f"Finding duplicate videos within the folder {folder}...")
    videos_duplicates = find_duplicates(all_videos)
    # Videos need to have same number of frames as well.
    all_videos_length = np.stack(all_videos_length)
    frames_duplicates = find_duplicate_frames(all_videos_length)
    # Combine video level and frame level duplicates
    videos_duplicates = np.logical_and(videos_duplicates, frames_duplicates)

    def video_size(video):  # Function to get file size to decide which video to keep
        return os.path.getsize(os.path.join(folder, videos_name[video]))

    visited = [False] * m  # To avoid unnecessary calls to duplicate videos
    files_duplicates = []
    for i in tqdm(range(m)):
        if visited[i]:
            continue
        visited[i] = True
        video_duplicates = videos_duplicates[i]
        if sum(video_duplicates) > 1:
            duplicate_idx = np.where(video_duplicates)[0].tolist()  # Get indexes of all duplicate videos
            # Sort the list based on their size, Reverse is set based on which file size is preferred.
            duplicate_idx.sort(key=video_size, reverse=args.keep_largest == 1)
            for idx in duplicate_idx:  # Set visited of duplicate videos to True to avoid unnecessary calls
                visited[idx] = True
            files_duplicates.append(duplicate_idx)
    time.sleep(0.1)

    if len(files_duplicates) > 0:
        # Display all duplicate files within a folder.
        print()
        print("Duplicates:")
        for i in range(len(files_duplicates)):
            for j in range(len(files_duplicates[i])):
                print(videos_name[files_duplicates[i][j]], end="\t")
                if j > 0:
                    to_delete.append(os.path.join(folder, videos_name[files_duplicates[i][j]]))
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
    parser = argparse.ArgumentParser(description='find-exact-duplicate-videos')
    parser.add_argument('--folder', type=str, default=".", help='Directory of videos. Default is current directory.')
    parser.add_argument('--keep_largest', type=int, default=0,
                        help='0: keeps the smallest file among duplicates; 1: keeps the largest file among duplicates')
    parser.add_argument('--compare_size', type=int, default=300,
                        help='Size used for comparison. Found 300 to be best for performance and results.')
    args = parser.parse_args()

    main(args)
