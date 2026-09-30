import os
import os.path
import shutil
import subprocess

# Set the path to the folder you want to organize
path = r"c:\Users\mindf\OneDrive\Projects\mindful-learning-academy\sapient-ai\classwork\day-02\automation"

# Change the current working directory to the specified path
os.chdir(path)

# Get a list of all files in the folder
files = os.listdir(path)

# Create a set of unique file extensions in the folder
exts = set([os.path.splitext(f)[1] for f in files])

# Create a folder for each unique file extension
for ext in exts:
    os.mkdir(ext[1:])

# Move each file to the corresponding folder based on its extension
for f in files:
    if os.path.isfile(f):
        ext = os.path.splitext(f)[1]
        shutil.move(f, ext[1:] + '\\' + f)  

print('Files organized successfully!')