import copy
import math
import os
import time

from PaddleOCR.paddleocr import PaddleOCR
from P5_get_topBarMsg import ocr_model
from tqdm import tqdm
import json
import cv2 as cv
import re
from P5_get_box import get_img_box
import numpy as np
import os
from P0_init import conf

# openRoaImgPath = 'PC/HP_roa'
# saveJsonPath = 'json/box.json'
# saveImgPath = 'PC/HP_box'
IsSave = True


# 定义模型
# def init_rec_model(use_gpu, rec_model_dir, rec_char_dict_path, det_model_dir, cls_model_dir):
#     text_recognizer = PaddleOCR(det_model_dir=det_model_dir,
#                                 rec_model_dir=rec_model_dir,
#                                 cls_model_dir=cls_model_dir,
#                                 rec_char_dict_path=rec_char_dict_path,
#                                 use_gpu=conf['use gpu'])
#     return text_recognizer


# 设置只进行识别的ocr模型
def text_recognize(img, rec_model):
    try:
        rec_res = rec_model.ocr(img, det=False, cls=False)  # only recognize
        return rec_res
    except Exception as E:
        print('error in text recognize')
        exit()


# 对固定位置的为学费的box进行数字调整
def num_fix(num_text):
    if num_text.find('免费') != -1:
        return '免费'
    elif num_text.find('待定') != -1:
        return '待定'
    num_list = re.findall(r"\d+", num_text)
    new_text = ''
    if len(num_list) > 0:
        new_text = num_list[0]
    return new_text


def getBoxAndRecognize(baseRoot, imgRoot, img_save_path):
    """
           对文件夹下所有的图片 进行分割识别
           1. 分割: 先通过之前的
           首先使用 P5_get_box.py 使用传统像素累加对每一个栏
           :param imageRoot: 图片打开路径 str
           :param savePath: 图片储存路径 str
    """
    model = ocr_model

    # 打开之前得到的分栏位置,对图片进行分栏
    json_split_name = os.path.join(baseRoot, 'json/split_positions.json')
    with open(json_split_name, 'r')as fp:
        page_data = json.load(fp)

    # 储存结果
    boxAnswerDict = {}

    imgNameList = os.listdir(imgRoot)
    startPage, endPage = 0, len(imgNameList)

    # 对所有图片一页一页进行识别
    t = time.time()
    for pageNum in range(0, endPage):
        # 取出图片
        imgName = str(pageNum).zfill(4) + '.jpg'
        imgPath = os.path.join(imgRoot, imgName)
        img = cv.imread(imgPath, 0)

        # 取出分栏信息
        posMsg = page_data[imgName]
        up_pos = posMsg['upper_pos']
        down_pos = posMsg['down_pos']
        left_pos = posMsg['left_pos']
        right_pos = posMsg['right_pos']
        len_width = right_pos - left_pos

        # 分别分割左中右三栏图片进行识别,将结果存入box列表中

        # 左栏,要将分割的位置稍微调整,防止将分栏的线也划进去
        # 得到文字的框之后还有对框进行微调
        img1 = img[up_pos + 10:down_pos, max(1, left_pos - len_width + 20): left_pos - 30]
        box1 = get_img_box(img1)
        box1[:, 0:2] += up_pos + 5
        box1[:, 2:] += max(1, left_pos - len_width + 20)
        box1[:, 0] -= 3
        box1[:, 1] += 3

        # 中栏
        img2 = img[up_pos + 10:down_pos, left_pos + 30: right_pos - 30]
        box2 = get_img_box(img2)
        box2[:, 0:2] += up_pos + 5
        box2[:, 2:] += left_pos + 30
        box2[:, 0] -= 3
        box2[:, 1] += 3

        # 右栏
        img3 = img[up_pos + 10:down_pos, right_pos + 30: right_pos + len_width]
        box3 = get_img_box(img3)
        box3[:, 0:2] += up_pos + 5
        box3[:, 2:] += right_pos + 30
        box3[:, 0] -= 3
        box3[:, 1] += 3

        # 将所有框合并
        boxes = np.concatenate((box1, box2, box3), axis=0)

        # 对于每一页进行储存
        box_list = []
        img2 = img.copy()

        # 再对框框进行微调 然后记录对应的左右边距,目的是为了后续判断

        for boxNum in tqdm(range(boxes.shape[0])):
            up, down, left, right = boxes[boxNum]
            up = up - 3
            down = down + 5
            # 记录左右边距
            if boxNum < box1.shape[0]:
                l_edge = int(left_pos - len_width + 20)
                r_edge = int(left_pos - 30)
            elif box1.shape[0] <= boxNum < box1.shape[0] + box2.shape[0]:
                l_edge = int(left_pos + 30)
                r_edge = int(right_pos - 30)
            else:
                l_edge = int(right_pos + 30)
                r_edge = int(right_pos + len_width)

            # 这里是判断数字框对应的位置,如果在这个位置要将框缩小尽可能的紧贴其对应的数字,增加识别的准确率
            if left > l_edge + 1350:
                left = left + 5
                right = right - 5

            # 把所有的框拉入识别模型进行预测
            img1 = img2[up:down, left:right]
            # 对应数字的位置还要进行一次高斯滤波
            if left < l_edge + 1350:
                img1 = cv.GaussianBlur(img1, (3, 3), 0)
            # 识别
            ans = text_recognize(img1, model)
            # 对相应数据进行记录,框的位置,识别结果文字,置信度,左右边距以及页码数
            up = int(up)
            down = int(down)
            left = int(left)
            right = int(right)
            text = ans[0][0]
            grade = float(ans[0][1])
            # 对数字框进行了一次简单修正
            if left > l_edge + 1350:
                text = num_fix(text)
            # 满足置信度的情况以及框框大小的送入box里边
            if text != '' and grade > 0.4 and down - up < 200:
                box = {'up': up, 'down': down, 'left': left, 'right': right, 'text': text, 'grade': grade,
                       'l_edge': l_edge, 'r_edge': r_edge, 'page_name': imgName}
                box_list.append(copy.deepcopy(box))
            # 输出答案
            # print(ans)
            # 划线
            cv.line(img, (left, up), (right, up), (0, 0, 255), 2)
            cv.line(img, (left, up), (left, down), (0, 0, 255), 2)
            cv.line(img, (left, down), (right, down), (0, 0, 255), 2)
            cv.line(img, (right, up), (right, down), (0, 0, 255), 2)
        # 将该页所有识别结果存入字典
        boxAnswerDict[imgName] = box_list
        # 保存图片
        savePathBox = os.path.join(img_save_path, str(pageNum) + ".jpg")
        print(savePathBox)
        cv.imwrite(savePathBox, img)
        print(time.time() - t)
        t = time.time()
        time.sleep(5)
    # 将结果存入json
    json_save_path = os.path.join(baseRoot, 'json/box.json')
    if IsSave:
        with open(json_save_path, 'w', encoding='UTF-8') as f:
            f.write(json.dumps(boxAnswerDict, ensure_ascii=False, indent=4))


def main():
    pass
    # getBoxAndRecognize(openRoaImgPath, saveImgPath, saveJsonPath)


if __name__ == "__main__":
    main()
