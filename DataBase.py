# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

from time import perf_counter
import logging
# import sys
import os
import re
import numpy as np

__logger = None


__prj_unapplied_changes = None
__prj: dict = {} 

__active_cycle_flag = False

# def warning(info):
#     if __logger: __logger.warning(info)

# def debug(info):
#     if __logger: __logger.debug(info)

def setlogger(logger: logging.Logger):
    __logger = logging
    print('setlogger!')
    if __logger: __logger.info('setlogger!')

def setCycle():
    # global __active_cycle_flag
    __active_cycle_flag = True
    print('setCycle!')
    if __logger: __logger.info('setCycle!')

def resetCycle():
    global __active_cycle_flag
    __active_cycle_flag = False
    global __prj_unapplied_changes
    if not __prj_unapplied_changes:
        return
    for key in __prj_unapplied_changes.keys():
        __prj[key] = __prj_unapplied_changes[key]
    print(f'resetCycle, copy values:\t {__prj_unapplied_changes.keys()}')
    if __logger: __logger.info(f'resetCycle, copy values:\t {__prj_unapplied_changes.keys()}')
    __prj_unapplied_changes = {} 

def get(*args, **kwargs):
    """Main params:
        sensors - actual sensor list;
        __path_to_save_app_settings;
        __dict_with_app_settings;
        Logger - logger;
        __path_to_projects - path to projects folder;
        project - current project with following settings
            "visible in app": 1,
            params to show in context menu - ;
            "h-files template": "D:/GyroResultsProcessing/h-files templates23/DeviceXXXX.h",
            "h-files folders": ["D:/GyroResultsProcessing/h-files"],
            "excel lists folders": "D:/GyroResultsProcessing",
            "settings results folder": "D:/GyroResultsProcessing/настройки",
            "check results folder": "D:/GyroResultsProcessing/проверки",
            "base number": 1100000,
            "settings temperatures": [-50, 23, 60],
            "check temperatures": [-50, 23, 50]
            n_peaks - число пиков на настройке для обсчета масштабников
            check results table cell - ;
            check results image cells - ;
        /
    """
    if __logger: __logger.info(f'Get param:\t {args}{kwargs}')
    print(f'Get param:\t {args}{kwargs}')
    return __prj.get(*args, **kwargs)

def getParams(params):
    """Main params:
        sensors - actual sensor list;
        __path_to_save_app_settings;
        __dict_with_app_settings;
        Logger - logger;
        __path_to_projects - path to projects folder;
        project - current project with following settings
            "visible in app": 1,
            params to show in context menu - ;
            "h-files template": "D:/GyroResultsProcessing/h-files templates23/DeviceXXXX.h",
            "h-files folders": ["D:/GyroResultsProcessing/h-files"],
            "excel lists folders": "D:/GyroResultsProcessing",
            "settings results folder": "D:/GyroResultsProcessing/настройки",
            "check results folder": "D:/GyroResultsProcessing/проверки",
            "base number": 1100000,
            "settings temperatures": [-50, 23, 60],
            "check temperatures": [-50, 23, 50]
            n_peaks - число пиков на настройке для обсчета масштабников
            check results table cell - ;
            check results image cells - ;
        /
    """
    output = []
    for key in params:
        res = __prj.get(key, None)
        if res:
            output.append(res)
    if __logger: __logger.info(f'Get params:\t {params}')
    print(f'Get params:\t {params}')
    return output

def setParams(**params):
    """Main params:
        sensors - actual sensor list;
        __path_to_save_app_settings;
        __dict_with_app_settings;
        Logger - logger;
        __path_to_projects - path to projects folder;
        project - current project with following settings
            "visible in app": 1,
            params to show in context menu - ;
            "h-files template": "D:/GyroResultsProcessing/h-files templates23/DeviceXXXX.h",
            "h-files folders": ["D:/GyroResultsProcessing/h-files"],
            "excel lists folders": "D:/GyroResultsProcessing",
            "settings results folder": "D:/GyroResultsProcessing/настройки",
            "check results folder": "D:/GyroResultsProcessing/проверки",
            "base number": 1100000,
            "settings temperatures": [-50, 23, 60],
            "check temperatures": [-50, 23, 50]
            n_peaks - число пиков на настройке для обсчета масштабников
            check results table cell - ;
            check results image cells - ;
        /
    """
    if __active_cycle_flag:
        for key in params.keys():
            __prj_unapplied_changes[key] = params[key]
        if __logger: __logger.info(f'Cycle active, copy values:\t {params.keys()}')
        print(f'Cycle active, copy values:\t {params.keys()}')
        return False
    else:
        for key in params.keys():
            __prj[key] = params[key]
        if __logger: __logger.info(f'Push values:\t {params.keys()}')
        print(f'Push values:\t {params.keys()}')
        return True

def xlsm_reader(path_to_list, *cells, **other):
    """sheet_name='Настройка КП', engine="calamine, header=None, index_col=None"""
    import pandas as pd
    res: pd.DataFrame = pd.read_excel(
            path_to_list,
            sheet_name='Настройка КП',
            header=None, index_col=None,
            # usecols='A:P', nrows=160,  # make faster a bit (max: 10-20% speed up)
            # dtype=np.float32,  # not working
            engine="calamine"  # calamine the fastest
    )
    print(cells, type(cells))
    if not cells is None and len(cells) > 0:
        result = []
        if (type(cells) == list or type(cells) == tuple) and type(cells[0]) == list:
            cells = cells[0]
        for cell in cells:
            i = get_coords(cell)
            result.append(res.iloc[i[0], i[1]])
        res = result
    return res

def number_to_column(n):
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

def shift_coords(string: str, value): 
    """res = cell + value: (row, col)"""
    column = re.findall('[A-Z]{1,3}', string)
    column_i = 0
    for letter in list(column[0]):
        column_i *= 26  # не 25 ????
        column_i += ord(letter) - 64
    column_i += value[0]
    # print(list(column[0]), column_i, number_to_column(column_i))
    row_i = int(*re.findall('[0-9]{1,4}', string)) + value[1] # -1 because in pd index starts from 0...
    res = number_to_column(column_i) + str(row_i)
    return res

def get_coords(string: str): 
    column = re.findall('[A-Z]{1,3}', string)
    column_i = 0
    for letter in list(column[0]):
    # for letter in column:
        column_i *= 26  # не 25 ????
        column_i += ord(letter) - 64
        # column_i += ord(letter) - 65
    column_i -= 1
    row_i = int(*re.findall('[0-9]{1,4}', string)) - 1 # -1 because in pd index starts from 0...
    return (row_i, column_i)

# print(ord('A') - 65)
# print(shift_coords('AAB23', (31, 213)))

# frame = xlsm_reader(
#     'D:/GyroResultsProcessing/1101509.xlsm',
#     ['F32', 'F33']
#     # DataBase.get('Scale factors cells'),
#     )
# print(frame)

def save_txt(data, **other):
    """."""
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_csv(other.get('filename', 'temp.txt'), header=None,
              index=None, sep=' ', mode='w', date_format='%d')

def txt_reader(path_to_list, **other):
    """delimiter=' ', dtype=np.int32, header=None, index_col=None, engine='pyarrow'"""
    import pandas as pd
    res: pd.DataFrame = pd.read_csv(
                filepath_or_buffer=path_to_list,
                delimiter=' ',
                dtype=np.int32,  # speed up a bit
                header=None, index_col=None,
                engine='pyarrow',  # engine = {'c', 'python', 'pyarrow'}
                **other)
    # 'pyarrow' provides x2 speed if you compare it with 'c'!
    return res

def xlsm_write(name, sheet, cells, value_to_write, app=None):
    """xlsm write with xlwings"""
    # добавить работу с несколькими таблицами внутри одной книги
    # добавить замену ошибок
    import pywintypes
    import xlwings as xw
    print('xlsm_write')
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
        print('\nWrite to OPEN xlsm\n')
        open = True
    # wb: xw.Book = app.books.open(name)
    wb = app.books.open(name)
    print('only loading: ', perf_counter() - t)
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
    print('without save and close: ', perf_counter() - t)
    wb.save()
    if open: wb.close()
    print(f'\tTOTAL {name} xlsm_write time: ', perf_counter() - t)
    if app_creation_flag: app.quit()

def to_image(to_save, name='temp_image.jpg', ext='jpg', **opts):
    """Save image. to_save plotItem or QWidget"""
    if hasattr(to_save, 'winId'): # opts.get('QImage') and 
        print('PyQt5 export')
        from PyQt5 import QtWidgets, QtGui
        to_save: QtWidgets.QWidget = to_save
        image: QtGui.QPixmap = to_save.grab(to_save.rect())
        # image = QtGui.QImage(to_save.size(), QtGui.QImage.Format.Format_Alpha8)
        # to_save.render(image)
        image.save(name, ext) #, 'jpg', 100)
    # elif hasattr(to_save, 'winId'): # проверка на виджет Qt
    #     from PyQt5 import QtWidgets
    #     to_save: QtWidgets.QWidget = to_save
    #     app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
    #     screen = app.primaryScreen()
    #     screenshot = screen.grabWindow(to_save.winId())  # QtWidgets.QWidget.winId()
    #     screenshot.save(name, 'jpg') #, 100)
    else:
        print('pyqtgraph export')
        import pyqtgraph.exporters as exporters
        # import pyqtgraph as pg  # pg.PlotWidget.plotItem
        exporter = exporters.ImageExporter  # exporter = exporters.SVGExporter\
        img_exporter = exporter(to_save) # может, я зря каждый раз это вызываю?
        # if opts.get('height'):
        #     exporter.params.param('height').setValue(100, blockSignal=exporter.heightChanged)
        # if opts.get('width'):
        #     exporter.params.param('width').setValue(100, blockSignal=exporter.widthChanged)
        img_exporter.export(name)
    return os.getcwd() + name


# xData222 = np.array([-5,-2,-1,2,3,4,6,4,5,7,9, 4])
# xData = np.array([-5,-1,-1,2,3,4,4,4,5,6, 6])
# ununique = np.where(np.diff(xData) != 0)[0] + 1
# print('ununique', ununique, np.diff(xData))
# # ununique = np.insert(ununique, ununique.size, xData.size)
# # __ununique = np.array([0, *ununique, xData.size])
# # print(__ununique)
# ununique = np.insert(ununique, [0, ununique.size], [0, xData.size])
# print(ununique)
# d_unique = np.diff(ununique)
# # print(np.where(d_unique == 1)[0])
# # print(np.where(d_unique != 1)[0])
# # print(np.diff(d_unique) == 1)
# print(d_unique, '\n')
# xData2 = np.ndarray(shape=(len(ununique) - 1))
# for i in range(ununique.size - 1):
#     print(ununique[i],ununique[i+1],d_unique[i])
#     xData2[i] = np.sum(xData[ununique[i]:ununique[i+1]]) / d_unique[i]
# print(xData2)
# print(xData222[ununique])
# print(np.array([[1,2], [3,4], [2, 5]]))
# print(np.divide(np.array([[1,2], [3,4], [2, 5]]), np.array([2, 4])))

# xlsm_write('D:/GyroResultsProcessing/1101383.xlsm', 'Настройка КП', 'A120', 1132434, app=None)
# import xlwings as xw
# with xw.App(visible=False) as app:
#     wb: xw.Book = app.books.open('D:/GyroResultsProcessing/1101383.xlsm')
#     ws: xw.Sheet = wb.sheets['Настройка КП']
#     # ws.range('A140').value = 32434
#     xw.Picture
#     ws.pictures
#     t = perf_counter()
#     for i, pic in enumerate(ws.pictures):
#         # pic: xw.Picture = pic
#         print(pic)
#         print(pic.left)
#         print(pic.top)
#         print(pic.name)
#         # pic.name = f'img_10649_acc.{i}'
#         # print(pic.update(os.path.realpath('D:/GyroResultsProcessing/temporary/img_10649_acc.jpg')))
#     print(perf_counter() - t)
#     wb.save()
#     wb.close()
# temp = '+23'
# # pattern = f'_\{temp}_[K-M]_' # (.*?){1,30} 
# # pattern = r'\+23_MK_' # (.*?){1,30} 
# pattern = f'_\{temp}' + r'_MK_' # (.*?){1,30} 
# res = re.findall(pattern, '02_+23_MK_13.5.txt') 
# print(res)

def sensors_from_str(text: str) -> list[str]:
    # def check(name):
        # return 3 < len(name) < 20 # and name.isdigit()  # use isdigit() or not???
    pattern = r'\d{1,4}\-\d{1,2}\-\d{1,4}\_'
    dates = re.findall(pattern, text) #; print('dates ', dates)
    if len(dates) == 1:
        text = text.removeprefix(dates[0])
    # print('text ', text)
    text = re.split("_", text); print('text ', text)
    # text = list(filter(check, text)); print('text ', text)
    return text

def validate_sensors(sensors: list[str]) -> list[str]:
    path = get('excel lists folders')
    if not path:
        return False
    validate = []
    for sensor in sensors:
        full_path = path + '/' + sensor + '.xlsm'
        if os.path.isfile(full_path):
            validate.append(sensor)
    return validate

# from numba import njit
# @njit()
def clear_repeats(xData: np.ndarray, yData: np.ndarray):
    t = perf_counter()
    args = xData.argsort(kind='quicksort')
    xData = xData[args]
    if len(yData.shape) == 1: yData = yData[args]
    else: yData = yData[args, :]
    ununique = np.where(np.diff(xData) != 0)[0] + 1
    ununique = np.insert(ununique, [0, ununique.size], [0, xData.size])
    d_unique = np.diff(ununique)
    sort_yData = np.add.reduceat(yData, ununique[:-1])  # works fast
    # sort_yData = np.ndarray(shape=(len(ununique) - 1, yData.shape[1]))
    # for i in range(ununique.size - 1):  # works slow
    #     sort_yData[i] = np.sum(yData[ununique[i]:ununique[i+1], :])
    # sort_yData = (sort_yData.transpose() / d_unique).transpose()
    if len(yData.shape) == 1: sort_yData = sort_yData / d_unique
    else: sort_yData = (sort_yData.transpose() / d_unique).transpose()
    sort_xData = xData[ununique[:-1]]
    # print(len(xData)); print(len(sort_xData))
    # print(len(xData[ununique])); print(len(sort_yData)); print(len(ununique))
    print('__t clear = ', perf_counter() - t)
    # print(sort_yData)
    return sort_xData, sort_yData

# frame = txt_reader(
#     'D:/GyroResultsProcessing/настройки/2024-06-20_1101353_1101141_1101755_x_x_1101630_1101597.2_x_1101109_x_x_x/000. Одно измерение.txt')
# frame = frame.to_numpy()
# res1, res2 = clear_repeats(frame[:, 3], frame[:, 2])

def get_date(type=1) -> str:
    """day.month.year"""
    from time import gmtime, time
    gmt_time = gmtime(time()) # current GMT Time
    date = f'{gmt_time.tm_mday}.{gmt_time.tm_mon}.{gmt_time.tm_year}'
    return date 

def smooth_data(array_to_smooth, n: int, type='mean', **opts):
    """type: mean or savgol"""
    n = int(n)
    if type == 'mean':
        filter = np.ones(n, dtype=np.float64) / n
        smoothed_array = np.apply_along_axis(
            lambda data: np.convolve(data, filter, mode='same'), axis=0, arr=array_to_smooth) # select only two channels!!!!
        n = int(n/2) + 1
        smoothed_array[:n, :] = smoothed_array[n, :] ########################
        smoothed_array[-n:, :] = smoothed_array[-n, :] ########################
    elif type == 'savgol':
        t = perf_counter()
        from scipy.signal import savgol_filter
        smoothed_array = savgol_filter(
            array_to_smooth, window_length=n, polyorder=opts.get('polyorder', 3))
        print('t savgol:', perf_counter() - t)
    else:
        raise(KeyError)
    return smoothed_array

# import xlwings as xw
# t = perf_counter()
# with xw.App(visible=False) as app:
#     # for i in range(3):
#     print(perf_counter() - t)
#     t = perf_counter()
#     wb = xw.Book('444.xlsm')
#     print(perf_counter() - t)
#     ws = wb.sheets(sh_nm)                                   
#     ws.range('I12').value = float(19832)
#     # # -----
#     # # 1 ---
#     # app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
#     # screen = app.primaryScreen()
#     # screenshot = screen.grabWindow(QtWidgets.QWidget.winId())
#     # screenshot.save('...\shot.jpg', 'jpg', 100)
#     # # 2 ---
#     # import pyqtgraph.exporters as exporters
#     # exporter = exporters.ImageExporter  # exporter = exporters.SVGExporter
#     # exporter(pg.PlotWidget.plotItem).export('...\shot.jpg')
#     # # -----
#     ws.pictures.add('D:\Work\Gyro2023_Git\shot22.jpg', anchor=ws.range('N51'))
#     wb.save()
#     # # wb.close()
#     print(perf_counter() - t)
#     # xw.App.quit()

# class DataBase(): # plots
#     progress_signal = QtCore.pyqtSignal(int)
#     # можно сделать так, чтобы графики автомати
#     def __init__(self, **params):
#         self.params


