import os.path

import json


def maj_name_fixed(name):
    name = name.replace('【', '[')
    name = name.replace('】', ']')
    name = name.replace('（', '(')
    name = name.replace('）', ')')
    pos1, pos2 = 0, len(name)
    for i in range(len(name)):
        if '\u4e00' <= name[i] <= '\u9fff' or name[i] == '[':
            pos1 = i
            break

    for i in range(len(name) - 1, -1, -1):
        if '\u4e00' <= name[i] <= '\u9fff' or name[i] == ')':
            pos2 = i + 1
            break
    name = name[pos1:pos2]
    return name


def process_sch_msg(baseRoot):
    # 取出统计的学校信息
    json_schMsg_name = os.path.join(baseRoot, 'json/School_msg.json')
    with open(json_schMsg_name, 'r', encoding='UTF-8')as fp:
        sch_data = json.load(fp)

    # 将所有专业id里出现'O'的替换为'0'
    for i in range(0, len(sch_data)):
        sch = sch_data[i]
        maj_list = sch['Major_list']
        for j in range(0, len(maj_list)):
            maj = maj_list[j]
            maj['name'] = maj_name_fixed(maj['name'])
            if 'O' in maj['id']:
                old_id = maj['id']
                maj['id'] = maj['id'].replace('O', '0')
                print(old_id, maj['id'])
            maj_list[j] = maj

    with open(json_schMsg_name, 'w', encoding='UTF-8') as f:
        f.write(json.dumps(sch_data, ensure_ascii=False, indent=4))


def main():
    process_sch_msg()


if __name__ == "__main__":
    main()
