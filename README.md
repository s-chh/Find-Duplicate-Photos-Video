# Duplicate-Images-Photos-Videos-Finder
Find and display all the exact duplicate images and videos in a folder and delete them (optional). <br>
Begins search at the root folder. Repeats it for all sub-directories as well. <br>


## Run commands: <br>
<table>
  <tr>
    <th>Type</th>
    <th>Run command</th>
  </tr>
  <tr>
    <td>Images</td>
    <td>python images_duplicate_exact.py </td>
  </tr>
  <tr>
    <td>Videos</td>
    <td>python videos_duplicate_exact.py </td>
  </tr>
</table>

Or Run "duplicate_media_exact.bat" on a Windows system to run both programs sequentially (images followed by videos).<br><br>

This program requires Python3 with numpy and tqdm libraries to function. <br>Run the following command to install the dependent libraries in the Python environment if they are not present already:
```python
pip install -r requirements.txt
```
<br>
Logic:<br>
Images are compared using pixel-wise comparison after setting them to a fixed size. <br>
Videos are compared using pixel-wise comparisons on the first frame (with a fixed size) and by matching their frame length.
