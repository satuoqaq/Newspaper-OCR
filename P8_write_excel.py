import os.path
import json
import xlwt
from P0_init import conf


def get_year(name, sch_batch):
    if sch_batch == '专科':
        return 3
    if name.find('7+X') != -1 or name.find('本硕连读') != -1:
        return 7
    if name.find('IX') != -1 or name.find('九年') != -1 or name.find('9年') != -1:
        return 9
    if name.find('Vm') != -1 or name.find('vm') != -1 or name.find('本硕博') != -1 or name.find('8年') != -1 or name.find(
            '八年') != -1 or name.find('本博连读') != -1:
        return 8
    if name.find('Ⅱ') != -1 or name.find('[I]') != -1:
        return 2
    if name.find('医学') != -1 or name.find('V') != -1:
        return 5
    return 4


def write_excel(startRoot, baseRoot):
    with open(os.path.join(baseRoot, 'json/School_msg.json'), 'r', encoding='UTF-8') as fp:
        sch_data = json.load(fp)
    with open(os.path.join(baseRoot, 'json/page_msg.json'), 'r', encoding='UTF-8') as fp1:
        page_data = json.load(fp1)

    # pro = ['招生代码', '学校名称', '计划人数', '检测计划人数', '图片页码', '学校备注']
    pro = ['年份', '高考省份', '科类', '录取批次', '招生代码', '学校名称', '计划人数', '检测计划人数', '学校所在页', '图片页码', '学校备注']
    # pro1 = ['招生代码', '学校名称', '专业代码', '专业名称', '计划人数', '学费', '专业备注']
    pro1 = ['年份', '高考省份', '科类', '录取批次', '招生代码', '学校名称', '专业招生代码', '专业名称', '计划人数', '学制', '学费', '报纸页码数', '图片页码数', '专业备注']
    book = xlwt.Workbook()
    sheet = book.add_sheet('Sheet1')
    sheet2 = book.add_sheet('Sheet2')
    # sheet的头
    for i in range(0, len(pro)):
        sheet.write(0, i, pro[i])
    for i in range(0, len(pro1)):
        sheet2.write(0, i, pro1[i])
    num = 1
    for i in range(0, len(sch_data)):
        sch = sch_data[i]
        url = "file:///" + os.path.abspath(os.path.join(startRoot, sch['page_name']))
        formula = 'HYPERLINK("{}", "{}")'.format(url, sch['page_name'])
        sheet.write(i + 1, 0, conf['Year'])
        sheet.write(i + 1, 1, conf['Province'])
        sheet.write(i + 1, 2, conf['AS'])
        sheet.write(i + 1, 3, sch['batch'])
        sheet.write(i + 1, 4, sch['id'])
        sheet.write(i + 1, 5, sch['name'])
        sheet.write(i + 1, 6, int(sch['place']))
        sheet.write(i + 1, 8, sch['page_num'])
        sheet.write(i + 1, 9, xlwt.Formula(formula))
        sum_place = 0
        maj_list = sch['Major_list']
        for j in range(0, len(maj_list)):
            maj = maj_list[j]
            sheet2.write(num, 0, 2020)
            sheet2.write(num, 1, '四川')
            sheet2.write(num, 2, conf['AS'])
            sheet2.write(num, 3, sch['batch'])
            sheet2.write(num, 4, sch['id'])
            sheet2.write(num, 5, sch['name'])
            sheet2.write(num, 6, maj['id'])
            sheet2.write(num, 7, maj['name'])
            sheet2.write(num, 8, int(maj['place']))
            sheet2.write(num, 9, get_year(maj['name'], sch['batch']))
            sheet2.write(num, 10, maj['tuition'])
            sheet2.write(num, 11, page_data[maj['page_name']]['page_number'])
            sheet2.write(num, 12, xlwt.Formula(formula))
            if maj['place'] != '0' and len(maj['id']) == 2:
                sheet2.write(num, 13, 'ac')
            elif maj['place'] == '0':
                sheet2.write(num, 13, '未检测到专业名额')
            else:
                sheet2.write(num, 13, '专业名出错')
            sum_place = sum_place + int(maj['place'])
            num = num + 1
        sheet.write(i + 1, 7, sum_place)
        if sum_place != int(sch['place']):
            sheet.write(i + 1, 10, '专业统计错误')
            print(sch['page_name'], ',', sch['name'], ':出错需修查')
        else:
            sheet.write(i + 1, 10, 'AC')

    book.save(os.path.join(baseRoot, 'ans.xls'))
    print('已成功写入excel!')


def main():
    write_excel('PC3/HP', 'PC3')


if __name__ == "__main__":
    main()
