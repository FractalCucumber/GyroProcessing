
# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

from time import perf_counter
import os
import re

to_replace = 'menu'
replace = u'меню'
# print('12 3'.replace('1', '2'))
# exit()
folder = 'D:/GyroResultsProcessing/ttt'#os.getcwd() 
for path in os.scandir(folder):
    print(path, path.name)
    if not path.is_file() or path.name == 'TEXT_REPLACER.py': continue
    with open(path, encoding='utf-8') as file:
        text = file.read()
    res = re.findall(to_replace, text)
    print(res)
    print('text before:\n', text)
    for r in res:
        print('text1:\n', text, r)
        text = text.replace(r, replace, 1)
    print('\ntext after:\n', text)
    print('\n')
    with open(path, mode='w', encoding='utf-8') as file:
        file.write(text)