import time
import tkinter as tk
from tkinter.filedialog import askdirectory
import os

from P1_img_roation import get_roa_img
from P2_img_split import get_com_line
from P3_get_full_line import get_full_line
from P4_get_box_and_rec import getBoxAndRecognize
from P5_get_topBarMsg import get_topbar_data
from P6_get_message import get_message
from P7_fix_wrong_msg import fix_wrong_msg
from P8_write_excel import write_excel
from recheck_board import CheckBoard


def make_dir(dir_list):
    for name in dir_list:
        print(name)
        if not os.path.exists(name):
            os.mkdir(name)


class Paths:
    # 这两个是自己选的路径  一个是图像原始图像的位置 一个是存储所有东西的位置
    openBaseImgPath = 'PC3/HP'
    saveBaseRoot = 'PC3'

    def __init__(self):
        self.jsonPath = None
        self.boxImgPath = None
        self.roaSplitImgPath = None
        self.lineImgPath = None
        self.roaImgPath = None

    def init(self):
        # 所有的东西都存到相应saveBaseRoot位置下边
        self.roaImgPath = os.path.join(self.saveBaseRoot, 'HP_roa')
        self.lineImgPath = os.path.join(self.saveBaseRoot, 'HP_line')
        self.roaSplitImgPath = os.path.join(self.saveBaseRoot, 'HP_roa_split')
        self.boxImgPath = os.path.join(self.saveBaseRoot, 'HP_box')
        self.jsonPath = os.path.join(self.saveBaseRoot, 'json')
        dirList = [self.roaImgPath, self.lineImgPath, self.roaSplitImgPath, self.boxImgPath, self.jsonPath]
        make_dir(dirList)


PATHS = Paths()


def main_window():
    # 界面布局
    window = tk.Tk()
    window.title('招生考试报识别')  # 窗口标题
    window.geometry('350x320')  # 窗口大小
    window.resizable(0, 0)  # 禁止调整窗口大小
    tk.Label(window, text=" ").grid(row=1, padx=30)  # 第1行，第一列
    tk.Label(window, text="招生考试报OCR识别程序").grid(row=2, column=2, padx=30)  # 第2行，第二列
    tk.Label(window, text=" ").grid(row=3, padx=30)  # 第3行，第一列
    choose_input_button = tk.Button(
        window, text='01.选择原图文件夹', command=click_input_dir)  # 点击时调用函数click_dir
    choose_input_button.grid(
        row=4, column=1, columnspan=2, ipadx=40, pady=5)  # 第4行，第一列
    choose_output_button = tk.Button(
        window, text='02.选择输出文件夹', command=click_output_dir)
    choose_output_button.grid(
        row=5, column=1, columnspan=2, ipadx=40, pady=5)
    step1_button = tk.Button(
        window, text='1.处理图片', command=click_step1)
    step1_button.grid(
        row=6, column=1, columnspan=2, ipadx=40, pady=5)
    step2_button = tk.Button(
        window, text='2.检查页码', command=click_step2)
    step2_button.grid(
        row=7, column=1, columnspan=2, ipadx=40, pady=5)
    step3_button = tk.Button(
        window, text='3.得到学校信息并纠错', command=click_step3)
    step3_button.grid(
        row=8, column=1, columnspan=2, ipadx=40, pady=5)
    step4_button = tk.Button(
        window, text='4.写入excel', command=click_step4)
    step4_button.grid(
        row=9, column=1, columnspan=2, ipadx=40, pady=5)
    window.mainloop()


def click_input_dir():
    dir_path = askdirectory()
    if dir_path:
        PATHS.openBaseImgPath = dir_path
    print('dir_path:', dir_path if dir_path else '!!User cancelled!!')


def click_output_dir():
    dir_path = askdirectory()
    if dir_path:
        PATHS.saveBaseRoot = dir_path
    print('dir_path:', dir_path if dir_path else '!!User cancelled!!')


def click_step1():
    t = time.time()
    PATHS.init()
    get_roa_img(PATHS.openBaseImgPath, PATHS.roaImgPath)
    get_com_line(PATHS.saveBaseRoot, PATHS.roaImgPath, PATHS.roaSplitImgPath)
    get_full_line(PATHS.saveBaseRoot, PATHS.roaImgPath, PATHS.lineImgPath)
    getBoxAndRecognize(PATHS.saveBaseRoot, PATHS.roaImgPath, PATHS.boxImgPath)
    print(time.time() - t)


def click_step2():
    get_topbar_data(PATHS.saveBaseRoot)


def click_step3():
    get_message(PATHS.saveBaseRoot)
    CheckBoard.fix_wrong_msg(PATHS.saveBaseRoot)


def click_step4():
    write_excel(PATHS.saveBaseRoot)


if __name__ == '__main__':
    main_window()
