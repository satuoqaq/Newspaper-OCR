import difflib
import json

with open('json/Sch_Standard_Compare_List.json', 'r', encoding='UTF-8') as fp:
    sch_list = json.load(fp)
with open('json/Maj_Standard_Compare_List.json', 'r', encoding='UTF-8') as fp:
    maj_list = json.load(fp)


def find_best_maj_match(maj_name):
    new_maj_name = difflib.get_close_matches(maj_name, maj_list, 5, cutoff=0.7)
    print(new_maj_name)
    if len(new_maj_name) != 0:
        return new_maj_name[0]
    return maj_name


def find_best_sch_match(sch_name):
    new_sch_name = difflib.get_close_matches(sch_name, sch_list, 1, cutoff=0.7)
    if len(new_sch_name) != 0:
        return new_sch_name[0]
    else:
        return sch_name


def main():
    print(find_best_sch_match('伊型职业技术学院'))


if __name__ == "__main__":
    main()
