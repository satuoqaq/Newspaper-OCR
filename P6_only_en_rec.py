from PaddleOCR.paddleocr import PaddleOCR
import os
import json
import cv2 as cv
import re
import matplotlib.pyplot as plt
import copy
import numpy as np

kernel = np.ones((5, 5), np.uint8)

ocr = PaddleOCR(use_angle_cls=False, lang="ch", use_gpu=False)


def get_right_value(ysum, lpos):
    rpos = min(len(ysum - 1), lpos + 25)
    return sum(ysum[lpos:rpos])


def get_new_id_pos(ysum):
    l, r = -1, -1
    for i in range(0, len(ysum)):
        if l != -1:
            if get_right_value(ysum, i) <= 50:
                r = i
                break
        elif get_right_value(ysum, i) >= 200:
            l = i
    return l, min(r + 7, len(ysum))


def get_new_id_img(img):
    img2 = copy.deepcopy(img)
    # cv.imshow("img_base", img)
    _, img = cv.threshold(img, 150, 255, cv.THRESH_BINARY)
    # cv.imshow("img_inv", img)
    img = cv.erode(img, kernel, iterations=1)
    # cv.imshow("img_erode", img)
    img1 = (255 - img) / 255
    ysum = np.sum(img1, axis=0)
    l, r = get_new_id_pos(ysum)
    if l == -1 or r == -1 or l >= r:
        print(l, r, 'wrong')
        return img2
    height, width = img.shape
    img_new = img[0:height, l:r]
    return img_new


def cmp(x, y):
    xx = int(x[:x.find('.')])
    yy = int(y[:y.find('.')])
    if xx < yy:
        return 1
    elif xx == yy:
        return 0
    else:
        return -1


def split_new_id(ans):
    text, grade = ans[0]
    if grade < 0.5:
        return ''
    if len(text) < 2:
        return ''
    maj_id_list = re.findall(r"[a-zA-Z0-9]+", text)
    if len(maj_id_list) == 0:
        return ''
    new_maj_id = maj_id_list[0]
    if len(new_maj_id) == 2:
        return new_maj_id
    else:
        return ''


def maj_id_rec(img):
    img_new = get_new_id_img(img)
    # plt.imshow(img_new,cmap='gray')
    # plt.show()
    ans = ocr.ocr(img_new, det=False, cls=False, rec=True)
    return split_new_id(ans)


def main():
    pass


if __name__ == "__main__":
    main()
