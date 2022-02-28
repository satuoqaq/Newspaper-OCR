import json
import cv2
import numpy as np
import os
import tkinter as tk
from tkinter.messagebox import showinfo
from PIL import Image, ImageTk


class CheckBoard:
    window = tk.Tk()
    # 制定图片以及文字框
    window.geometry('1000x400')  # 窗口大小
    window.resizable(0, 0)  # 禁止调整窗口大小
    img_w = 800
    label_img = tk.Label(window, width=img_w, height=2, bg="white")
    text_page_number = tk.Entry(window)
    text_major_id = tk.Entry(window)
    text_major_name = tk.Entry(window)
    text_major_place = tk.Entry(window)
    text_major_tuition = tk.Entry(window)
    button_last_img = tk.Button(window, text='上一张')
    button_next_img = tk.Button(window, text='下一张')
    button_finish = tk.Button(window, text='完成')
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
        cls.button_last_img.config(command=cls.click_last_page)
        cls.button_last_img.pack(fill=tk.X, pady=5)
        cls.button_next_img.config(command=cls.click_next_page)
        cls.button_next_img.pack(fill=tk.X, pady=5)
        cls.button_finish.config(command=cls.click_finish)
        cls.button_finish.pack(fill=tk.X, pady=5)
        # 设置背景颜色
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
        showinfo('检查完成', '已完成所有需要检查的项目,保存成功')
        cls.window.destroy()

    @classmethod
    # 保存修改信息
    def save_current_message(cls):
        # 保存当前修改的信息 id & name
        cls.editing_maj['id'] = cls.text_major_id.get()
        cls.editing_maj['name'] = cls.text_major_name.get()
        cls.editing_maj['place'] = cls.text_major_place.get()
        cls.editing_maj['tuition'] = cls.text_major_tuition.get()
        print(cls.editing_maj)
        cls.norm_data[cls.editing_maj['sch_index']]['Major_list'][cls.editing_maj['maj_index']] = cls.editing_maj

    @classmethod
    # 保存并且翻到上一张去
    def click_last_page(cls):
        cls.save_current_message()
        # 上一张
        if cls.fix_what == 'id':
            if cls.major_id > 0:
                cls.major_id -= 1
            else:
                showinfo('error', '已经是第一条信息了')
        elif cls.fix_what == 'place':
            if cls.major_place > 0:
                cls.major_place -= 1
            else:
                showinfo('', '已经是最后一条信息了')
        cls.main_edit()

    @classmethod
    # 保存并且翻到下一张去
    def click_next_page(cls):
        cls.save_current_message()
        # 下一张
        if cls.fix_what == 'id':
            if cls.major_id + 1 < cls.total_major_id_num:
                cls.major_id += 1
            else:
                showinfo('', '已经是最后一条信息了')
        elif cls.fix_what == 'place':
            if cls.major_place + 1 < cls.total_major_place_num:
                cls.major_place += 1
            else:
                showinfo('', '已经是最后一条信息了')
        cls.main_edit()

    @classmethod
    # 点击完成表示这种错误核查完毕
    def click_finish(cls):
        cls.save_current_message()
        if cls.fix_what == 'id':
            if cls.total_major_place_num:
                cls.fix_what = 'place'
                showinfo('提示', '开始核查专业名额错误')
                cls.main_edit()
            else:
                cls.end_message_box()
        elif cls.fix_what == 'place':
            cls.end_message_box()

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

        # with open(os.path.join(baseRoot, 'json/wrong_maj_id.json'), 'r', encoding='UTF-8') as fp:
        #     cls.id_infos = json.load(fp)
        #
        # with open(os.path.join(baseRoot, 'json/wrong_maj_place.json'), 'r', encoding='UTF-8') as fp1:
        #     cls.place_infos = json.load(fp1)
        #
        # with open(os.path.join(baseRoot, 'json/School_msg.json'), 'r', encoding='UTF-8') as fp4:
        #     cls.norm_data = json.load(fp4)
        #
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
        if cls.total_major_id_num == 0:
            cls.fix_what = 'place'
            if cls.total_major_place_num == 0:
                showinfo('核查完成', '没有需要修改的信息')
                return
        cls.base_root_path = baseRoot
        cls.roa_path = os.path.join(baseRoot, 'HP_roa')
        cls.main_edit()
        cls.window.mainloop()


if __name__ == '__main__':
    CheckBoard.fix_wrong_msg("PC2")
