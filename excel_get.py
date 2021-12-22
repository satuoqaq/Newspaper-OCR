import os.path

import json
import xlwt
import xlrd

baseRoot = 'PC3'


def get_sch_excel():
    data = xlrd.open_workbook(r'read2021.xls')
    print(data.sheet_names()[0])
    # print(data.sheet_names())
    Sch_excel = data.sheet_by_index(0)
    sch_num = Sch_excel.nrows
    Sch_msg1 = {}
    for i in range(1, sch_num):
        sch_batch = Sch_excel.cell(i, 3).value
        sch_id = int(Sch_excel.cell(i, 4).value)
        sch_id = str(sch_id).zfill(4)
        sch_name = Sch_excel.cell(i, 5).value
        sch_place = int(Sch_excel.cell(i, 6).value)
        sch_page = int(Sch_excel.cell(i, 7).value)
        print(sch_id, sch_name, sch_place, sch_batch, sch_page)
        sch_singer_id = str(sch_page).zfill(4) + sch_id
        Sch_msg1[sch_singer_id] = [sch_id, sch_name, sch_place, sch_batch, sch_page]

    with open(os.path.join(baseRoot, 'json/Sch_standard1.json'), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(Sch_msg1, ensure_ascii=False, indent=4))

    with open(os.path.join(baseRoot, 'json/School_msg.json'), 'r', encoding='UTF-8')as fp:
        sch_data = json.load(fp)

    Sch_msg2 = {}

    for i in range(0, len(sch_data)):
        sch = sch_data[i]
        sch_id = sch['id']
        sch_name = sch['name']
        sch_place = int(sch['place'])
        sch_batch = sch['batch']
        sch_page = sch['page_num']
        print(sch_id, sch_name, sch_place, sch_batch, sch_page)
        sch_singer_id = str(sch_page).zfill(4) + sch_id
        Sch_msg2[sch_singer_id] = [sch_id, sch_name, sch_place, sch_batch, sch_page]
    with open(os.path.join(baseRoot, 'json/Sch_standard2.json'), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(Sch_msg2, ensure_ascii=False, indent=4))


def get_maj_excel():
    Sch_msg1 = {}
    data = xlrd.open_workbook(r'read2021.xls')
    Maj_excel = data.sheet_by_index(1)
    for i in range(0, Maj_excel.nrows):
        sch_id = int(Maj_excel.cell(i, 4).value)
        sch_id = str(sch_id).zfill(4)
        if sch_id not in Sch_msg1.keys():
            Sch_msg1[sch_id] = {}
        maj_id = Maj_excel.cell(i, 6).value
        maj_name = Maj_excel.cell(i, 7).value
        maj_place = int(Maj_excel.cell(i, 8).value)
        maj_tuition = str(Maj_excel.cell(i, 10).value)
        if '0' <= maj_tuition[0] <= '9':
            maj_tuition = int(maj_tuition.split('.')[0])
        Sch_msg1[sch_id][maj_id] = [maj_name, maj_place, maj_tuition]
    with open(os.path.join(baseRoot, 'json/Maj_standard1.json'), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(Sch_msg1, ensure_ascii=False, indent=4))

    with open(os.path.join(baseRoot, 'json/School_msg.json'), 'r', encoding='UTF-8') as fp:
        sch_data = json.load(fp)

    Sch_msg2 = {}
    for i in range(0, len(sch_data)):
        sch = sch_data[i]
        sch_id = sch['id']
        if sch_id not in Sch_msg2.keys():
            Sch_msg2[sch_id] = {}
        for maj in sch['Major_list']:
            maj_id = maj['id']
            maj_name = maj['name']
            maj_place = int(maj['place'])
            maj_tuition = maj['tuition']
            if '0' <= maj_tuition[0] <= '9':
                maj_tuition = int(maj_tuition)
            Sch_msg2[sch_id][maj_id] = [maj_name, maj_place, maj_tuition]

    with open(os.path.join(baseRoot, 'json/Maj_standard2.json'), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(Sch_msg2, ensure_ascii=False, indent=4))


get_sch_excel()
get_maj_excel()
