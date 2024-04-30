import numpy as np
from cv2 import imdecode, imencode, cvtColor, IMREAD_UNCHANGED, COLOR_BGR2BGRA
from os import path, listdir


def crop_by_alpha(img_path):
    
    # 检查文件是否存在
    img = file_exist(img_path)
    # 不存在则跳过
    if len(img) == 0:
        return np.zeros((0, 0, 3), dtype=np.uint8), [], []
    # 若文件无透明通道，则添加一个全部都为不透明的透明通道
    if img.shape[2] == 3:
        img = cvtColor(img, COLOR_BGR2BGRA)
        alpha_channel = 255 * np.ones_like(img[:, :, 0], dtype=np.uint8)
        img[:, :, 3] = alpha_channel

    ini_size = img.shape
    bottom = 0
    top = row = ini_size[0]
    left = 0
    right = col = ini_size[1]

    for i in np.arange(0, row, 1):
        if img[i, :, 3].sum() != 0:
            bottom = max(bottom, i)
            break
    for i in np.arange(row - 1, -1, -1):
        if img[i, :, 3].sum() != 0:
            top = min(top, i)
            break
    for j in np.arange(0, col, 1):
        if img[:, j, 3].sum() != 0:
            left = max(left, j)
            break
    for j in np.arange(col - 1, -1, -1):
        if img[:, j, 3].sum() != 0:
            right = min(right, j)
            break

    cropped_img = img[bottom:top+1, left:right+1]
    return cropped_img, ini_size, cropped_img.shape


def crop_by_white(img_path):
    
    # 检查文件是否存在
    img = file_exist(img_path)
    # 不存在则跳过
    if len(img) == 0:
        return np.zeros((0, 0, 3), dtype=np.uint8), [], []
    # 若文件无透明通道，则添加一个全部都为不透明的透明通道
    if img.shape[2] == 3:
        img = cvtColor(img, COLOR_BGR2BGRA)
        alpha_channel = 255 * np.ones_like(img[:, :, 0], dtype=np.uint8)
        img[:, :, 3] = alpha_channel
    # 将完全透明的像素的 rgb 改为黑色，防止在白色模式下透明边界被裁剪
    img[np.where(img[:, :, 3] == 0)] = [0, 0, 0, 0]

    ini_size = img.shape
    bottom = 0
    top = row = ini_size[0]
    left = 0
    right = col = ini_size[1]

    # for channel in range(img.shape[2]):
    #     for i in np.arange(0, row, 1):
    #         if img[i, :, channel].sum() != img.shape[1] * 255:
    #             bottom = max(bottom, i)
    #             break
    #     for i in np.arange(row - 1, -1, -1):
    #         if img[i, :, channel].sum() != img.shape[1] * 255:
    #             top = min(top, i)
    #             break
    #     for j in np.arange(0, col, 1):
    #         if img[:, j, channel].sum() != img.shape[0] * 255:
    #             left = max(left, j)
    #             break
    #     for j in np.arange(col - 1, -1, -1):
    #         if img[:, j, channel].sum() != img.shape[0] * 255:
    #             right = min(right, j)
    #             break

    for i in np.arange(0, row, 1):
        if img[i, :, 0].sum() != img.shape[1] * 255 or \
        img[i, :, 1].sum() != img.shape[1] * 255 or \
        img[i, :, 2].sum() != img.shape[1] * 255 or \
        img[i, :, 3].sum() != img.shape[1] * 255:
            bottom = max(bottom, i)
            break

    for i in np.arange(row - 1, -1, -1):
        if img[i, :, 0].sum() != img.shape[1] * 255 or \
        img[i, :, 1].sum() != img.shape[1] * 255 or \
        img[i, :, 2].sum() != img.shape[1] * 255 or \
        img[i, :, 3].sum() != img.shape[1] * 255:
            top = min(top, i)
            break

    for j in np.arange(0, col, 1):
        if img[:, j, 0].sum() != img.shape[0] * 255 or \
        img[:, j, 1].sum() != img.shape[0] * 255 or \
        img[:, j, 2].sum() != img.shape[0] * 255 or \
        img[:, j, 3].sum() != img.shape[0] * 255:
            left = max(left, j)
            break

    for j in np.arange(col - 1, -1, -1):
        if img[:, j, 0].sum() != img.shape[0] * 255 or \
        img[:, j, 1].sum() != img.shape[0] * 255 or \
        img[:, j, 2].sum() != img.shape[0] * 255 or \
        img[:, j, 3].sum() != img.shape[0] * 255:
            right = min(right, j)
            break
    

    cropped_img = img[bottom:top+1, left:right+1]
    return cropped_img, ini_size, cropped_img.shape


# 读取图片
def file_read(folder_path):

    image_paths = []
    for filename in listdir(folder_path):
        # 检查文件是否为图片文件
        if filename.endswith(('.png', '.PNG', '.jpg', '.JPG', '.jpeg', '.JPEG')):
            image_paths.append(path.join(folder_path + '/', filename))
    return image_paths


# 保存图片
def file_save(cropped_img, output_path, temp_name):
    
    imencode(ext='.png', img=cropped_img)[1].tofile(output_path + '/' + temp_name + '.png')


# 检查处理图片是否存在
def file_exist(img_path):
    try:
        img_data = np.fromfile(file=img_path, dtype=np.uint8)
        img = imdecode(img_data, IMREAD_UNCHANGED)
        return img
    except FileNotFoundError:
        return np.zeros((0, 0, 3), dtype=np.uint8)