import json
import cv2
import numpy as np
import os
import tkinter as tk
from tkinter.messagebox import showinfo
from PIL import Image, ImageTk
import torch


class CheckBoard:
    window = tk.Tk()
    window.geometry('1000x400')  # 窗口大小
    img_w = 800
    label_img = tk.Label(window, width=img_w, height=2, bg="white")
    text_page_number = tk.Entry(window)
    text_major_id = tk.Entry(window)
    text_major_name = tk.Entry(window)
    text_major_place = tk.Entry(window)
    text_major_tuition = tk.Entry(window)
    button_next_img = tk.Button(window, text='下一张')

    id_infos = None
    place_infos = None
    norm_data = None
    editing_maj = None
    roa_path = None
    base_root_path = None
    fix_what = 'id'
    major_id = 0
    total_major_id_num = 0
    major_place = 0
    total_major_place_num = 0

    @classmethod
    def init_board_window(cls):
        # 界面布局
        cls.window.title('招生考试报识别-人工检查')  # 窗口标题
        cls.label_img.pack(fill=tk.Y, side=tk.LEFT)
        tk.Label(cls.window, text="页码").pack(fill=tk.X)
        cls.text_page_number.pack(fill=tk.X)
        tk.Label(cls.window, text="专业ID").pack(fill=tk.X)
        cls.text_major_id.pack(fill=tk.X)
        tk.Label(cls.window, text="专业名称").pack(fill=tk.X)
        cls.text_major_name.pack(fill=tk.X)
        tk.Label(cls.window, text="专业名额").pack(fill=tk.X)
        cls.text_major_place.pack(fill=tk.X)
        tk.Label(cls.window, text="专业学费").pack(fill=tk.X)
        cls.text_major_tuition.pack(fill=tk.X)
        tk.Label(cls.window, text=" ").pack(fill=tk.X)
        cls.button_next_img.config(command=cls.click_next_page)
        cls.button_next_img.pack(fill=tk.X)

        img = np.zeros((1, 800, 3), np.uint8)
        img.fill(255)
        cls.edit_img_label_img(img)

    @classmethod
    def load_major_img(cls, img_root_dir, major_info):
        """
        使用opencv读取专业图片
        :param img_root_dir: 图片文件夹
        :param major_info: {'left', 'right', 'up', 'down'}
        :return: img
        """
        page_name = major_info['page_name']
        img_path = os.path.join(img_root_dir, page_name)

        img = cv2.imread(img_path)
        left = max(0, major_info['left'] - 100)
        right = min(major_info['right'] + 100, img.shape[1])
        up = max(0, major_info['up'] - 50)
        down = min(major_info['down'] + 50, img.shape[0])

        img = img[up:down, left:right]
        img = cv2.resize(img, (int(img.shape[1] * 0.5), int(img.shape[0] * 0.5)))
        return img

    @classmethod
    def edit_img_label_img(cls, img):
        img = cv2.resize(img, (cls.img_w, int(img.shape[0] * cls.img_w / img.shape[1])))

        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)  # 转换颜色从BGR到RGBA
        current_image = Image.fromarray(cv2image)  # 将图像转换成Image对象
        imgtk = ImageTk.PhotoImage(image=current_image)

        cls.label_img.imgtk = imgtk
        cls.label_img.config(image=imgtk)

    @classmethod
    def end_message_box(cls):
        savePath = os.path.join(cls.base_root_path, 'json/School_msg.json')
        with open(savePath, 'w', encoding='UTF-8') as f:
            f.write(json.dumps(cls.norm_data, ensure_ascii=False, indent=4))
        showinfo('检查完成', '已完成所有需要检查的项目')
        cls.window.destroy()

    @classmethod
    def click_next_page(cls):
        # 保存当前修改的信息 id & name
        cls.editing_maj['id'] = cls.text_major_id.get()
        cls.editing_maj['name'] = cls.text_major_name.get()
        cls.editing_maj['place'] = cls.text_major_place.get()
        cls.editing_maj['tuition'] = cls.text_major_tuition.get()
        print(cls.editing_maj)
        cls.norm_data[cls.editing_maj['sch_index']]['Major_list'][cls.editing_maj['maj_index']] = cls.editing_maj
        # 下一张
        if cls.fix_what == 'id':
            cls.major_id += 1
            if cls.major_id >= cls.total_major_id_num:
                cls.fix_what = 'place'
        elif cls.fix_what == 'place':
            cls.major_place += 1
            if cls.major_place >= cls.total_major_place_num:
                cls.end_message_box()
                return
        cls.main_edit()

    @classmethod
    def main_edit(cls):
        # maj = None
        if cls.fix_what == 'id' and cls.major_id < len(cls.id_infos):
            cls.window.title('招生考试报识别-专业id人工检查 {}/{}'.format(cls.major_id + 1, cls.total_major_id_num))
            maj = cls.id_infos[cls.major_id]
        elif cls.fix_what == 'place' and cls.major_place < len(cls.place_infos):
            cls.window.title('招生考试报识别-专业名额人工检查 {}/{}'.format(cls.major_place + 1, cls.total_major_place_num))
            maj = cls.place_infos[cls.major_place]
        else:
            showinfo('检查完成', '已完成所有需要检查的项目')
            maj = None

        cls.editing_maj = maj

        img = cls.load_major_img(cls.roa_path, maj)
        cls.edit_img_label_img(img)

        cls.text_page_number.delete(0, 'end')
        cls.text_page_number.insert(0, str(maj['page_name']))
        cls.text_major_id.delete(0, 'end')
        cls.text_major_id.insert(0, str(maj['id']))
        cls.text_major_name.delete(0, 'end')
        cls.text_major_name.insert(0, str(maj['name']))
        cls.text_major_place.delete(0, 'end')
        cls.text_major_place.insert(0, str(maj['place']))
        cls.text_major_tuition.delete(0, 'end')
        cls.text_major_tuition.insert(0, str(maj['tuition']))

    @classmethod
    def fix_wrong_msg(cls, baseRoot):
        cls.init_board_window()

        with open(os.path.join(baseRoot, 'json/wrong_maj_id.json'), 'r', encoding='UTF-8') as fp:
            cls.id_infos = json.load(fp)

        with open(os.path.join(baseRoot, 'json/wrong_maj_place.json'), 'r', encoding='UTF-8') as fp1:
            cls.place_infos = json.load(fp1)

        with open(os.path.join(baseRoot, 'json/School_msg.json'), 'r', encoding='UTF-8') as fp4:
            cls.norm_data = json.load(fp4)

        cls.major_id = 0
        cls.total_major_id_num = len(cls.id_infos)
        cls.major_place = 0
        cls.total_major_place_num = len(cls.place_infos)
        cls.base_root_path = baseRoot
        cls.roa_path = os.path.join(baseRoot, 'HP_roa')
        cls.main_edit()
        cls.window.mainloop()


if __name__ == '__main__':
    CheckBoard.fix_wrong_msg("PC2")
