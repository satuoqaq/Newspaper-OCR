# def maj_id_wrong_change(name):
#     if name == '00' or name == 'QQ':
#         name = '0Q'
#     if name.find('I') != -1:
#         name = name.replace('I', '1')
#     return name
#
#
# ans = maj_id_wrong_change('CI')
# print(ans)
import cv2
import matplotlib.pyplot as plt
import json
import os
import matplotlib

# matplotlib.use('TkAgg')
baseRoot = 'PC'
page_name = '0000.jpg'
imgNameList = os.listdir(os.path.join(baseRoot, 'HP_roa'))
end_page_name = str(len(imgNameList)).zfill(4) + '.jpg'

img_path = os.path.join('PC', 'HP_roa', imgNameList[0])
img = cv2.imread(img_path)
# cv2.imshow('img', img)
# cv2.waitKey(0)
plt.imshow(img)
plt.axis('off')
plt.show()
