# import numpy as np
# import cv2 as cv
#
# kernel = np.ones((3, 3), np.uint8)
# img = cv.imread('PC_art_test/HP/0001.jpg')
# # img_new = img
# # img_new = cv.resize(img, (int(img.shape[1] * 0.1), int(img.shape[0] * 0.1)))
# img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# _, img_bin = cv.threshold(img_gray, 240, 255, cv.THRESH_BINARY)
# img_erode = cv.erode(img_bin, kernel, iterations=1)
# img_erode = ~img_erode
# xpos = 0
# for i in range(0, img_erode.shape[0]):
#     if img_erode[5000][i] == 255:
#         xpos = i
#         break
#
# ypos = 0
# for i in range(0, img_erode.shape[1]):
#     if img_erode[i][4000] == 255:
#         ypos = i
#         break
#
# mat_translation = np.float32([[1, 0, -xpos+30], [0, 1, -ypos+30]])
# img_erode = cv.warpAffine(img_erode, mat_translation, (img_erode.shape[1], img_erode.shape[0]),
#                        borderValue=(0, 0, 0))
#
# # contours, hierarchy = cv.findContours(img_erode, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
# # cv.drawContours(img_erode, contours, -1, (255, 255, 255), 3)
# # cv.imshow('img_', img_gray)
# # cv.imshow('img_bin', img_bin)
# cv.imshow('img_erode', img_erode)
# cv.waitKey(0)
# # cv2.imwrite('img_neddd.jpg', dst)
