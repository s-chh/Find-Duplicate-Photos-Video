# Duplicate-Photos-Finder
Find all the duplicate images in a folder by pixel-wise comparison and deletes them. Repeats it for all sub-directories as well. 
<br>

v2 uses 2x2 average pooling to reduce the image size. Provides faster execution and lowers memory consumption.

<br>

This code requires Python3. Run the following command to install all the dependencies:
```python
pip install -r requirements.txt
```

Use the following command to run the code: 
```python
python duplicate.py --inspection_folder "D:\Pictures\"
```
