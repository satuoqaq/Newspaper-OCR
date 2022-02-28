"""
    检查topBar中信息
"""
import os

import cv2
import os.path as osp
import numpy as np
from tqdm import tqdm
from P0_init import conf
from P2_img_split import get_image_names
import json
import re
import matplotlib.pyplot as plt
import math
from PaddleOCR.paddleocr import PaddleOCR


def init_rec_model(use_gpu,
                   rec_model_dir,
                   rec_char_dict_path,
                   det_model_dir,
                   cls_model_dir):
    text_recognizer = PaddleOCR(det_model_dir=det_model_dir,
                                rec_model_dir=rec_model_dir,
                                cls_model_dir=cls_model_dir,
                                rec_char_dict_path=rec_char_dict_path,
                                use_gpu=use_gpu,
                                show_log=False)
    return text_recognizer


def page_enhance(xin):
    img_h, img_w = xin.shape[:2]
    try:
        img_c = xin.shape[2]
    except IndexError:
        img_c = 1
    # print(img_h, img_w, img_c)
    r = int(math.sqrt(float(img_w * img_h)) / 32.0) + 1
    fin = cv2.GaussianBlur(xin, (r + r + 1, r + r + 1), 0.0)

    xout = xin.copy()

    for j in range(img_h):
        po = xout[j]
        pf = fin[j]
        for i in range(img_w):
            if img_c == 1:
                xout[j][i] = 0 if pf[i] == 0 else min(
                    255.0, 255.0 * po[i] / pf[i])
            else:
                for ci in range(img_c):
                    xout[j][i][ci] = 0 if pf[i][ci] == 0 else min(
                        255.0, 255.0 * po[i][ci] / pf[i][ci])
    return xout


rec_model_dir = 'PaddleOCR/inference/ch_ppocr_server_v2.0_rec_infer'
rec_char_dict_path = 'ppocr/utils/ppocr_keys_v1.txt'
det_model_dir = 'PaddleOCR/model/210924_ch_ppocr_server_v2.0_infer/det'
cls_model_dir = 'PaddleOCR/model/210924_ch_ppocr_server_v2.0_infer/cls'
use_gpu = conf['use gpu']

ocr_model = init_rec_model(use_gpu, rec_model_dir, rec_char_dict_path, det_model_dir, cls_model_dir)


def get_topbar_data(baseRoot, specific_pages=None):
    """
    得到顶栏信息（页码、批次）
    :param image_root_dict:
    :param specific_pages:
    """
    image_root_dict = os.path.join(baseRoot, 'HP_roa_split/uppers')
    img_names = get_image_names(image_root_dict, specific_pages)
    page_infos = {}
    for img_name in tqdm(img_names):
        img_path = osp.join(image_root_dict, img_name)

        ori_img = cv2.imread(img_path, 0)

        page_number, class_info = check_page_data(ori_img)
        tqdm.write('{}> page{},{}'.format(img_name, page_number, class_info))
        page_infos[img_name] = {'page_number': page_number,
                                'class_info': class_info}
    page_infos = recheck_page_number(page_infos)
    page_infos = recheck_page_infos(page_infos)

    json_page_msg = os.path.join(baseRoot, 'json/page_msg.json')
    with open(json_page_msg, 'w', encoding='utf-8') as f:
        f.write(json.dumps(page_infos, indent=4, ensure_ascii=False))

    # with open(osp.join(image_root_dict, 'page_infos.json'), 'r', encoding='utf-8') as f:
    #     page_infos = json.load(f)


def recheck_page_infos(page_infos):
    """
    重新对info dict进行整理，检查并订正错误的clas_info项
    遍历每一页，若当前页的前后页具有相同info，则当前页也应具有相同info
    :param page_infos:
    :return: dict
    """
    infos_per_page = {value['page_number']: value['class_info'] for key, value in page_infos.items()}
    page_numbers = sorted(infos_per_page)
    for p_idx in page_numbers:
        if p_idx == -1:
            continue
        l_idx = p_idx - 1
        r_idx = p_idx + 1
        try:
            if infos_per_page[l_idx] == infos_per_page[r_idx]:
                infos_per_page[p_idx] = infos_per_page[l_idx]
        except KeyError:
            continue
    new_infos = {}
    for key, page_item in page_infos.items():
        p_idx = page_item['page_number']
        if p_idx == -1:
            new_infos[key] = page_item
            continue
        info = page_item['class_info']
        if infos_per_page[p_idx] != page_item['class_info']:
            info = infos_per_page[p_idx]
        new_infos[key] = dict(page_number=p_idx, class_info=info)
    return new_infos


def recheck_page_number(page_infos):
    """
    重新对info dict进行整理，检查并订正错误的page_number项
    遍历每一页，若当前页的前后页page_number间隔1，则当前页的page_number为两者之间
    !!使用前提是文件命名顺序正确!!
    :param page_infos:
    :return:
    """
    img_names = list(page_infos.keys())
    for idx, img_name in enumerate(img_names):
        page_number = page_infos[img_name]['page_number']
        if page_number != -1:
            continue
        img_num = int(img_name[:-4])
        try:
            l_img_num = int(img_names[idx - 1][:-4])
            r_img_num = int(img_names[idx + 1][:-4])
            l_info = page_infos[img_names[idx - 1]]['class_info']
            r_info = page_infos[img_names[idx + 1]]['class_info']
            l_page_number = page_infos[img_names[idx - 1]]['page_number']
            r_page_number = page_infos[img_names[idx + 1]]['page_number']
        except IndexError:
            continue
        if not (l_img_num + 1 == img_num == r_img_num - 1):
            continue
        if not (l_page_number + 2 == r_page_number):
            continue
        if l_info == r_info:
            page_infos[img_name]['page_number'] = l_page_number + 1
            page_infos[img_name]['class_info'] = l_info
    return page_infos


def check_page_data(ori_img):
    """
    分析传入图片并得到页码和批次信息
    :param ori_img:
    :return: int, str
    """
    img_h, img_w = ori_img.shape[:2]

    if img_h < 1000:
        page_number, class_info = get_default_topbar_data(ori_img)
    else:
        page_number, class_info = get_title_topbar_data(ori_img)

    return page_number, class_info


def get_default_topbar_data(ori_img):
    """
    针对默认顶栏类型，获取其中信息（页码、批次）
    :ori_img 裁剪后的topbar图片
    :return: 页码, 批次
    """
    ret, binary_img = cv2.threshold(ori_img, 200, 255, cv2.THRESH_BINARY)

    left_bin_img = binary_img[:, :300]
    right_bin_img = binary_img[:, -300:]

    left_sum = sum(map(sum, left_bin_img))
    right_sum = sum(map(sum, right_bin_img))

    if left_sum > right_sum:
        # 页码在右侧
        page_number_img = ori_img[:, -300:]
        class_info_img = ori_img[:, -3000:-300]
    else:
        # 页码在左侧
        page_number_img = ori_img[:, :300]
        class_info_img = ori_img[:, 300:3000]

    page_number = get_default_pagenumber(page_number_img)
    class_info = get_default_classinfo(class_info_img)

    return page_number, class_info


def get_default_classinfo(class_info_img):
    """
    针对默认顶栏中的批次信息图片，进行处理并ocr得到批次
    :param class_info_img:
    :return: 批次信息str
    """
    class_info_img = page_enhance(class_info_img[:-20, :])
    ret, class_info_img = cv2.threshold(class_info_img, 200, 255, cv2.THRESH_BINARY)
    class_info_img = cv2.medianBlur(class_info_img, 3)
    class_info_h, class_info_w = class_info_img.shape[:2]

    # 每列求和
    rows_sum = np.sum(class_info_img, axis=0)
    rows_sum = list(map(lambda x: x / 255, rows_sum))
    # 分别从前向后和从后向前找连续0的开始,即页码框部分 （0-黑 1-白）
    flag_front, flag_behind = 0, 0
    start_idx, end_idx = 0, 0
    for idx in range(class_info_w):
        flag_front = flag_front + 1 if rows_sum[idx] < (class_info_h - 10) and not start_idx else 0
        flag_behind = flag_behind + 1 if rows_sum[-idx] < (class_info_h - 10) and not end_idx else 0
        if flag_front >= 2:
            start_idx = idx
        if flag_behind > 2:
            end_idx = idx
        if start_idx and end_idx:
            break
    class_info_img = class_info_img[:, start_idx:class_info_w - end_idx]

    ocr_results = ocr_model.ocr(class_info_img, det=False, cls=False)
    ocr_results = sorted(ocr_results, key=lambda x: x[-1], reverse=True)  # 按置信度降序排列
    try:
        result_text = ocr_results[0][0]
        result_text = result_text[result_text.index('专刊') + 2:]
    except IndexError:
        result_text = ''
    except ValueError:
        print('{} not contains \"专刊\"!'.format(result_text))

    class_info = result_text
    # 利用正则匹配取出批次信息
    # ^[,;.:．\"\'·]*([\u4e00-\u9fa5].*[\u4e00-\u9fa5])[,;.:．\"\'·]*$
    # ^[^\u4e00-\u9fa5]*([\u4e00-\u9fa5].*[\u4e00-\u9fa5])[^0-9\u4e00-\u9fa5]*$
    info_pattern = "^[^\u4e00-\u9fa5]*([\u4e00-\u9fa5].*[\u4e00-\u9fa5])[^0-9\u4e00-\u9fa5]*$"
    class_pattern = '[\u4e00-\u9fa5].*[\u4e00-\u9fa5]'
    if re.match(info_pattern, class_info) is not None:
        class_info = re.search(class_pattern, class_info)[0]

    return class_info


def get_default_pagenumber(page_number_img):
    """
    针对默认顶栏中的页码图片，进行处理并ocr得到页码数字
    :param page_number_img: 粗略裁剪的页码位置图片
    :return: 页码数字
    """
    page_number_img = page_enhance(page_number_img[:-20, :])
    ret, page_number_img = cv2.threshold(page_number_img, 200, 255, cv2.THRESH_BINARY)
    page_number_img = cv2.erode(page_number_img, np.ones((5, 5), np.uint8))
    page_number_img = cv2.medianBlur(page_number_img, 3)
    page_number_h, page_number_w = page_number_img.shape[:2]
    rows_sum = np.sum(page_number_img, axis=0)
    rows_sum = list(map(lambda x: x / 255, rows_sum))
    # 分别从前向后和从后向前找连续0的开始,即页码框部分 （0-黑 1-白）
    flag_front, flag_behind = 0, 0
    start_idx, end_idx = 0, 0
    for idx in range(page_number_w):
        flag_front = flag_front + 1 if rows_sum[idx] == 0 and not start_idx else 0
        flag_behind = flag_behind + 1 if rows_sum[-idx] == 0 and not end_idx else 0
        if flag_front >= 2:
            start_idx = idx
        if flag_behind >= 2:
            end_idx = idx
        if start_idx and end_idx:
            break
    page_number_img = page_number_img[:, start_idx:page_number_w - end_idx]
    page_number_img = cv2.dilate(page_number_img, np.ones((3, 3), np.uint8))
    # plt.imshow(page_number_img)
    # plt.axis('off')
    # plt.show()
    ocr_results = ocr_model.ocr(page_number_img, det=True, cls=False)
    ocr_results = sorted(ocr_results, key=lambda x: x[-1], reverse=True)  # 按置信度降序排列
    try:
        result = eval(ocr_results[0][1][0])
    except IndexError:
        result = -1

    # cv2.imshow('pagenumber', page_number_img)
    return result


def get_title_topbar_data(ori_img):
    """
    针对封面标题顶栏类型，获取其中信息（页码、批次）
    :param ori_img: 裁剪后的topbar图片
    :return: 页码, 批次
    """
    bar_top_pos = 985
    bar_height = 100
    bar_left_pos = 585
    bar_width = 2500

    bar_img = ori_img[bar_top_pos:bar_top_pos + bar_height, bar_left_pos:bar_left_pos + bar_width]
    bar_img = page_enhance(bar_img)
    bar_h, bar_w = bar_img.shape[:2]

    ret, bar_img = cv2.threshold(bar_img, 200, 255, cv2.THRESH_BINARY)
    bar_img = cv2.medianBlur(bar_img, 3)

    # 每列求和
    rows_sum = np.sum(bar_img, axis=0)
    rows_sum = list(map(lambda x: x / 255, rows_sum))
    flag_behind, end_idx = 0, 0
    for idx in range(bar_w):
        flag_behind = flag_behind + 1 if rows_sum[-idx] > bar_h * 2 else 0
        if flag_behind >= 2:
            end_idx = idx
            break
    bar_img = bar_img[:, :bar_w - end_idx]

    ocr_results = ocr_model.ocr(bar_img, det=False, cls=False)
    ocr_results = sorted(ocr_results, key=lambda x: x[-1], reverse=True)  # 按置信度降序排列
    try:
        result_text = ocr_results[0][0]
        result_text = result_text[result_text.index('专刊') + 2:]
    except IndexError:
        return -1, ''
    except ValueError:
        print('\"{}\" not contains \"专刊\"!'.format(result_text))

    page_number = -1
    class_info = result_text
    # 正则表达式匹配，若符合则取出
    # ^[，,;.:．\"\'·]*([\u4e00-\u9fa5].*[\u4e00-\u9fa5])[，,;.:．\"\'·]*[0-9]{1,3}[,;.:．\"\'·】\]》]*$
    # ^[^\u4e00-\u9fa5]*([\u4e00-\u9fa5].*[\u4e00-\u9fa5])[^0-9\u4e00-\u9fa5]*[0-9]{1,3}[^0-9\u4e00-\u9fa5]*$
    info_pattern = "^[^\u4e00-\u9fa5]*([\u4e00-\u9fa5].*[\u4e00-\u9fa5])" \
                   "[^0-9\u4e00-\u9fa5]*[0-9]{1,3}[^0-9\u4e00-\u9fa5]*$"
    number_pattern = '[0-9]{1,3}'
    class_pattern = '[\u4e00-\u9fa5].*[\u4e00-\u9fa5]'
    if re.match(info_pattern, result_text) is not None:
        page_number = eval(re.search(number_pattern, result_text)[0])
        class_info = re.search(class_pattern, result_text)[0]

    return page_number, class_info


def main():
    # get_topbar_data('PC2/HP_upper/', list(range(0, 2)))
    get_topbar_data('PC2/HP_roa_split/uppers/')


if __name__ == "__main__":
    main()
