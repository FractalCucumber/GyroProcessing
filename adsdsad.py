
from time import perf_counter, sleep
import os
from pympler import asizeof
from memory_profiler import profile
# i = 1
# print(i, id(i))
# i += 1
# print(i, id(i))
# import numpy as np
# i = np.array([22, 44])
# print(i, id(i))
# i += 5
# print(i, id(i))
# exit(-1)
import itertools
# print(list(itertools.product(*[['123','323'], ['23','55','-50'], range(1,6)])))

path = 'D:/Work/Gyro2023_Git/Test (2).xlsm'
t = perf_counter()
import numpy as np
print('t = ', perf_counter() - t)
t = perf_counter()
import polars as pl
print('t = ', perf_counter() - t)
t = perf_counter()
import pandas as pd
print('t = ', perf_counter() - t)

# print('asizeof(pl)', asizeof(pl.Int32))
# t = perf_counter()
# df = pl.read_excel(path, sheet_name='Настройка КП', engine='calamine')
# print('t = ', perf_counter() - t)
# print('df = ', df)
# # Создаем DataFrame с данными
# data = {'name': ['Alice', 'Bob', 'Charlie'], 'age': [25, 30, 35]}
# df = pl.DataFrame(data) ; print(df)
# named_tuple = df['name']
# pl.read_csv('D:/Work/Gyro2023_Git/6884_139_6.2_3.txt', has_header=False,
#                  separator='\t', use_pyarrow=True)
# pd.read_csv('D:/Work/Gyro2023_Git/6884_139_6.2_3.txt', header=None,
#                  sep='\t', engine='pyarrow')
# print(named_tuple)
# pd.DataFrame.to_csv()
# df=  

sleep(0.1)
t = perf_counter()
# t = perf_counter()
# for i in range(50):
# print('read_csv t = ', perf_counter() - t)
# @profile
def do(f, n=50):
    if f == 1:
        t = perf_counter()
        for _ in range(n):
            df = pl.read_csv('D:/Work/Gyro2023_Git/6884_139_6.2_5.txt',
                            has_header=False,
                            separator='\t',
                            # n_threads=16,
                            # batch_size=512, sample_size=256,
                            schema_overrides=[pl.Int32, pl.Int32, pl.Int32, pl.Int16, pl.Int16], 
                            low_memory=True,
                            # encoding='ascii', #'utf-8',
                            use_pyarrow=True
                            )#.to_numpy()
        print(f'pl read_csv t = {perf_counter() - t:.4f}')
        res = df.estimated_size() #pl.DataFrame.estimated_size()
        print(f's.estimated_size = {res} bytes, {(res / 1024):.1f} KB')
        print(f's.size = {df.shape}, df.dtypes = {df.dtypes}\n')
        lll = [df.clone() for _ in range(20)]
        print(df)
        print(df.select(pl.col('column_5')))
        print(df.select('column_5').to_numpy().dtype)
        import polars.selectors as cs
        print(df.select(cs.by_index(range(1, 3))))
        print(df.select(pl.nth(range(0, 2))))
        print(df.select(pl.nth([0, 4])))
        # print(df.select(pl.nth(range(0, 2))).to_numpy().dtype)
    else:
        t = perf_counter()
        for _ in range(n):
            df = pd.read_csv('D:/Work/Gyro2023_Git/6884_139_6.2_5.txt', header=None,
                            #   index_col=[0],
                              dtype=np.int32,
                              delimiter='\t',
                              low_memory=True,
                              engine='pyarrow'
                              )#.to_numpy() #, dtype=np.int32) #, na_filter=False)
        print(f'pdread_csv t = {perf_counter() - t:.4f}')
        res = df.info() #pl.DataFrame.estimated_size()
        print(f's.info = {res}')
        print(f's.size = {df.shape}, df.dtypes = {df.dtypes}\n')
        lll = [df.copy(True) for _ in range(20)]
    try:
        res = asizeof.asizeof(df)
        print(f's.size = {res} bytes, {(res / 1024):.1f} KB\n')
    except Exception: pass
    return df, lll

# @profile
def do2(f, df):
    if f == 1:
        t = perf_counter()
        pl.DataFrame.write_csv(df, 
                            'D:/Work/Gyro2023_Git/pl_test.txt',
                                separator='\t',
                                # batch_size=512,
                                include_bom=False,
                                include_header=False
                            )
        print(f'pl write_csv t = {perf_counter() - t:.4f}')
    else:
        t = perf_counter()
        pd.DataFrame.to_csv(df, 
                    'D:/Work/Gyro2023_Git/pd_test.txt',
                        mode='w', 
                        sep='\t',
                        # chunksize=512,
                        # float_format='%.3f', decimal=',',
                        header=None, index=None
                    )
        print(f'pd to_csv t = {perf_counter() - t:.4f}')

df, lll = do(1, n=1)
do2(1, df=df)
# print(df) 
# Создаем именованный кортеж на основе столбца 'name'
# import fastexcel as fe
# import python_calamine as pc
# sleep(0.1)
# sleep(0.1)
# df1 = pd.read_excel('D:/Work/Gyro2023_Git/123.xlsm', sheet_name='Настройка КП', engine='calamine')
# t = perf_counter()
# for i in range(50):
#     df1 = pd.read_excel(path, sheet_name='Настройка КП', engine='calamine')
# print('read_excel t = ', perf_counter() - t)
# sleep(0.1)
# df2 = pl.read_excel('D:/Work/Gyro2023_Git/123.xlsm', sheet_name='Настройка КП', engine='calamine') #, parse_dates=False)
# t = perf_counter()
# for i in range(50):
#     df2 = pl.read_excel(path, sheet_name='Настройка КП', engine='calamine') #, parse_dates=False)
# print('read_excel t = ', perf_counter() - t)
sleep(10)
exit(-2)
# arrays = [["bar", "bar", "baz", "baz", "foo", "foo", "qux", "qux"],
#     ["one", "two", "one", "two", "one", "two", "one", "two"], ]
# tuples = list(zip(*arrays))
# index = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])
iterables = [
    ["111", "321"] , #, "113", "114"],
    ["23", "50", '-50'],
    ["1", "2", "3", "4", "5"]
    ]
index = pd.MultiIndex.from_product(
    iterables, names=["s name", "temp", "n"])
print(index.dtype) ; print(index.codes) # print(index.array)
print(index.nbytes) ; print(index.ndim) ; print(index.shape) ; print(index.size)
print(index)
iterables = [
    ["channel 1", "channel 2"],
    ["shift", "small shift", "std"]
    ]
index2 = pd.MultiIndex.from_product(
    iterables, names=["channel", "param"])

idx = pd.IndexSlice
s = pd.DataFrame(
    # np.random.randn(8, 8), # будет NaN
    index=index, columns=index2, dtype=np.float64)
print('-----------------------------------------')
print('-----------------------------------------')
# print(index.droplevel("s name"))
print(index.droplevel(level=["s name"]))
print(index.droplevel(level=["s name"]).to_list())
print(index.droplevel(level=["s name"]).drop_duplicates())
print(index.droplevel(level=["s name"]).drop_duplicates().to_list())
# print(s.columns.droplevel("s name").to_list())
# # print(s.groupby(level=0))
# print(s.index) ; print(s.columns)
# exit(-1)
print('-----------------------------------------')
print(s)
print(f's.size = {s.size}')
print(f's.size = {asizeof.asizeof(s)} bytes, {asizeof.asizeof(s) / 1024:.1f} KB')
print('-----------------------------------------')
s.loc[(slice(None), '23', '1'), ('channel 1', 'shift')] = [[6], [2]]
s.loc[idx[:, '23', '1'], idx['channel 1', 'shift']] = [[16], [12]]
print(s.xs('111', level="s name")['channel 1'])
# i = pd.Index(["1", "3"], name="s name")
# s.xs('1', level='name')['10']  = [[6, 4, 1, 1], [6, 4, 1, 1]]
print('-----------------------------------------')
print(s.loc[(slice(None), '23', slice(None)), ('channel 1', 'shift')])
print(s.loc[idx[:, '23', :], idx['channel 1', 'shift']])
print('-----------------------------------------')
print(s.loc[(slice(None)), ('channel 1', 'shift')])
print('-----------------------------------------')
print(s.loc[(slice(None)), ('channel 1', 'shift')])
print(s.loc[idx[:], idx['channel 1', 'shift']])
exit(-1)
# print(s)
# print(s.loc[('2'), ('20', 'std', 'shift2')])
# exit(-1)
print('-----------------------------------------')
print('-----------------------------------------')
print('-----------------------------------------')
print(s)
print('=====================================')
print(s.xs('111', level='s name')['channel 1'])
print('-----------------------------------------')
print(s.xs('111', level='s name'))
print('-----------------------------------------')
print(s.xs('23', level='temp')['channel 1'])
print('-----------------------------------------')
print(s.xs('23', level='temp'))
# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem
# import os

# class DirectoryViewer(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.tree = QTreeWidget()
#         self.tree.setColumnCount(1)
#         self.tree.setHeaderLabels(['Files and Directories'])
#         self.setCentralWidget(self.tree)
#         self.populate_tree()

#     def populate_tree(self):
#         # root_dir = 'D:/Work/Gyro2023_Git/res/' # Укажите путь к директории, которую хотите отобразить
#         root_dir = 'D:/Work/Gyro2023_Git/' # Укажите путь к директории, которую хотите отобразить
#         # t1 = perf_counter()
#         self.add_items(self.tree, root_dir)
#         # print('t1 = ', perf_counter() - t1)

#     def add_items(self, parent, path):
#         for item_name in os.scandir(path):
#             item = QTreeWidgetItem(parent, [item_name.name])
#             if item_name.is_dir():
#                 self.add_items(item, item_name.path)

#     def show(self):
#         super().show()

# if __name__ == '__main__':
#     t = perf_counter()
#     app = QApplication(sys.argv)
#     viewer = DirectoryViewer()
#     viewer.show()
#     print('t = ', perf_counter() - t)
#     sys.exit(app.exec_())

# import psutil


# print(psutil.cpu_percent(interval=0.5, percpu=True))
# path = 'D:/Work/Gyro2023_Git/33.xlsm'

# t = perf_counter()
# for proc in psutil.process_iter(['pid', 'name']):
# # for proc in psutil.process_iter(['pid', 'name']):
#     try:
#         # proc.open_files()
#         for item in proc.open_files():
#             # print(item.path)
#             if path in item.path:
#                 print(3213213)
#                 break
#         print('Ok')
#     except psutil.AccessDenied:
#         # print('AccessDenied')
#         pass
#     except PermissionError:
#         # print('PermissionError')
#         pass
#     except psutil.NoSuchProcess:
#         # print('NoSuchProcess')
#         pass
# print('t = ', perf_counter() - t)



import xlwings as xw


# print(xw.apps)
# print(xw.books)
# for a in xw.apps:
#     a: xw.App = a
#     print(a.engine)
#     print(a.status_bar)
#     print(a.startup_path)
#     for book in a.books:
#         print(book)
#         book: xw.Book = book
#         print(book.fullname)
#         print(book.sheet_names)

import win32com.client as win32
import pythoncom as pycom


# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from PyQt5.QtCore import pyqtSignal, QObject

# class FileChangeHandler(FileSystemEventHandler, QObject):
#     file_changed = pyqtSignal(str, bool)  # Сигнал для оповещения об изменении файла
#     def __init__(self):
#         super(FileChangeHandler, self).__init__()

#     def on_modified(self, event):
#         print(event)
#         if not event.is_directory:
#             self.file_changed.emit(event.src_path, True)

#     def on_deleted(self, event):
#         print(event)
#         if not event.is_directory:
#             self.file_changed.emit(event.src_path, False)

# class FileMonitor(QObject):
#     def __init__(self, file_path):
#         super(FileMonitor, self).__init__()
#         self.file_path = file_path
#         self.event_handler = FileChangeHandler()
#         self.observer = Observer()
#         self.observer.schedule(self.event_handler, path=file_path)
#         self.observer.start()

#         self.event_handler.file_changed.connect(self.handle_file_change)

#     def handle_file_change(self, file_path, is_modified):
#         if is_modified:
#             print(f'File {file_path} has been modified')
#         else:
#             print(f'File {file_path} has been deleted')

#     def stop(self):
#         self.observer.stop()
#         self.observer.join()

# if __name__ == "__main__":
#     file_monitor = FileMonitor(r'D:/Work/Gyro2023_Git/33.xlsm')
#     input("Press any key to stop file monitoring...")
#     file_monitor.stop()

# print('--------------------------------------------------------')

# val = [
#     [772013, 294, 96757, 1200, 56789, 24, 6757, 1200, 56789, 24, 6757, 1200, 56789],
#     [192313, 24, 6757, 1200, 56789, 24, 6757, 1200, 56789, 24, 6757, 1200, 9999],
#     [2313, 24, 6757, 1200, 56789, 24, 6757, 1200, 56789, 24, 6757, 1200, 9999],
#     [2313, 24, 6757, 1200, 56789, 24, 6757, 1200, 56789, 24, 6757, 1200, 7895],
#     [2313, 24, 6757, 1200, 56789, 24, 6757, 1200, 56789, 24, 6757, 1200, 9999],
#     [2313, 24, 6757, 1200, 56789, 24, 6757, 1200, 56789, 24, 6757, 1200, 9999],
#     [2313, 24, 6757, 1200, 56789, 24, 6757, 1200, 56789, 24, 6757, 1200, 9999]
# ]
# # ----------------------------------------------------------------
# print('--------------------------------------------------------')
# # ----------------------------------------------------------------
# name = 'D:/Work/Gyro2023_Git/33.xlsm'
# t = perf_counter()
# try:
#     aaa = True
#     os.rename(name, name)  # удобная проверка на открытие файла
#     app = xw.App(visible=False, add_book=False)
#     print(f' EnsureDispatch xlwings {(perf_counter() - t):.3f}')
#     # app.calculation = 'manual'
#     # app.enable_events = False
#     # app.display_alerts = False
#     # app.interactive = False
#     app.screen_updating = False
#     t1 = perf_counter() 
#     wb = app.books.open(name)  # , update_links=True , local=True  , add_to_mru=True
# except OSError as e:
#     aaa = False
#     print(e.strerror) ; print(e.errno)
#     print(e.args) ; print(e.filename)
#     print(e.winerror) ; print(e.filename2)
#     t1 = perf_counter()
#     wb = xw.Book(name)  #, add_to_mru=True) !!! engine="remote": "xlwings Server",
#                     # "calamine": "xlwings Reader"
# # with xw.App(visible=False) as app:
# print(f'Open xlwings {(perf_counter() - t1):.3f}')
# t2 = perf_counter()
# ws: xw.Sheet = wb.sheets['Настройка КП']
# ws.range('A1').value = val  # нужен обработчик ошибок
# ws.range('B2').value = val  # нужен обработчик ошибок
# print(f'write xlwings {(perf_counter() - t2):.3f}')
# t3 = perf_counter()
# wb.save()
# if aaa: wb.close()
# # print(f'\tTOTAL {name} xlsm_write time:  {(perf_counter() - t3):.3f}')
# res = perf_counter() - t1
# print(f' Save Close xlwings {(perf_counter() - t3):.3f}')
# t4 = perf_counter()
# app.quit()
# print(f'Quit xlwings {(perf_counter() - t4):.3f}')
# print(f'\tTOTAL xlwings {(perf_counter() - t):.3f}')
# print(f'\tRES xlwings {res:.3f}')
# # ----------------------------------------------------------------
# print('--------------------------------------------------------')
# # ----------------------------------------------------------------
# name = 'D:/Work/Gyro2023_Git/22.xlsm'
# t = perf_counter()
# # excel_com_object: win32.CDispatch = win32.gencache.EnsureDispatch('Excel.Application')
# excel_com_object = win32.Dispatch('Excel.Application')
# # sleep(0.5)
# # print(type(excel_com_object))
# # excel_com_object = win32.DispatchEx('Excel.Application')
# # excel_com_object = win32.dynamic.Dispatch('Excel.Application')
# print(f' EnsureDispatch win32 {(perf_counter() - t):.3f}')
# t1 = perf_counter()
# wb = excel_com_object.Workbooks.Open(name)
# print(f'Open win32 {(perf_counter() - t1):.3f}')
# t2 = perf_counter()
# wb.Worksheets('Настройка КП').Cells(1, 1).Value = val
# print(f'write win32 {(perf_counter() - t2):.3f}')

# t3 = perf_counter()
# wb.Save()
# wb.Close()
# res = perf_counter() - t1
# print(f' Save Close win32 {(perf_counter() - t3):.3f}')
# t4 = perf_counter()
# excel_com_object.Quit()
# print(f'Quit win32 {(perf_counter() - t4):.3f}')
# print(f'\tTOTAL win32 {(perf_counter() - t):.3f}')
# print(f'\tRES win32 {res:.3f}')
# # ----------------------------------------------------------------
# print('--------------------------------------------------------')
# # ----------------------------------------------------------------

def to_image(to_save, name='temp_image.jpg', ext='jpg', **opts):
    """Save image. to_save plotItem or QWidget"""
    if hasattr(to_save, 'winId'): # opts.get('QImage') and 
        print(f'PyQt5 export')
        from PyQt5 import QtWidgets, QtGui
        to_save: QtWidgets.QWidget = to_save
        image: QtGui.QPixmap = to_save.grab(to_save.rect())
        # image = QtGui.QImage(to_save.size(), QtGui.QImage.Format.Format_Alpha8)
        # to_save.render(image)
        image.save(name, ext) #, 'jpg', 100)

def xlsm_write(name, sheet, cells, value_to_write, app=None):
    """xlsm write with xlwings"""
    # добавить работу с несколькими таблицами внутри одной книги
    # добавить замену ошибок
    import pywintypes
    import xlwings as xw
    print(f'xlsm_write')
    t = perf_counter()
    if app is None:
        app_creation_flag = True
        app = xw.App(visible=False)
    else:
        app_creation_flag = False
    # with xw.App(visible=False) as app:
    open = False
    try:
        os.rename(name, name)  # удобная проверка на открытие файла
    except FileNotFoundError:  # так быстрее и лучше, чем через if not os.path.isfile(current_xlsm_path)
        if app_creation_flag: app.quit()
        print(f'\nFileNotFoundError {name}\n')
        return False
    except OSError:
        print(f'\nWrite to OPEN xlsm\n')
        # тут надо подключаться к тому объекту, в котором открыт файл
        # если 'app' был получен извне, то нужно новый создать!
        open = True
    # wb: xw.Book = app.books.open(name)
    wb = app.books.open(name)
    print(f'only loading:  {(perf_counter() - t3):.3f}')
    if type(sheet) != list and type(sheet) != tuple:
        sheet = [sheet]
        value_to_write = [value_to_write]
        cells = [cells]
    for (value, sheet_cell, one_sheet) in zip(value_to_write, cells, sheet):
        img_flag = False
        ws: xw.Sheet = wb.sheets[one_sheet]
        print(f'\twrite to cell: {sheet_cell}, sheet {one_sheet}') #, value {value}')
        # ---
        if not value is None: 
            if type(value) == str:
                print(f'write to cell: {sheet_cell}')
                img_name, extension = os.path.splitext(value)
                img_name = os.path.basename(img_name)
                if extension in ['.jpg', '.png'] and os.path.isfile(value):
                    print(f' ws.pictures.add')
                    for _, pic in enumerate(ws.pictures):
                        try:
                            if pic.name == img_name:
                                print(f'update image {img_name}')
                                pic.update(val)
                                break
                        except pywintypes.com_error:
                            pass
                    else:
                        ws.pictures.add(value, 
                                        left=ws.range(sheet_cell).left, top=ws.range(sheet_cell).top,
                                        name=img_name
                                        # anchor=ws.range(cells)
                                        )  # нужен обработчик ошибок
                        print(f'add image {img_name}')
                        # можно искать картинки с теми же left и top
                        # и использовать метод update, чтобы их заменить
                else:
                    ws.range(sheet_cell).value = value  # нужен обработчик ошибок
            else:
                print(f'\nwrite to cells: {sheet_cell}')#,\nvalue: {value}')
                if type(sheet_cell) == list:
                    for (cell, val) in zip(sheet_cell, value):
                        # print(f'\twrite to cells: {cell}, value: {val}')
                        if not value is None:
                            if type(val) == str:
                                img_name, extension = os.path.splitext(val)
                                img_name = os.path.basename(img_name)
                                if extension in ['.jpg', '.png'] and os.path.isfile(val):
                                    # sheet.pictures старые на новые, так правильнее
                                    if not img_flag:
                                        pics = [pic for pic in ws.pictures]
                                        img_flag = True
                                    for _, pic in enumerate(pics):
                                        try:
                                            if pic.name == img_name:
                                                print(f'update image {img_name}')
                                                pic.update(val)
                                                break
                                        except pywintypes.com_error:
                                            pass
                                    else:
                                    # print(f' ws.pictures.add')
                                        ws.pictures.add(
                                            val, left=ws.range(cell).left, top=ws.range(cell).top,
                                            name=img_name
                                            )  # нужен обработчик ошибок
                                        print(f'add image {img_name}')
                                    continue
                            ws.range(cell).value = val  # нужен обработчик ошибок
                        else:
                            print(f'None!')
                        # wb.save()
                else:
                    ws.range(sheet_cell).value = value   # нужен обработчик ошибок
        else:
            print(f'None!')
                # ---
    print(f'without save and close:  {(perf_counter() - t3):.3f}')
    wb.save()
    if open: wb.close()
    print(f'\tTOTAL {name} xlsm_write time:  {(perf_counter() - t3):.3f}')
    if app_creation_flag: app.quit()