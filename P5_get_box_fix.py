import json

save_json_path = 'json/box1.json'

with open(save_json_path, 'r')as fp:
    box_data = json.load(fp)

for page_name in box_data:
    page = box_data[page_name]
    # for i in range(len(page) - 1, -1, -1):
    for i in range(0, len(page)):
        box = page[i]
        if box['down'] - box['up'] > 120:
            print(box['page_name'], box['text'])
            # page.remove(box)
#
# with open('box.json', 'w', encoding='UTF-8') as f:
#     f.write(json.dumps(box_data, ensure_ascii=False,indent=4))
