import cv2 as cv
import json
import os

imgOpenPath = 'PC2/HP_roa'
imgDrawLinePath = 'PC2/HP_line'


def get_full_line(baseRoot, imgRoot, saveRoot):
    """
       找到位置后 划线以便查看是否正确
       :param imageRoot: 图片打开路径 str
       :param savePath: 图片储存路径 str
     """
    dict_split_name = os.path.join(baseRoot, 'json/split_positions.json')
    with open(dict_split_name, 'r')as fp:
        page_data = json.load(fp)

    for name in page_data:

        upper_pos = page_data[name]['upper_pos']
        down_pos = page_data[name]['down_pos']
        left_pos = page_data[name]['left_pos']
        right_pos = page_data[name]['right_pos']
        imgPath = os.path.join(imgRoot, name)
        img = cv.imread(imgPath, 0)
        cv.line(img, (0, upper_pos), (9999, upper_pos), (0, 0, 255), 7)
        cv.line(img, (0, down_pos), (9999, down_pos), (0, 0, 255), 7)
        cv.line(img, (left_pos, 0), (left_pos, 9999), (0, 0, 255), 7)
        cv.line(img, (right_pos, 0), (right_pos, 9999), (0, 0, 255), 7)
        savePath = os.path.join(saveRoot, name)
        cv.imwrite(savePath, img)
        print(name+'划线完毕。')
    print('所有图片划线完毕!')
def main():
    get_full_line(imgOpenPath, imgDrawLinePath)


if __name__ == "__main__":
    main()
