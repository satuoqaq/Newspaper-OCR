import math
import re
import cv2 as cv
import numpy as np
import os

# *所有参数*

# 图片路径
# initialImgRoot = 'PC2/HP/'
# ImgRoaRoot = 'PC2/HP_roa/'

need_change_position = -400


def imgSort_and_Rename(imgRoot):
    """
       对路径中所有的图片进行过滤后手动去除冗余页码
       然后对其进行顺序排序后重新命名,按照0000,0001,0002,0003...jpg的方式
       :param imageRoot: 图片路径
    """
    imgNameList = []
    for root, dirs, files in os.walk(imgRoot, topdown=True):
        for name in files:
            _, ending = os.path.splitext(name)
            if ending == '.jpg':
                imgNameList.append(os.path.join(name))
    print(imgNameList)
    # 正则取出前缀排序
    imgNameList.sort(key=lambda x: int(re.findall(r"\d+", x)[0]))
    # 按照顺序修改名字
    for i in range(0, len(imgNameList)):
        oldName = os.path.join(imgRoot, imgNameList[i])
        newName = os.path.join(imgRoot, str(i).zfill(4) + '.jpg')
        print(oldName, '->', newName)
        os.rename(oldName, newName)
    print('name sorting completed')


def get_roa_img(imgRoot, saveRoot):
    imgSort_and_Rename(imgRoot)
    """
       :此函数主要目的是为了矫正图片存在的角度
       通过寻找报纸顶端直线计算夹角并且进行旋转回正
       :param imageRoot: 待旋转的图片路径
       :param saveRoot: 旋转后的图片路径
    """
    imgNameList = os.listdir(imgRoot)
    startPage, endPage = 0, len(imgNameList)
    if not os.path.exists(saveRoot):
        os.makedirs(saveRoot)
    for i in range(startPage, endPage):
        name = str(i).zfill(4) + '.jpg'
        print(name)
        imgPath = os.path.join(imgRoot, name)
        # 取出图片并灰度化
        imgStart = cv.imread(imgPath, 0)

        # 平移图片到左上角
        kernel = np.ones((3, 3), np.uint8)
        _, img_bin = cv.threshold(imgStart, 240, 255, cv.THRESH_BINARY)
        img_erode = cv.erode(img_bin, kernel, iterations=1)
        img_erode = ~img_erode
        x_pos = 0
        for j in range(0, img_erode.shape[0]):
            if img_erode[5000][j] == 255:
                x_pos = j
                break
        y_pos = 0
        for j in range(0, img_erode.shape[1]):
            if img_erode[j][4000] == 255:
                y_pos = j
                break
        mat_translation = np.float32([[1, 0, -x_pos + 30], [0, 1, -y_pos + 30]])
        imgStart = cv.warpAffine(imgStart, mat_translation, (img_erode.shape[1], img_erode.shape[0]),
                                 borderValue=(255, 255, 255))

        # 截取顶栏位置寻找直线
        img = imgStart[50:2000, 30:imgStart.shape[1]]
        angleRoa = 0
        # 进行缩放、边缘滤波、hough变换提取直线
        img_new = cv.resize(img, (int(img.shape[1] * 0.5), int(img.shape[0] * 0.5)))
        img_canny = cv.Canny(img_new, 50, 150)
        lines = cv.HoughLines(img_canny, 1, np.pi / 1800, 100)
        # 取出这个直线 并且旋转
        for j in range(0, 1):
            rho, theta = lines[j][0]  # line[0]存储的是点到直线的极径和极角，其中极角是弧度表示的。
            a = np.cos(theta)  # theta是弧度
            b = np.sin(theta)
            x0 = a * rho  # 代表x = r * cos（theta）
            y0 = b * rho  # 代表y = r * sin（theta）
            x1 = int(x0 + 5000 * (-b))  # 计算直线起点横坐标
            y1 = int(y0 + 5000 * a)  # 计算起始起点纵坐标
            x2 = int(x0 - 5000 * (-b))  # 计算直线终点横坐标
            y2 = int(y0 - 5000 * a)  # 计算直线终点纵坐标
            # print(x1, y1, x2, y2)
            if x2 == x1 or y1 == y2:
                print('图片' + str(i) + ": 完全垂直")
                continue
            angle = math.degrees(math.atan((y2 - y1) / (x2 - x1)))
            if abs(angle + 90) < 45:
                angleRoa = angle + 90
            elif abs(angle - 90) < 45:
                angleRoa = angle - 90
            else:
                angleRoa = angle
            print('图片' + str(i) + '角度: ' + str(angleRoa))
            # 注：这里的数值1000给出了画出的线段长度范围大小，数值越小，画出的线段越短，数值越大，画出的线段越长
            cv.line(img_new, (x1, y1), (x2, y2), (0, 0, 255), 1)  # 点的坐标必须是元组，不能是列表
        # matRoa = cv.getRotationMatrix2D((0, 0), angleRoa, 1)
        # img = cv.warpAffine(img, matRoa, (img.shape[1], img.shape[0]), borderValue=255)

        # 输出检测的直线图片
        # cv.imshow("image" + str(i), img_new)

        # 旋转缩放图片
        # matRoa = cv.getRotationMatrix2D((0, 0), angleRoa, 1)
        # img_roa = cv.warpAffine(img_new, matRoa, (img_new.shape[1], img_new.shape[0]))
        # cv.imshow('img', img_roa)

        # 旋转原始图片
        matRoa = cv.getRotationMatrix2D((0, 0), angleRoa, 1)
        imgRoa = cv.warpAffine(imgStart, matRoa, (imgStart.shape[1], imgStart.shape[0]), borderValue=255)

        cv.imwrite(os.path.join(saveRoot, name), imgRoa)
        print('步骤一:图片旋转完成！')


def main():
    pass
    # imgSort_and_Rename(initialImgRoot)
    # get_roa_img(initialImgRoot, ImgRoaRoot)


if __name__ == "__main__":
    main()
