# Image_Edges_Cropper
A tool to crop batch images with transparent or white edges.

<img src="ProgramInterface_en.png" width="900px">

* Input folder: The program will read image files with the extensions ".png", ".jpg", or ".jpeg" directly contained in the selected input folder. Files in subfolders will not be read.

* Output folder: If no output folder is specified, the program will create an "output" folder within the input folder to store processed files.

* Cropping mode: "Transparent" will only crop edges with an alpha channel value of 0, while "White" will only crop edges where all RGB alpha channel values are 255.

* Start and cease: You can also pause or resume the program while running.

<img src="Diagram.png" width="700px">

Read this in other languages: zn_CN [Chinese](README.zh_CN.md)
