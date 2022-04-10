import os
import re
import cv2 as cv


def imgs_name_add(imgRoot, cnt):
    """
       imgRoot:文件夹名字
       cnt:名字以多少号序号开始
    """
    imgNameList = []
    for root, dirs, files in os.walk(imgRoot, topdown=True):
        for name in files:
            _, ending = os.path.splitext(name)
            if ending == '.jpg':
                imgNameList.append(os.path.join(name))
    print(imgNameList)
    # 正则取出前缀排序
    print(imgNameList[0])
    x = re.findall(r"\d+", imgNameList[0])
    print(x)

    imgNameList.sort(key=lambda x: int(re.findall(r"\d+", x)[0]))
    # 按照顺序修改名字
    for i in range(len(imgNameList) - 1, -1, -1):
        oldName = os.path.join(imgRoot, imgNameList[i])
        newName = os.path.join(imgRoot, str(i + cnt).zfill(4) + '.jpg')
        print(oldName, '->', newName)
        os.rename(oldName, newName)
    print('name sorting completed')


def imgs_name_del(imgRoot, cnt):
    """
       imgRoot:文件夹名字
       cnt:名字以多少号序号开始
    """
    imgNameList = []
    for root, dirs, files in os.walk(imgRoot, topdown=True):
        for name in files:
            _, ending = os.path.splitext(name)
            if ending == '.jpg':
                imgNameList.append(os.path.join(name))
    print(imgNameList)
    # 正则取出前缀排序
    print(imgNameList[0])
    x = re.findall(r"\d+", imgNameList[0])
    print(x)

    imgNameList.sort(key=lambda x: int(re.findall(r"\d+", x)[0]))
    # 按照顺序修改名字
    for i in range(0, len(imgNameList), 1):
        oldName = os.path.join(imgRoot, imgNameList[i])
        newName = os.path.join(imgRoot, str(i+cnt).zfill(4) + '.jpg')
        print(oldName, '->', newName)
        os.rename(oldName, newName)
    print('name sorting completed')


# imgs_name_add('PC_test/', 188)
