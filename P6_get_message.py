import copy
import os

from matplotlib import pyplot as plt

import json
import sys
import cv2 as cv
from P6_only_en_rec import maj_id_rec
from P6_Post_processing import process_sch_msg
import xlwt

box_data = {}


# 找上一个框框
def next_box(pg_name, bx_id):
    if bx_id + 1 < len(box_data[pg_name]):
        bx_id = bx_id + 1
    else:
        pg_name = str(int(pg_name[:4]) + 1).zfill(4) + '.jpg'
        if pg_name not in box_data.keys():
            bx_id = -1
        else:
            bx_id = 0
    return pg_name, bx_id


# 找下一个框框
def last_box(pg_name, bx_id):
    if bx_id > 0:
        bx_id = bx_id - 1
    else:
        pg_name = str(int(pg_name[:4]) - 1).zfill(4) + '.jpg'
        if pg_name not in box_data.keys():
            bx_id = -1
        else:
            bx_id = len(box_data[pg_name]) - 1
    return pg_name, bx_id


def is_num(x):  # 判断是不是全是数字
    if len(x) == 0:
        return False
    for i in range(len(x)):
        if '0' <= x[i] <= '9':
            continue
        else:
            return False
    return True


def is_Chinese(ch):
    if '\u4e00' <= ch <= '\u9fff':
        return True
    return False


def is_char(x):  # 检测是否为字符
    for i in range(len(x)):
        if '0' <= x[i] <= '9' or 'a' <= x[i] <= 'z' or 'A' <= x[i] <= 'Z':
            continue
        else:
            return False
    return True


def is_School(box):  # 检测是不是学校代码
    text = box['text']
    l_edge = box['l_edge']
    left = box['left']
    up = box['up']
    down = box['down']
    if len(text) >= 4 and is_num(text[0:4]) and left < l_edge + 100 and down - up >= 80:
        return True
    return False


def is_Major(pg_name, bx_id):
    box = box_data[pg_name][bx_id]
    text = box['text']
    text = text.replace('.', '')
    l_edge = box['l_edge']
    left = box['left']
    last_pg_name, last_bx_id = last_box(pg_name, bx_id)
    box1 = box_data[last_pg_name][last_bx_id]
    if len(text) >= 2 and (
            box1['right'] - box1['left'] < 1600 or (len(box1['text']) >= 2 and box1['text'][0:2] == '地址')):
        if len(text) >= 3 and is_char(text[0:2]) and is_num(text[2]):
            return False
        if is_char(text[0:2]) and l_edge + 100 > left:
            return True
    return False


def is_Sch_place(box):
    text = box['text']
    r_edge = box['r_edge']
    left = box['left']
    if is_num(text) and left > r_edge - 580:
        return True
    return False


def is_Major_place(box):
    text = box['text']
    text = text.replace('.', '')
    l_edge = box['l_edge']
    left = box['left']
    if len(text) <= 3 and left > l_edge + 1350 and (is_num(text) and int(text) < 1000):
        return True
    return False


def is_half_Major(pg_name, bx_id):
    box = box_data[pg_name][bx_id]
    text = box['text']
    l_edge = box['l_edge']
    left = box['left']
    last_pg_name, last_bx_id = last_box(pg_name, bx_id)
    box1 = box_data[last_pg_name][last_bx_id]
    if len(text) >= 1 and is_char(text[0]) and left < l_edge + 100 and is_Major_tuition(box1):
        return True
    return False


def is_Sch_remark(pg_name, bx_id):
    box = box_data[pg_name][bx_id]
    text = box['text']
    pg_name, bx_id = last_box(pg_name, bx_id)
    box1 = box_data[pg_name][bx_id]
    right = box1['right']
    r_edge = box1['r_edge']
    if right < r_edge - 65 and text[0:2] == '备注':
        return True
    return False


def is_Major_tuition(box):
    text = box['text']
    l_edge = box['l_edge']
    left = box['left']
    if len(text) >= 2 and left > l_edge + 1350 and (
            # or int(text)==0 是一个特判,有一个0的情况
            text == '免费' or text == '待定' or (is_num(text) and (int(text) >= 1000 or int(text) == 0))):
        return True
    return False


def fix_name(text):
    pos = len(text) - 1
    for i in range(pos, -1, -1):
        if not '0' <= text[i] <= '9':
            pos = i
            break
    new_sch_name = text[0:pos + 1]
    new_place = text[pos + 1:]
    return new_sch_name, new_place


def get_maj_range(left, right, up, down, box):
    left = min(left, box['left'])
    right = max(right, box['right'])
    up = min(up, box['up'])
    down = max(down, box['down'])
    return left, right, up, down


def change_batch(batch, text_title):
    if text_title.find('本科一批') != -1:
        batch = '本一'
    if text_title.find('本科二批') != -1:
        batch = '本二'
    if text_title.find('专科') != -1:
        batch = '专科'
    if text_title.find('深度贫困专项') != -1 or \
            text_title.find('省级公费师范生') != -1 \
            or text_title.find('本土人才培养专项') != -1:
        batch = '跳过'
    return batch


def get_box_img(baseRoot, box_img):
    pg_name = box_img['page_name']
    left = box_img['left']
    right = box_img['right']
    up = box_img['up']
    down = box_img['down']
    openPath = os.path.join(baseRoot, 'HP_roa', pg_name)
    img = cv.imread(openPath, 0)
    img = img[up:down, left:right]
    return img


def fix_maj_id_box(baseRoot, box_maj):
    img = get_box_img(baseRoot, box_maj)
    text = box_maj['text']
    # plt.imshow(img,cmap='gray')
    # plt.show()
    new_id = maj_id_rec(img)
    if text[:2] != new_id:
        print(text)
        print(new_id)
        print('---------')
    if new_id != '' and new_id.find('Q') != -1 or is_num(new_id):
        text = text.replace('.', '')
        pos = 0
        while pos < len(text):
            if '0' <= text[pos] <= '9' or 'a' <= text[pos] <= 'z' or 'A' <= text[pos] <= 'Z':
                pos = pos + 1
            else:
                break
        rest_text = text[pos:]
        new_text = new_id + rest_text
        box_maj['text'] = new_text
        if text != new_text:
            print('old:', text)
            print('new:', new_text)
    return box_maj


def get_maj_id_order(maj_id):
    ans = 0
    if len(maj_id) == 2:
        if '0' <= maj_id[0] <= '9':
            x = ord(maj_id[0]) - ord('0')
        else:
            x = ord(maj_id[0]) - ord('A') + 10
        if '0' <= maj_id[1] <= '9':
            y = ord(maj_id[1]) - ord('0')
        else:
            y = ord(maj_id[1]) - ord('A') + 10
        ans = x * 36 + y
    return ans


def maj_id_wrong_change(name):
    if name == '00' or name == 'QQ':
        name = '0Q'
    if name.find('I') != -1:
        name = name.replace('I', '1')
    if name.find('Z') != -1:
        name = name.replace('Z', '2')

    return name


def get_message(baseRoot):
    School_list = []
    School = {}
    Major_list = []
    Major = {}
    halfMajorList = []
    json_box_name = os.path.join(baseRoot, 'json/box.json')
    json_pageMsg_name = os.path.join(baseRoot, 'json/page_msg.json')
    start_fg = 0
    start_text = '本科'
    page_name = '0000.jpg'
    imgNameList = os.listdir(os.path.join(baseRoot, 'HP_roa'))
    end_page_name = str(len(imgNameList)).zfill(4) + '.jpg'
    end_text = '三、藏文、彝文一类模式'
    AS = '理科'  # 文理科(arts or science)
    Batch = '本一'  # 本科 本科提前批 本一 本二 专科
    box_id = 0
    global box_data
    with open(json_box_name, 'r', encoding='UTF-8')as fp:
        box_data = json.load(fp)
    wrong_maj_name = []
    wrong_maj_id = []
    wrong_maj_place = []
    wrong_maj_tuition = []
    with open(json_pageMsg_name, 'r', encoding='UTF-8')as fp:
        page_data = json.load(fp)
    while box_id != -1:
        box = box_data[page_name][box_id]
        #  先找到开始标志
        if start_fg == 0:
            if box['text'] == start_text:
                start_fg = 1
            else:
                page_name, box_id = next_box(page_name, box_id)
                continue

        if page_name == end_page_name:
            break

        if box['text'] == end_text:
            print(box['text'])
            break

        if 120 < box['down'] - box['up']:
            print(box['text'])
            Batch = change_batch(Batch, box['text'])

        if is_School(box) and Batch != '跳过':
            #  找到学校先把学校的id,名字,学校招生人数进行统计
            text = box['text']
            School['page_name'] = box['page_name']
            School['id'] = text[:4]  # 记录学校id
            School['place'] = '0'
            Sch_name = ''
            School['as'] = AS
            School['batch'] = Batch
            School['page_num'] = page_data[School['page_name']]['page_number']
            School['left'] = box['left']
            School['right'] = box['right']
            School['up'] = box['up']
            School['down'] = box['down']
            if len(text) > 4:
                Sch_name = Sch_name + text[4:]
            page_name, box_id = next_box(page_name, box_id)
            # if box_id == -1 or page_name == end_page_name1:
            if box_id == -1 :
                break
            box = box_data[page_name][box_id]
            while not is_Sch_place(box) and box['text'][0:2] != '地址':
                School['left'], School['right'], School['up'], School['down'] = get_maj_range \
                    (School['left'], School['right'], School['up'], School['down'], box)
                Sch_name = Sch_name + box['text']
                page_name, box_id = next_box(page_name, box_id)
                if box_id == -1 :
                    break
                box = box_data[page_name][box_id]
            # 找到学校结尾了
            if is_Sch_place(box):
                School['place'] = box['text']
            else:
                Sch_name, Sch_place = fix_name(Sch_name)
                if Sch_place == '':
                    Sch_place = '0'
                School['place'] = Sch_place

            School['name'] = Sch_name
            Sch_sum_place = int(School['place'])
            Sch_sum_place_check = 0
            # 以上代码是从学校代码找到'地址'作为学校代码,名字,以及招生人数的结尾

            # 以下进入专业的寻找
            if box_id == -1 :
                break
            page_name, box_id = next_box(page_name, box_id)
            if box_id == -1 :
                break
            box = box_data[page_name][box_id]
            School['left'], School['right'], School['up'], School['down'] = get_maj_range \
                (School['left'], School['right'], School['up'], School['down'], box)
            # 循环的结束是找到下一个学校或者是找到备注(学校结尾判断)
            while box['text'][0:2] != '备注' and not is_School(box):
                # 如果找到一个专业,就循环下去
                if is_Major(page_name, box_id) or is_half_Major(page_name, box_id):
                    # save_maj_id_box(box, maj_cnt)
                    if box['text'].find('Q') != -1:
                        box = fix_maj_id_box(baseRoot, box)
                    halfMajorList.append([page_name, box_id])
                    text = box['text']
                    # 记录一个专业总体的位置
                    Major['left'] = box['left']
                    Major['right'] = box['right']
                    Major['up'] = box['up']
                    Major['down'] = box['down']
                    Major['page_name'] = page_name
                    Major_name = ''
                    Major['tuition'] = '0'
                    Major['place'] = '0'
                    if is_Major(page_name, box_id):
                        Major['id'] = text[:2]
                        Major_name = Major_name + text[2:]
                    else:
                        Major['id'] = text[:1]
                        Major_name = Major_name + text[1:]
                    Major['id'] = Major['id'].upper()
                    Major['id'] = Major['id'].replace('O', '0')
                    page_name, box_id = next_box(page_name, box_id)
                    if box_id == -1 :
                        break
                    box = box_data[page_name][box_id]
                    Major['left'], Major['right'], Major['up'], Major['down'] = get_maj_range \
                        (Major['left'], Major['right'], Major['up'], Major['down'], box)
                    School['left'], School['right'], School['up'], School['down'] = get_maj_range \
                        (School['left'], School['right'], School['up'], School['down'], box)
                    # 判断专业结尾,找出专业学费
                    while (not is_School(box) and not is_Major_tuition(box)) and not is_Sch_remark(page_name,
                                                                                                   box_id) and (
                            not (is_Major(page_name, box_id) and (Major['place'] != '0' or Major['tuition'] != '待定'))):
                        if is_Major_place(box):
                            Major['place'] = box['text']
                        else:
                            Major_name = Major_name + box['text']
                        # 下一个框框
                        page_name, box_id = next_box(page_name, box_id)
                        if box_id == -1 :
                            break
                        box = box_data[page_name][box_id]
                        Major['left'], Major['right'], Major['up'], Major['down'] = \
                            get_maj_range(Major['left'], Major['right'], Major['up'], Major['down'], box)
                        School['left'], School['right'], School['up'], School['down'] = get_maj_range \
                            (School['left'], School['right'], School['up'], School['down'], box)
                    else:
                        # 一个专业结束了,需要判断一下是否有专业招生数,如果没有,可能是框连到一起去了,需要分割出来
                        if is_School(box):
                            # 如果是专业跟着学校,没有place和tuition就是那种YD高水平运动队,就没有push到学校的List里边,如有需求,可修改
                            Major_list.append(copy.deepcopy(Major))
                            Major_list.clear()
                            page_name, box_id = last_box(page_name, box_id)
                            break
                        if Major['place'] == '0':
                            Major_name, Major_place = fix_name(Major_name)
                            if Major_place != '':
                                Major['place'] = Major_place
                        Major['name'] = Major_name
                        if is_Major_tuition(box):
                            Major['tuition'] = box['text']
                        # 把Major保存下载
                        if is_num(Major['place']):
                            Sch_sum_place_check = Sch_sum_place_check + int(Major['place'])

                        # img = cv.imread('PC/HP_roa/' + Major['page_name'])
                        # img_new = img[Major['up']:Major['down'], Major['left']:Major['right']]
                        # plt.imshow(img_new)
                        # plt.axis('off')
                        # plt.show()

                        Major_list.append(copy.deepcopy(Major))
                        Major['sch_index'] = len(School_list)
                        Major['maj_index'] = len(Major_list) - 1
                        # 判断一下Major的情况,如果有错误就记录下来 但是存的其实是Sch_msg.json下的位置 sch_index,maj_index
                        # 如果当前专业id只有一位或者说不是纯数字+字母
                        if len(Major['id']) < 2 or not is_char(Major['id']):
                            wrong_maj_id.append(copy.deepcopy(Major))
                        # 如果当前的专业id没有问题,但是跟前一id的顺序不对把两个都加进去
                        elif len(Major_list) > 1:
                            last_maj = Major_list[len(Major_list) - 2]
                            if get_maj_id_order(Major['id']) <= get_maj_id_order(last_maj['id']):
                                new_maj_id_last = maj_id_wrong_change(last_maj['id'])
                                new_maj_id = maj_id_wrong_change(Major['id'])
                                if get_maj_id_order(Major['id']) > get_maj_id_order(new_maj_id_last):
                                    Major_list[len(Major_list) - 2]['id'] = new_maj_id_last
                                elif get_maj_id_order(new_maj_id) > get_maj_id_order(last_maj['id']):
                                    Major_list[len(Major_list) - 1]['id'] = new_maj_id
                                else:
                                    last_maj['sch_index'] = len(School_list)
                                    last_maj['maj_index'] = len(Major_list) - 2
                                    wrong_maj_id.append(copy.deepcopy(last_maj))
                                    wrong_maj_id.append(copy.deepcopy(Major))
                        if Major['name'] == '':
                            wrong_maj_name.append(copy.deepcopy(Major))
                        if Major['place'] == '0' and School['place'] != '0':
                            wrong_maj_place.append(copy.deepcopy(Major))
                        if Major['tuition'] != '免费' and Major['tuition'] != '待定' and Major['tuition'][0] == '0':
                            wrong_maj_tuition.append(copy.deepcopy(Major))
                        Major.clear()
                        if is_Major(page_name, box_id):
                            page_name, box_id = last_box(page_name, box_id)
                # 下一个框框
                page_name, box_id = next_box(page_name, box_id)
                if box_id == -1 :
                    break
                box = box_data[page_name][box_id]
                if 120 < box['down'] - box['up']:
                    print(box['text'])
                    Batch = change_batch(Batch, box['text'])
            else:
                School['left'], School['right'], School['up'], School['down'] = get_maj_range \
                    (School['left'], School['right'], School['up'], School['down'], box)
                # 一个学校找完了,把信息存了
                if is_School(box):
                    page_name, box_id = last_box(page_name, box_id)
                elif box['text'][0:2] != '备注':
                    print('wrong_with:', page_name)
                    print(box)
                    sys.exit()
                School['Major_list'] = copy.deepcopy(Major_list)
                if Sch_sum_place_check == Sch_sum_place:
                    School['maj_num_check'] = 1
                else:
                    School['maj_num_check'] = 0
                Major_list.clear()
                print(School['page_name'], School['id'], School['name'], School['as'], School['batch'],
                      School['page_num'])
                School_list.append(copy.deepcopy(School))
                School.clear()
            if box_id == -1 :
                break
            # print(box['text'])
        page_name, box_id = next_box(page_name, box_id)
        if box_id == -1 :
            break

    with open(os.path.join(baseRoot, 'json/School_msg.json'), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(School_list, ensure_ascii=False, indent=4))
    with open(os.path.join(baseRoot, 'json/wrong_maj_id.json'), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(wrong_maj_id, ensure_ascii=False, indent=4))
    with open(os.path.join(baseRoot, 'json/wrong_maj_name.json'), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(wrong_maj_name, ensure_ascii=False, indent=4))
    with open(os.path.join(baseRoot, 'json/wrong_maj_place.json'), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(wrong_maj_place, ensure_ascii=False, indent=4))
    with open(os.path.join(baseRoot, 'json/wrong_maj_tuition.json'), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(wrong_maj_tuition, ensure_ascii=False, indent=4))
    with open(os.path.join(baseRoot, 'json/half_maj.json'), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(halfMajorList, ensure_ascii=False, indent=4))
    process_sch_msg(baseRoot)


def main():
    pass
    get_message('PC')


if __name__ == '__main__':
    main()
