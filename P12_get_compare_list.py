import json


def get_sch_compare_list():
    with open('json/Sch_standard1.json', 'r', encoding='UTF-8') as fp:
        sch_msg = json.load(fp)

    School_Standard_List = []
    for sch in sch_msg:
        School_Standard_List.append(sch_msg[sch][1])

    print(School_Standard_List)

    with open('json/Sch_Standard_Compare_List.json', 'w', encoding='UTF-8') as f:
        f.write(json.dumps(School_Standard_List, ensure_ascii=False,indent=4))


def get_maj_compare_list():
    with open('Maj_standard1.json', 'r', encoding='UTF-8') as fp:
        sch_msg = json.load(fp)

    Major_Standard_List = []
    for sch in sch_msg:
        maj_dict = sch_msg[sch]
        for id in maj_dict:
            maj_name = maj_dict[id][0]
            if maj_name not in maj_dict:
                Major_Standard_List.append(maj_name)
    print(Major_Standard_List)

    with open('json/Maj_Standard_Compare_List.json', 'w', encoding='UTF-8') as f:
        f.write(json.dumps(Major_Standard_List, ensure_ascii=False,indent=4))


def main():
    get_sch_compare_list()
    get_maj_compare_list()


if __name__ == "__main__":
    main()
