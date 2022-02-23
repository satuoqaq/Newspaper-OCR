# import tkinter as tk
#
# import os
#
# window = tk.Tk()
# window.geometry('1000x400')
# window.title('学习tk')
# img_w = 800
# label_img = tk.Label(window, width=img_w, height=2, bg='pink')
# label_img.pack()
# # text_page_number = tk.Entry(window)
# # text_major_id = tk.Entry(window)
# # text_major_name = tk.Entry(window)
# # text_major_place = tk.Entry(window)
# # text_major_tuition = tk.Entry(window)
# # text_page_number.pack()
# # text_major_id.pack()
# # text_major_name.pack()
# # text_major_place.pack()
# # text_major_tuition.pack()
# button_next_img = tk.Button(window, text='下一张')
# button_next_img.pack()
# window.mainloop()

import torch
print(torch.cuda.is_available())
