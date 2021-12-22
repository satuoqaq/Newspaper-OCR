import cv2 as cv
from page_enhance import page_enhance

# "up": 4421,
#       "down": 4492,
#       "left": 318,
#       "right": 979,
img = cv.imread('PC2/HP_roa/0010.jpg', 0)
img = img[4421:4492, 318:400]
img = cv.GaussianBlur(img, (3, 3), 0)
cv.imwrite('img.png', img)
print(1)
