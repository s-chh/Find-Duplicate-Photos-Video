# Duplicate-Photos-Finder
Find and delete all the duplicate images in a folder. Repeats it for all sub-directories as well. 

v2 uses 2x2 average pooling to reduce the image size. Provides faster detection time with lower memory consumption.

<br>

This code requires Python3. Run the following command to install all the dependencies:
```python
pip install -r requirements.txt
```

Use the following command to run the code: 
```python
python duplicate.py --inspection_dir "D:\Pictures\"
```
