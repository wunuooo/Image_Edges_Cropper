# Image_Edges_Cropper
一个可以批量裁剪图片透明或白色边缘的工具。

<img src="ProgramInterface_zh_CN.png" width="900px">

* 输入文件夹：程序会读取所选输入文件夹直接包含的，后缀为「.png」「.jpg」「.jpeg」的图片文件，子文件夹下的文件将不会被读取。

* 输出文件夹：若未指定输出文件夹，程序会在输入文件夹下创建一个「output」文件夹以存放处理后的文件。

* 「透明边缘」仅裁剪 α 通道为0的边缘，「白色边缘」仅裁剪 rgbα 通道都为255的边缘。

* 启动与终止：运行程序或结束程序，可中途暂停或继续。

<img src="Diagram.png" width="700px">

英文介绍版本：en [English](README.md)
