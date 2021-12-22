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

baseImgPath = 'PC3/HP/'
baseRoot = baseImgPath.split('/')[0]
roaImgPath = os.path.join(baseRoot, 'HP_roa')
lineImgPath = os.path.join(baseRoot, 'HP_line')
roaSplitImgPath = os.path.join(baseRoot, 'HP_roa_split')
boxImgPath = os.path.join(baseRoot, 'HP_box')
jsonPath = os.path.join(baseRoot, 'json')

def make_dir(dir_list):
    for name in dir_list:
        if not os.path.exists(name):
            os.mkdir(name)


dirList = [roaImgPath, lineImgPath, roaSplitImgPath, boxImgPath, jsonPath]
make_dir(dirList)

# get_roa_img(baseImgPath, roaImgPath)
# get_com_line(baseRoot, roaImgPath, roaSplitImgPath)
# get_full_line(baseRoot, roaImgPath, lineImgPath)
# getBoxAndRecognize(baseRoot, roaImgPath, boxImgPath)
get_topbar_data(baseRoot)
# get_message(baseRoot)
# fix_wrong_msg(baseRoot)
