import cv2 as cv
import json
import os
from P1_img_roation import get_roa_img
from P2_img_split import get_com_line
from P3_get_full_line import get_full_line
from P4_get_box_and_rec import getBoxAndRecognize
from P5_get_topBarMsg import get_topbar_data
from P6_get_message import get_message
from P7_fix_wrong_msg import fix_wrong_msg
from P8_write_excel import write_excel


# 这两个是自己选的路径  一个是图像原始图像的位置 一个是存储所有东西的位置
openBaseImgPath = 'PC3/HP'
saveBaseRoot = 'PC3'
# 所有的东西都存到相应saveBaseRoot位置下边
roaImgPath = os.path.join(saveBaseRoot, 'HP_roa')
lineImgPath = os.path.join(saveBaseRoot, 'HP_line')
roaSplitImgPath = os.path.join(saveBaseRoot, 'HP_roa_split')
boxImgPath = os.path.join(saveBaseRoot, 'HP_box')
jsonPath = os.path.join(saveBaseRoot, 'json')


def make_dir(dir_list):
    for name in dir_list:
        print(name)
        if not os.path.exists(name):
            os.mkdir(name)


dirList = [roaImgPath, lineImgPath, roaSplitImgPath, boxImgPath, jsonPath]
make_dir(dirList)
# botton 1 处理图片得到box
get_roa_img(openBaseImgPath, roaImgPath)
get_com_line(saveBaseRoot, roaImgPath, roaSplitImgPath)
get_full_line(saveBaseRoot, roaImgPath, lineImgPath)
getBoxAndRecognize(saveBaseRoot, roaImgPath, boxImgPath)
# botton 2 然后让他们check一下
get_topbar_data(saveBaseRoot)
# botton 3  得到学校信息然后纠错
get_message(saveBaseRoot)
fix_wrong_msg(saveBaseRoot)
# botton 4 写excel
write_excel(saveBaseRoot)
