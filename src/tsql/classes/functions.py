import os
from pathlib import Path


def snake_case(s):
    return s.lower().replace(' ', '_')


def pascal_case(s):
    return s.title().replace(' ', '').replace('_', '')


def rename(obj):
    res = ''
    valid = False
    while res == '' or valid == False:
        res = input(f'\nRename {obj.__name__} ({obj.name}): ')
        if obj.validate_name(res):
            valid = True
    obj.name = snake_case(res)

    if obj.__name__ == 'Table':
        obj.dataclass = pascal_case(res)


def get_name(obj):
    res = ''
    valid = False
    while res == '' or valid == False:
        res = input(f'\nName for new {obj.__name__}: ')
        if obj.validate_name(res):
            valid = True
    obj.name = snake_case(res)

    if obj.__name__ == 'Table':
        obj.dataclass = pascal_case(res)


def get_file_name(dir, name, ext):
    i = 0
    new_name = name + f'.{ext}'
    while new_name in os.listdir(Path(dir).absolute()):
        i += 1
        new_name = new_name.split('.')[0].split('-')[0] + f'-{i}.{ext}'
    return new_name.split('.')[0]

