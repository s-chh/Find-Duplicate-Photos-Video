import os
import numpy as np
import time
import itertools
from PIL import Image
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(description='find-duplicate-images')
parser.add_argument('--inspection_folder', type=str, default="", required=True, help='Directory of images.')
args = parser.parse_args()

inspection_folder = args.inspection_folder
print ("Inspection folder: " + str(inspection_folder))

folders = [x[0] for x in os.walk(inspection_folder)]

COMPARE_SIZE = 300

to_delete = []

def check_folder(folder):
	print("Checking Folder -> " + folder)
	files = os.listdir(folder)
	files.sort()
	m = len(files)

	images = []
	images_name = []
	time.sleep(1)
	for i in tqdm(range(m)):
		try:
			img = Image.open(os.path.join(folder, files[i])).convert('RGB')
			if img is not None:
				img = img.resize((COMPARE_SIZE, COMPARE_SIZE))
				img = np.array(img)
				images.append(img)
				images_name.append(files[i])
		except:
			pass
	time.sleep(1)

	images = np.array(images)
	m = images.shape[0]
	print("Images Read. Total images = " + str(m))

	if m == 0:
		print()
		return

	print("Finding duplicates now...")
	time.sleep(1)
	im_duplicates = []
	for i in tqdm(range(m)):
		diff = images - images[i]
		diff = diff.mean(axis=(1,2,3))
		duplicates = diff == 0
		duplicates[i] = False
		idx = np.where(duplicates)[0]
		if idx.size > 0:
			im_duplicate = list()
			im_duplicate.append(i)
			for j in range(idx.shape[0]):
				im_duplicate.append(idx[j])
			im_duplicate.sort()
			im_duplicates.append(im_duplicate)
	time.sleep(1)
	im_duplicates.sort()
	im_duplicates = list(im_duplicates for im_duplicates, _ in itertools.groupby(im_duplicates))

	if len(im_duplicates) > 0:
		print()
		print("Duplicates:")
		for i in range(len(im_duplicates)):
			for j in range(len(im_duplicates[i])):
				print(images_name[im_duplicates[i][j]], end="\t")
				if j>0:
					to_delete.append(os.path.join(folder, images_name[im_duplicates[i][j]]))
			print()
	else:
		print("No duplicates found.")
	print()

for folder in folders:
	check_folder(folder)

print('-----------------------------Overall Report----------------------------------')

if len(to_delete) == 0:
	print("No duplicates found.")
	exit()

print("\nFiles marked for delete:")
for file in to_delete:
	print(file)
print("Print Y to delete")
inp = input()
if inp == 'Y':
	for file in to_delete:
		os.remove(file)
	print("Done.")
else:
	print("Files not deleted.")