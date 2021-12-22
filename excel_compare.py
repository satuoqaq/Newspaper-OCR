import os.path

import json
import xlwt
import xlrd
from P11_string_kmp import find_best_sch_match, find_best_maj_match

baseRoot = 'PC3'


def sch_name_change(name):
    pos = name.find('(')
    if pos != -1:
        name = name[:pos]
    pos = name.find('（')
    if pos != -1:
        name = name[:pos]
    return name


def sch_rate_check():
    with open(os.path.join(baseRoot, 'json/Sch_standard1.json'), 'r', encoding='UTF-8')as fp:
        sch_data1 = json.load(fp)
    with open(os.path.join(baseRoot, 'json/Sch_standard2.json'), 'r', encoding='UTF-8')as fp1:
        sch_data2 = json.load(fp1)
    all_sum = 0
    sch_num_sum = 0
    place_sum = 0
    name_sum = 0
    batch_sum = 0
    page_sum = 0
    for id in sch_data1:
        all_sum = all_sum + 1
        name = sch_data1[id][1]
        if id in sch_data2.keys():
            sch_num_sum = sch_num_sum + 1
            sch_id1, sch_name1, sch_place1, sch_batch1, sch_page1 = sch_data1[id]
            sch_id2, sch_name2, sch_place2, sch_batch2, sch_page2 = sch_data2[id]
            sch_name1 = sch_name_change(sch_name1)
            sch_name2 = sch_name_change(sch_name2)
            # 通过学校数据表找到最对应的那个
            if sch_name2.find(sch_name1) == -1:
                sch_name2 = find_best_sch_match(sch_name2)
                print('change_name', sch_name2)
            if sch_name2.find(sch_name1) != -1:
                name_sum = name_sum + 1
            else:
                print('name wrong:')
                print(sch_batch1, sch_id1, sch_name1, sch_place1)
                print(sch_batch2, sch_id2, sch_name2, sch_place2)
            if sch_place1 == sch_place2:
                place_sum = place_sum + 1
            else:
                print('place wrong:')
                print(sch_batch1, sch_id1, sch_name1, sch_place1)
                print(sch_batch2, sch_id2, sch_name2, sch_place2)
            if sch_batch1 == sch_batch2:
                batch_sum = batch_sum + 1
            else:
                print('batch wrong:')
                print(sch_batch1, sch_id1, sch_name1, sch_place1)
                print(sch_batch2, sch_id2, sch_name2, sch_place2)

            if sch_page1 == sch_page2:
                page_sum = page_sum + 1
            else:
                print('page wrong:')
                print(sch_batch1, sch_id1, sch_name1, sch_place1)
                print(sch_batch2, sch_id2, sch_name2, sch_place2)
        else:
            print('id:', id,'  name:',name)

    sch_num_ac_rate = float(sch_num_sum / all_sum) * 100
    place_ac_rate = float(place_sum / all_sum) * 100
    name_ac_rate = float(name_sum / all_sum) * 100
    batch_ac_rate = float(batch_sum / all_sum) * 100
    page_ac_rate = float(page_sum / all_sum) * 100

    print('sch_num_ac_rate:', sch_num_ac_rate, '%', all_sum - sch_num_sum)
    print('place_ac_rate:', place_ac_rate, '%', all_sum - place_sum)
    print('name_ac_rate:', name_ac_rate, '%', all_sum - name_sum)
    print('batch_ac_rate:', batch_ac_rate, '%', all_sum - batch_sum)
    print('page_ac_rate:', page_ac_rate, '%', all_sum - page_sum)


def maj_rate_check():
    with open(os.path.join(baseRoot, 'json/Maj_standard1.json'), 'r', encoding='UTF-8')as fp:
        sch_data1 = json.load(fp)
    with open(os.path.join(baseRoot, 'json/Maj_standard2.json'), 'r', encoding='UTF-8')as fp1:
        sch_data2 = json.load(fp1)
    all_sum = 0
    maj_sum = 0
    name_sum = 0
    place_sum = 0
    tuition_sum = 0
    for sch_id1 in sch_data1:
        all_sum = all_sum + len(sch_data1[sch_id1])
        if sch_id1 in sch_data2.keys():
            maj_list1 = sch_data1[sch_id1]
            maj_list2 = sch_data2[sch_id1]
            for maj_id1 in maj_list1:
                if maj_id1 in maj_list2:
                    # print(sch_id1, maj_id1, '√')
                    maj_sum = maj_sum + 1
                    maj_name1, maj_place1, maj_tuition1 = maj_list1[maj_id1]
                    maj_name2, maj_place2, maj_tuition2 = maj_list2[maj_id1]
                    maj_name1 = sch_name_change(maj_name1)
                    maj_name2 = sch_name_change(maj_name2)
                    # maj_name2 = find_best_maj_match(maj_name2)
                    # 通过专业数据表找到最对应的那个
                    # if maj_name2.find(maj_name1) == -1:
                    #     print(maj_name1,maj_name2)
                    #     maj_name2 = find_best_maj_match(maj_name2)
                    #     print(maj_name1, maj_name2)
                    #     print('**********')
                    if maj_name2.find(maj_name1) != -1:
                        name_sum = name_sum + 1
                    else:
                        pass
                        # print('name wrong:')
                        # print(maj_id1, maj_name1, maj_place1, maj_tuition1)
                        # print(maj_id1, maj_name2, maj_place2, maj_tuition2)
                        # print('nnnnnnnnnnnnnnn')
                    if maj_place1 == maj_place2:
                        place_sum = place_sum + 1
                    else:
                        pass
                        # print('place wrong:')
                        # print(maj_id1, maj_name1, maj_place1, maj_tuition1)
                        # print(maj_id1, maj_name2, maj_place2, maj_tuition2)
                        # print('ppppppppppppppp')
                    if type(maj_tuition1) == type(maj_tuition2):
                        if maj_tuition1 == maj_tuition2:
                            tuition_sum = tuition_sum + 1
                        else:
                            pass
                            # print('tuition wrong:')
                            # print(maj_id1, maj_name1, maj_place1, maj_tuition1)
                            # print(maj_id1, maj_name2, maj_place2, maj_tuition2)
                            # print('ttttttttttttttt')
                    else:
                        pass
                        # print('tuition type_wrong')
                        # print(maj_id1, maj_name1, maj_place1, maj_tuition1)
                        # print(maj_id1, maj_name2, maj_place2, maj_tuition2)
                        # print('------------')1
                else:
                    pass
                    print(sch_id1, maj_id1, '×')

    maj_id_ac_sum = float(maj_sum / all_sum) * 100
    name_ac_rate = float(name_sum / all_sum) * 100
    place_ac_sum = float(place_sum / all_sum) * 100
    tuition_ac_sum = float(tuition_sum / all_sum) * 100

    print('maj_id_ac_rate:', maj_id_ac_sum, '%', all_sum - maj_sum)
    print('name_ac_rate:', name_ac_rate, '%', all_sum - name_sum)
    print('place_ac_rate:', place_ac_sum, '%', all_sum - place_sum)
    print('tuition_ac_rate:', tuition_ac_sum, '%', all_sum - tuition_sum)


sch_rate_check()
maj_rate_check()
