import cv2 as cv
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
import time


def get_img_box(imgStart):
    """
        使用传统像素分布的方法将图像进行分割
        首先将整张图片按照行分割,然后对于一行文字再进行按段分割
        返回所有框的坐标
        :param imgStart: 图片打开路径 str
    """

    # 设置一个阈值表示空白部分的最大像素和(考虑噪声)
    blank_space_max_sumVal = 5000
    # 一个text_box的最小像素和
    text_min_sumVal = 50000
    # 一段文字框的最小像素长度
    textMinLen = 10
    # val表示该位置有没有东西
    line_val = 15 * 255
    val = 3 * 255
    # 二值化阈值
    thresh_val = 200
    # 膨胀腐蚀卷积核
    kernel = np.ones((3, 3), np.uint8)
    kernel5 = np.ones((5, 5), np.uint8)
    # 存储结果的list
    ansBoxList = []

    height, width = imgStart.shape

    # 原图大小为了竖线
    _, base_img = cv.threshold(imgStart, 200, 255, cv.THRESH_BINARY)
    base_img = cv.medianBlur(base_img, 5)
    base_img = 255 - base_img

    #  切割一部分是为了横线
    _, img_for_line = cv.threshold(imgStart[0:height, 30:width - 30], thresh_val, 255, cv.THRESH_BINARY)
    img_for_line = cv.medianBlur(img_for_line, 5)
    img_for_line = 255 - img_for_line

    y_sum = np.sum(img_for_line, axis=1)
    posUp = 0
    cnt = 0
    while posUp < y_sum.size:
        if y_sum[posUp] >= line_val:
            posDown = posUp + 1
            while posDown < y_sum.size and y_sum[posDown] >= line_val:
                posDown = posDown + 1
            if posDown - posUp >= 30:
                img_hang = base_img[posUp - 3:posDown + 5, 0:imgStart.shape[1]]
                x_sum = np.sum(img_hang, axis=0)
                blank_min_len = min(50, int((posDown - posUp) * 0.6))
                posL = 0
                while posL < x_sum.size:

                    if x_sum[posL] >= val:
                        posR = posL + 1
                        while posR < x_sum.size:

                            if x_sum[posR] >= val:
                                posR = posR + 1
                            else:
                                # 大于最小文字长度
                                if posR - posL > textMinLen and sum(x_sum[posL:posR]) > text_min_sumVal:
                                    # 取看一段文字的结尾一小段,看这小段是否为长间隔长度的留白,-1表示有留白
                                    blank_space = sum(x_sum[posR:min(posR + blank_min_len, x_sum.size)])
                                    if blank_space <= blank_space_max_sumVal:
                                        # 如有留白就划线,直接查找留白之后的东西
                                        l_pos = max(0, posL - 10)
                                        r_pos = min(posR + 10, img_hang.size)
                                        if cnt > 0:
                                            last_posUp = ansBoxList[cnt - 1][0]
                                            last_posR = ansBoxList[cnt - 1][3]
                                            if last_posUp != posUp:  # 如果不是同一行
                                                if 100 < l_pos < 1350:
                                                    l_pos = 120
                                                # 直接加进去没问题
                                                ansBoxList.append([posUp, posDown, l_pos, r_pos])
                                                cnt = cnt + 1
                                            else:  # 是同一行的话情况很多
                                                # 就是上一个是专业id
                                                if last_posR < 120:
                                                    # 且这部分是专业名
                                                    if posL < 1350:
                                                        # 把这部分专业名字尽量连接到id后边,防止漏检字的左边
                                                        l_pos = last_posR + 5
                                                    ansBoxList.append([posUp, posDown, l_pos, r_pos])
                                                    cnt = cnt + 1
                                                elif posL > 1350:  # 如果是人数,学费
                                                    # 且上一个不是人数,学费,其实就是专业名了
                                                    if ansBoxList[cnt - 1][2] < 1350:
                                                        # 就把专业名的框框往后移一个字的长度,防止尾部漏检
                                                        ansBoxList[cnt - 1][3] = min(last_posR + 40, posL - 10)
                                                    ansBoxList.append([posUp, posDown, l_pos, r_pos])
                                                    cnt = cnt + 1
                                                elif posL - last_posR < 80:  # 这种就是专业名从中间断开了,连接起来就行
                                                    ansBoxList[cnt - 1][3] = r_pos
                                                else:  # 还有什么奇奇怪怪的情况,确实离谱
                                                    ansBoxList.append([posUp, posDown, l_pos, r_pos])
                                                    cnt = cnt + 1
                                        else:
                                            ansBoxList.append([posUp, posDown, l_pos, r_pos])
                                            cnt = cnt + 1
                                        posL = posR + blank_min_len
                                    # 如果没有留白,就是后边还有文字,就接着找
                                    else:
                                        right_range = min(posR + blank_min_len, x_sum.size) - 1
                                        new_posR = posR
                                        for findPosR in range(right_range, posR + 1, -1):
                                            if x_sum[findPosR] >= val:
                                                new_posR = findPosR
                                                break
                                        if new_posR == posR:
                                            posR = right_range
                                        else:
                                            posR = new_posR
                                else:
                                    if sum(x_sum[posL:posR]) > text_min_sumVal and sum(
                                            x_sum[posR:min(posR + 30, x_sum.size - 1)]) > text_min_sumVal:
                                        posR = posR + 1
                                    else:
                                        posL = posR
                                        break
                        else:
                            if posR - posL > textMinLen and sum(x_sum[posL:posR]) > text_min_sumVal:
                                l_pos = max(0, posL - 10)
                                r_pos = min(posR + 10, img_hang.size)
                                ansBoxList.append([posUp, posDown, l_pos, r_pos])
                                cnt = cnt + 1
                            posL = posR
                    posL = posL + 1
            posUp = posDown
        posUp = posUp + 1

    text_boxes = np.array(ansBoxList)
    return text_boxes


if __name__ == "__main__":
    img_path = 'PC/HP_roa_split/0010_2.jpg'
    img = cv.imread(img_path, 0)
    ans_box = get_img_box(img)
    # x = input()
