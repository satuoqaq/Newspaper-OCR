import json
import sys
import cv2 as cv
import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
import os


def fix_wrong_msg(baseRoot):
    with open(os.path.join(baseRoot, 'json/wrong_maj_id.json'), 'r', encoding='UTF-8')as fp:
        maj_id = json.load(fp)
    with open(os.path.join(baseRoot, 'json/wrong_maj_name.json'), 'r', encoding='UTF-8')as fp1:
        maj_name = json.load(fp1)
    with open(os.path.join(baseRoot, 'json/wrong_maj_place.json'), 'r', encoding='UTF-8')as fp2:
        maj_place = json.load(fp2)
    with open(os.path.join(baseRoot, 'json/wrong_maj_tuition.json'), 'r', encoding='UTF-8')as fp3:
        maj_tuition = json.load(fp3)
    with open(os.path.join(baseRoot, 'json/School_msg.json'), 'r', encoding='UTF-8')as fp4:
        sch_data = json.load(fp4)

    path = os.path.join(baseRoot, 'HP_roa')

    for i in range(0, len(maj_id)):
        maj = maj_id[i]

        print('***********************************************')
        print('页码:', maj['page_name'])
        print('专业id:', maj['id'], ' ------需修改')
        print('专业名称:', maj['name'])
        print('专业名额:', maj['place'])
        print('专业学费:', maj['tuition'])

        page_name = maj['page_name']
        img_path = os.path.join(path, page_name)
        img = cv.imread(img_path)
        left = max(0, maj['left'] - 100)
        right = min(maj['right'] + 100, img.shape[1])
        up = max(0, maj['up'] - 50)
        down = min(maj['down'] + 50, img.shape[0])
        img = img[up:down, left:right]
        img = cv.resize(img, (int(img.shape[1] * 0.5), int(img.shape[0] * 0.5)))
        plt.imshow(img)
        plt.axis('off')
        plt.show()
        print(sch_data[maj['sch_index']]['name'])
        new_maj_id = input("请输入专业id,若无需修改则回车:")
        if new_maj_id != '':
            maj['id'] = new_maj_id
        new_maj_name = input("请输入专业name,若无需修改则回车:")
        if new_maj_name != '':
            maj['name'] = new_maj_name
        sch_data[maj['sch_index']]['Major_list'][maj['maj_index']] = maj

    for i in range(0, len(maj_place)):
        maj = maj_place[i]
        if sch_data[maj['sch_index']]['maj_num_check'] == 1:
            continue
        print('***********************************************')
        print('学校名称', sch_data[maj['sch_index']]['name'])
        print('页码:', maj['page_name'])
        print('专业id:', maj['id'])
        print('专业名称:', maj['name'])
        print('专业名额:', maj['place'], ' ------需修改')
        print('专业学费:', maj['tuition'])

        page_name = maj['page_name']
        img_path = os.path.join(path, page_name)
        img = cv.imread(img_path)
        left = max(0, maj['left'] - 100)
        right = min(maj['right'] + 100, img.shape[1])
        up = max(0, maj['up'] - 50)
        down = min(maj['down'] + 50, img.shape[0])
        img = img[up:down, left:right]
        img = cv.resize(img, (int(img.shape[1] * 0.5), int(img.shape[0] * 0.5)))
        plt.imshow(img)
        plt.axis('off')
        plt.show()
        new_maj_place = input("请输入专业招生人数,若无需修改则回车:")
        if new_maj_place != '':
            maj['place'] = new_maj_place
        sch_data[maj['sch_index']]['Major_list'][maj['maj_index']] = maj

    # for i in range(0, len(maj_tuition)):
    #     maj = maj_tuition[i]
    #     print('***********************************************')
    #     print('页码:', maj['page_name'])
    #     print('专业id:', maj['id'])
    #     print('专业名称:', maj['name'])
    #     print('专业名额:', maj['place'])
    #     print('专业学费:', maj['tuition'], ' ------需修改')
    #     page_name = maj['page_name']
    #     img_path = os.path.join(path, page_name)
    #     img = cv.imread(img_path)
    #     left = max(0, maj['left'] - 100)
    #     right = min(maj['right'] + 100, img.shape[1])
    #     up = max(0, maj['up'] - 50)
    #     down = min(maj['down'] + 50, img.shape[0])
    #     img = img[up:down, left:right]
    #     img = cv.resize(img, (int(img.shape[1] * 0.5), int(img.shape[0] * 0.5)))
    #     plt.imshow(img)
    #     plt.axis('off')
    #     plt.show()
    #     new_maj_tuition = input("请输入专业学费,若无需修改则回车:")
    #     if new_maj_tuition != '':
    #         maj['tuition'] = new_maj_tuition
    #     sch_data[maj['sch_index']]['Major_list'][maj['maj_index']] = maj

    savePath = os.path.join(baseRoot, 'json/School_msg.json')
    with open(savePath, 'w', encoding='UTF-8') as f:
        f.write(json.dumps(sch_data, ensure_ascii=False, indent=4))


def main():
    fix_wrong_msg('PC3')


if __name__ == '__main__':
    main()
