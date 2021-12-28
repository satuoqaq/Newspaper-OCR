import yaml

with open('config.yaml', 'r', encoding='UTF-8') as f:
    conf = yaml.load(f, Loader=yaml.FullLoader)
