"""
    报纸图片板块切分
"""
import json
import cv2
import numpy as np
import os.path as osp
import os
from tqdm import tqdm
import re


TopBarHeight = 185
TopTitleHeight = 1290
BottomBarHeight = 125
RowWidth = 1915


def get_image_names(image_root_dict, specific_pages, img_type='.jpg'):
    """
    从指定路径中，取出符合img_type后缀的图片，可利用specific_pages指定具体页
    :param image_root_dict: str
    :param specific_pages: None or [int*]
    :param img_type: str
    :return:
    """
    img_names = []
    specific_basics = []

    if specific_pages:
        # 若有指定页码，则生成指定的基础文件前缀
        for idx in specific_pages:
            basic_name = str(idx).rjust(4, '0')
            specific_basics.append(basic_name)

    img_list = os.listdir(image_root_dict)
    img_list.sort(key=lambda x: int(re.findall(r"\d+", x)[0]))
    for img_name in img_list:
        if not img_name.endswith(img_type):
            continue
        img_names.append(img_name)

    return img_names


def get_com_line(baseRoot, image_root_dict, target_root_dict, specific_pages=None):
    """
    对图片内容分块, 上、左、中、右、下
    :image_root_dict: str
    :target_root_dict: str
    :specific_pages: [int*]
    """
    if not osp.isdir(image_root_dict):
        print('{} is not exists!'.format(image_root_dict))
        exit(-1)
    if not osp.isdir(target_root_dict):
        os.mkdir(target_root_dict)
        print('{} has been created automatically'.format(target_root_dict))

    img_names = get_image_names(image_root_dict, specific_pages)

    print('detecting split position lines...')
    img_split_position_dict = get_split_positions(image_root_dict, img_names)

    # 写入json文件

    dict_path = os.path.join(baseRoot, 'json/split_positions.json')
    with open(dict_path, 'w') as f:
        f.write(json.dumps(img_split_position_dict, indent=4))

    # # 读取json文件
    with open(dict_path, 'r') as f:
        img_split_position_dict = json.load(f)

    print('spliting images...')
    get_split_images(image_root_dict, target_root_dict,
                     img_names, img_split_position_dict)

    return img_split_position_dict


def get_split_images(image_root_dict, target_root_dict, img_names, img_split_positions):
    """
    利用获得的每页板块位置边距信息，分割图片并存储到target_dict
    """
    if not os.path.exists(osp.join(target_root_dict, 'uppers')):
        os.mkdir(osp.join(target_root_dict, 'uppers'))
    if not os.path.exists(osp.join(target_root_dict, 'downs')):
        os.mkdir(osp.join(target_root_dict, 'downs'))

    for img_name in tqdm(img_names):
        img_path = osp.join(image_root_dict, img_name)
        position_dict = img_split_positions[img_name]
        upper, down, left, middle, right = split_image_position(
            img_path, position_dict)

        target_path = osp.join(target_root_dict, img_name)

        cv2.imwrite(osp.join(target_root_dict, 'uppers', img_name), upper)
        cv2.imwrite(osp.join(target_root_dict, 'downs', img_name), down)
        cv2.imwrite(target_path.replace('.jpg', '_1.jpg'), left)
        cv2.imwrite(target_path.replace('.jpg', '_2.jpg'), middle)
        cv2.imwrite(target_path.replace('.jpg', '_3.jpg'), right)


def split_image_position(image_path, position_dict):
    """
    针对单张图片进行分割
    """
    ori_img = cv2.imread(image_path)
    h, w = ori_img.shape[:2]
    upper_pos = position_dict['upper_pos']
    down_pos = position_dict['down_pos']
    left_pos = position_dict['left_pos']
    right_pos = position_dict['right_pos']

    row_width = RowWidth
    left_border = left_pos - row_width
    left_border = 0 if left_border < 0 else left_border
    right_border = right_pos + row_width
    upper_border = upper_pos - TopBarHeight
    down_border = h

    if position_dict['layout'] == 'cover':
        upper_border = upper_pos - TopTitleHeight
        down_border = down_pos + BottomBarHeight
    elif position_dict['layout'] == 'backcover':
        down_border = down_pos + BottomBarHeight

    upper_image = ori_img[upper_border:upper_pos, left_border:right_border]
    down_image = ori_img[down_pos:down_border, left_border:right_border]

    left_image = ori_img[upper_pos:down_pos, left_border:left_pos]
    right_image = ori_img[upper_pos:down_pos, right_pos:right_border]
    middle_image = ori_img[upper_pos:down_pos, left_pos:right_pos]

    return upper_image, down_image, left_image, middle_image, right_image


def get_split_positions(image_root_dict, img_names):
    """
    计算得到版面分割线位置
    """
    kernel = np.ones((5, 5), np.uint8)
    img_split_position_dict = {}
    for img_name in tqdm(img_names):
        img_path = osp.join(image_root_dict, img_name)
        ori_img = cv2.imread(img_path, 0)
        ret, binary_img = cv2.threshold(ori_img, 200, 255, cv2.THRESH_BINARY)
        up_pos = get_upper_split_line(binary_img, kernel)
        left_pos = get_left_split_line(binary_img, kernel)
        right_pos = get_right_split_line(binary_img, kernel)

        # 统计每一页的信息
        position_dict = {'upper_pos': up_pos,
                         'left_pos': left_pos,
                         'right_pos': right_pos}
        if up_pos > 1000:
            position_dict['down_pos'] = up_pos + 7070
            position_dict['layout'] = 'cover'
            last_img_name = str(int(img_name[:4]) - 1).zfill(4) + '.jpg'
            if img_split_position_dict.__contains__(last_img_name):
                img_split_position_dict[last_img_name]['down_pos'] = img_split_position_dict[last_img_name][
                                                                         'upper_pos'] + 8170
                img_split_position_dict[last_img_name]['layout'] = 'backcover'
        # elif up_pos > 700:
        #     position_dict['layout'] = 'ad'
        #     position_dict['down_pos'] = up_pos + 7070
        else:
            position_dict['down_pos'] = up_pos + 8300
            position_dict['layout'] = 'default'

        img_split_position_dict[img_name] = (position_dict)

    return img_split_position_dict


def get_upper_split_line(binary_img, kernel):
    img_row1 = binary_img[100:1800, 100:5000]
    img_row1 = 255 - img_row1
    # img_row11 = cv2.resize(img_row1, (int(img_row1.shape[1] * 0.3), int(img_row1.shape[0] * 0.3)))
    # cv2.imshow('img', img_row11)
    # cv2.waitKey(0)
    img_erode_0 = cv2.erode(img_row1, kernel, iterations=1)
    y_sum = np.sum(img_erode_0, axis=1)
    pos0 = int(np.argmax(y_sum))
    up_pos = pos0 + 100
    return up_pos


def get_left_split_line(binary_img, kernel):
    img_line1 = binary_img[1500:3000, 1900:2300]
    img_erode_1 = cv2.erode(img_line1, kernel, iterations=2)
    x_sum1 = np.sum(img_erode_1, axis=0)
    pos1 = int(np.argmin(x_sum1))
    left_pos = pos1 + 1900
    return left_pos


def get_right_split_line(binary_img, kernel):
    img_line2 = binary_img[1500:3000, 3850:4280]
    img_erode_2 = cv2.erode(img_line2, kernel, iterations=2)
    x_sum2 = np.sum(img_erode_2, axis=0)
    pos2 = int(np.argmin(x_sum2))
    right_pos = pos2 + 3850
    return right_pos


def main():
    get_com_line('PC/HP_roa', 'PC/HP_roa_split')


if __name__ == "__main__":
    main()
