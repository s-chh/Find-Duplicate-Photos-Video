# Find-Duplicate-Photos-Videos
Python code to find and display all the exact duplicate photos (images) and videos in a folder and delete them (optional). <br>
Begins search at the current folder. Repeats it for all sub-directories as well. <br><br>

## Run commands <br>
<table>
  <tr>
    <th>Type</th>
    <th>Run command</th>
  </tr>
  <tr>
    <td>Photos</td>
    <td>python duplicate_exact_photos.py</td>
  </tr>
  <tr>
    <td>Videos</td>
    <td>python duplicate_exact_videos.py </td>
  </tr>
</table>

Or Run "duplicate_media_exact.bat" on a Windows system to run both programs sequentially (photos followed by videos).<br><br>


## Run Arguments <br>
<table>
  <tr>
    <th>Argument</th>
    <th>Usage</th>
    <th>Default</th>
  </tr>
  <tr>
    <td>folder</td>
    <td>Folder to begin the search. Subfolders are included.</td>
    <td>Current path </td>
  </tr>
  <tr>
    <td>keep_largest</td>
    <td>Keep the file with the largest or smallest size among the duplicates. 1 for largest and 0 for smallest. </td>
    <td>1: Keep largest</td>
  </tr>
  <tr>
    <td>compare_size</td>
    <td>Photos are resized to this value for comparison. <br>Higher value compares more pixels but requires more RAM and runs slower. </td>
    <td>300 gives accurate and fast results.</td>
  </tr>
</table>
<br>

## Requirements <br>
This program requires Python with numpy, tqdm and CV2 libraries to function. <br>Run the following command to install the dependent libraries in the Python environment if they are not present already:
```python
pip install -r requirements.txt
```
<br>

## Finding Duplicates Logic <br>
Photos are compared using pixel-wise comparison using cosine distance after setting them to a fixed size. <br>
Videos are compared using pixel-wise comparisons using cosine distance  on the first frame (with a fixed size) and by matching their frame length.
