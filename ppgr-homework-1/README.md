## PPGR_Homework_1
This repo represents my first homework for the elective course at the Faculty of Mathematics, University of Belgrade, called:
  - Application of Projective Geometry in Computing

I have implemented three algorithms for perspective mappings with a GUI for importing and correcting image distortion:
  - Naive algorithm
  - Direct Linear Transform (DLT) algorithm
  - Normalized DLT algorithm


### Requirements and running
Software: python3  
Libraries: pyqt5, PIL, Pillow

```sh
$  pip install -r requirements.txt
$. python3 main.py
```

#### Files explanation  
There are three options for testing my homework.  
  1. running file: ppgr_homework1.py with python3
  2. running file: ppgr_homework1.ipynb with jupyter notebook
  3. running file: main.py with python3 where I have implemented simple GUI

#### Explaining option 3 with GUI
  - Insert how many points you want to select on image, lets say N
  - Import random image by clicking on the button or in File->Open Image
  - Mark N points on the original image and N projected points on the black image
  - Choose witch algorithm you want to use for fixing the image distortion