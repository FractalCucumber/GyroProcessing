# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

from time import time, sleep, perf_counter
import sys
import os
import re
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from widgets.PyQt_CustomPushButton import CustomButton
from CustomQTextEdit import CustomQTextEdit
from widgets.PyQt_ProjectsComboBox import ProjectsComboBox

from widgets.tab_widget.PyQt_CustomViewBox import CustomViewBox

from QtCustomPlot import CustomPlot

from multiprocessing import Pool, Process


import DataBase


class ScaleFactorsCalculatorGroupbox(QtWidgets.QGroupBox): # scale factors
    progress_signal = QtCore.pyqtSignal(int)
    def __init__(self, settings=None, *args, **kwds):
        QtWidgets.QGroupBox.__init__(self, *args, **kwds)
        self.__logger = DataBase.get('Logger', None)  # !!!
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(3, 5, 3, 3)
        # ---
        self.lbl_table = QtWidgets.QTableWidget()
        # горизонтальный скролбар не появится, т.к. всего один столбец в таблице
        self.lbl_table.setMinimumHeight(260) 
        self.lbl_table.setColumnCount(1)
        self.lbl_table.setRowCount(6)
        self.lbl_table.horizontalHeader().hide()
        self.lbl_table.setVerticalHeaderLabels(
            ['Тип',
             'Определение\nинтервалов по КП', # убрать потом?
             'Коэффициент\nдля определения пиков',
             'Отступ справа\nот переходного процесса',
             'Отступ слева\nот переходного процесса',
             'Выполнил'
             ])
        self.type_cb = QtWidgets.QComboBox()
        self.type_cb.addItems(['Аксель', 'Гирик', 'А+Г'])
        self.lbl_table.setCellWidget(0, 0, self.type_cb)
        self.person_cb = ProjectsComboBox(self)
        # self.person_cb.addItems(['Human1', 'Human2', 'Human3'])
        self.lbl_table.setCellWidget(
            self.lbl_table.rowCount() - 1, 0, self.person_cb)

        items_text = ['all', '1.5', '200', '300']
        for i, text in enumerate(items_text):
            item = QtWidgets.QTableWidgetItem(text)
            item.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignCenter)
            self.lbl_table.setItem(i + 1, 0, item)
        self.lbl_table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.lbl_table.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.lbl_table)
        # ---
        self.calc_scale_factors_button = CustomButton('Считать')
        layout.addWidget(self.calc_scale_factors_button)
        self.calc_scale_factors_button.clicked.connect(
            self.process
        )
        # ---
        self.path_te = CustomQTextEdit(
            objectName="with_border", maximumHeight=80)
        layout.addWidget(self.path_te)
        # ---
        self.on_fly_checkbox = QtWidgets.QCheckBox("Get path on fly")
        layout.addWidget(self.on_fly_checkbox)
        # ---
        self.write_status_checkbox = QtWidgets.QCheckBox("Ставить статус 'На проверку'")
        layout.addWidget(self.write_status_checkbox)
        # ---
        import pyqtgraph as pg
        self.graphWidget = CustomPlot(viewBox=CustomViewBox(), visible=False)  # !!!
        # self.graphWidget = pg.PlotWidget()
        self.graphWidget.plotItem.clear()
        self.graphWidget.plotItem.addLegend(offset=(-1, 1), labelTextSize=f'{12}pt',
                                            labelTextColor=pg.mkColor('w'))
        self.graphWidget.plotItem.plot(pen=pg.mkPen('#0055FF'), name='-2')
        self.graphWidget.plotItem.plot(pen=pg.mkPen('#FF5500'), name='1')
        self.graphWidget.plotItem.plot(pen=pg.mkPen('#00AA55'), name='2', width=1.5)
        self.graphWidget.plotItem.plot(pen=pg.mkPen('#AAAA55'), name='3')
        self.graphWidget.plotItem.plot(pen=pg.mkPen('#000000'), name='4')

        if settings: self.restore_settings(settings)

    def process_single_temp(
            self, files: list[str], ind, dist_between,
            n_smooth, required_len, shift, channel, # 0 - acc, 1 - gyro
            n=1, k_peaks=0.1 # 1 sec
            ):
        # учесть fs при построении фильтра
        if type(ind) == int:
            range_to_read = [ind + 1, ind + 2, ind + 3]
            gyro_range = [ind + 2]
        else:
            range_to_read = []  # [0]
            gyro_range = []
            for i in ind:
                __i = 1 + i * 3
                [range_to_read.append(__i + n) for n in range(3)]
                gyro_range.append(__i + channel)
        # print('range_to_read', range_to_read); print('gyro_range', gyro_range)
        # --- read files ---
        for _, file in enumerate(files): # цикл чтения файлов (пока что читаю только последний из списка)
            file = files[-1]
            frame = DataBase.txt_reader(file, usecols=[0, *range_to_read])
            self.__logger.warning('пока что читаю последний файл только')
            break # пока что только последний файл беру
        # --- end read ---
        t = perf_counter()
        # pd.Series(array).rolling(window=window_size, center=True).mean()
        array = frame.to_numpy()
        # print('\n\narray', array.shape)
        array_to_smooth = array[::n, gyro_range].astype(np.float64)
        smoothed_array = DataBase.smooth_data(array_to_smooth, int(n_smooth / n))
        smoothed_array = DataBase.smooth_data(smoothed_array, int(n_smooth / n / 8))
        # DataBase.save_txt(res)
        diff = np.diff(smoothed_array, axis=0)
        diff2_extrs = np.full(shape=(required_len, diff.shape[1]), fill_value=np.nan)
        for i in range(diff.shape[1]):
            diff2 = np.abs(diff[:, i])
            diff2_extr_all = np.where(
                (diff2[1:-2] > diff2[0:-3]) & (diff2[1:-2] > diff2[2:-1])
                )[0] + 1
            diff2_max = np.max(diff2)
            diff2_extr_all = diff2_extr_all[diff2[diff2_extr_all - 1] > k_peaks * diff2_max] # 
            print(f'\ndiff2_extr[{i}] before: ', diff2_extr_all, '\n')
            diff2_extr_all = np.insert(diff2_extr_all, [0, diff2_extr_all.size], [0, diff2.size - 1]) # diff2_extr[-1] + shift + 1)
            # diff2_extr_all = np.insert(diff2_extr_all, diff2_extr_all.size, diff2.size - 1) # diff2_extr[-1] + shift + 1)
            where = np.where(np.diff(diff2_extr_all) > dist_between / n)[0]
            # diff2_extr = diff2_extr_all[where] * n  # n - учет прореживания!!!!
            diff2_extr = np.array([*diff2_extr_all[where] * n, *diff2_extr_all[where + 1] * n])
            diff2_extr_all = np.insert(diff2_extr_all, [0, diff2_extr_all.size], [0, diff2.size - 1]) # diff2_extr[-1] + shift + 1)
            print(f'\ndiff2_extr[{i}] afterwww: ', diff2_extr, '\n')
            diff2_extr = np.sort(diff2_extr)[:-1]
            diff2_extr = diff2_extr[np.where(np.diff(diff2_extr) > dist_between / n)[0] + 1]
            res = diff[diff2_extr, i]
            prod = np.prod(res / np.sum(np.abs(res)))
            print(f'\ndiff2_extr[{i}] afterwww2: ', diff2_extr, '\n')
            print(diff[diff2_extr, i], prod, prod / np.abs(prod))
            print(f'\ndiff2_extr[{i}] after: ', diff2_extr, '\n')
            if prod / np.abs(prod) != 1:
                text = f'Не сходятся знаки ({prod})'
                self.__logger.error(text); print(text)
                continue
            if e_n := len(diff2_extr) != required_len:
                text = f'Нашел {e_n} экстремумов, а нужно было {required_len}'
                self.__logger.error(text); print(text)
                continue
            diff2_extrs[:, i] = diff2_extr
        diff2_extr = np.nanmedian(diff2_extrs, axis=1)
        print(f'\diff2_extrs !!! : ', diff2_extr, '\n\n')
        diff2_extr = (diff2_extr.astype(np.int64)).tolist()
        diff2_extr = [0, *diff2_extr, array.shape[0] - 1]
        if any(np.isnan(diff2_extr)):
            self.__logger.error('isnan error'); print('\nisnan error\n')
            self.graphWidget.show()
            self.graphWidget.plotItem.curves[0].setData(x=array[:, 0], y=array_to_smooth[:, 0])
            self.graphWidget.plotItem.curves[1].setData(x=array[:, 0], y=smoothed_array[:, 0])
            self.graphWidget.plotItem.curves[2].setData(x=array[:-1, 0], y=diff[:, 0])
            self.graphWidget.plotItem.curves[3].setData(x=np.array(diff2_extr), y=array[diff2_extr, 1])
            return False
        res_table = np.ndarray(
            shape=(len(diff2_extr) - 1, len(range_to_read)), dtype=np.float64)
        std_res_table = np.ndarray(
            shape=(len(diff2_extr) - 1, len(range_to_read)))

        for k in range(len(diff2_extr) - 1):
            fragment = array[diff2_extr[k] + shift:diff2_extr[k + 1] - shift, range_to_read]
            res_table[k, :] = np.mean(fragment, axis=0)
            zero_shift = fragment - res_table[k, :]
            std_res_table[k, :] = np.std(zero_shift, axis=0)
        # mean = np.mean(std_res_table, axis=0)  # среднее по СКО
        mean = np.median(std_res_table, axis=0)  # !!! median среднее по СКО !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # --- print --- 
        # print('\nres_table\n', res_table.round(2))
        print('\nzero_shift\n', zero_shift.round(2))
        print('\nstd_res_table\n', std_res_table.round(2), '\n')
        # --- plots ---
        self.graphWidget.show()
        self.graphWidget.plotItem.curves[0].setData(x=array[:, 0], y=array_to_smooth[:, 0])
        self.graphWidget.plotItem.curves[1].setData(x=array[:, 0], y=smoothed_array[:, 0])
        self.graphWidget.plotItem.curves[2].setData(x=array[:-1, 0], y=diff[:, 0])
        self.graphWidget.plotItem.curves[3].setData(x=np.array(diff2_extr), y=array[diff2_extr, 1])

        res_table.resize(res_table.shape[0] + 1, res_table.shape[1], refcheck=False)
        res_table[-1, :] = mean
        print('\n math time: ', perf_counter() - t)
        print('\n res_table final\n', res_table.round(1), '\n')
        return res_table
# -------------------------------------------------------------------------------
    def process(self, path_to_xlsm: str = None, 
                n_peaks: int = None, real_sensors = None,
                fs=200,
                temps=None,
                mp_flag=True
                ): # добавить moveToThread
        t__0 = perf_counter()

        if not real_sensors:
            real_sensors = DataBase.get('sensors')  # !!!
            if not real_sensors:
                self.__logger.warning(
                    'Сожалею, но для вызова функции не хватает параметров (sensors)')  # !!!
                return False
        if not path_to_xlsm: # учесть опцию get on fly в противном случае вызвать диалоговое окно
            path_to_xlsm = DataBase.get('excel lists folders')  # !!!
            if not path_to_xlsm:
                self.__logger.warning(
                    'Сожалею, но для вызова функции не хватает параметров (excel lists folders)')  # !!!
                return False
        if not n_peaks: # учесть опцию get on fly в противном случае вызвать диалоговое окно
            n_peaks = DataBase.get('number of peaks', None)  # !!!
            if not n_peaks:
                self.__logger.warning(
                    'Сожалею, но для вызова функции не хватает параметров (n_peaks)')  # !!!
                return False
        if not temps:
            temps = DataBase.get('settings temperatures', None)  # !!!
            if not temps:
                self.__logger.warning(
                    'Сожалею, но для вызова функции не хватает параметров (settings temperatures)')  # !!!
                return False

        # --- find folder with settings results ---
        directory, files = self.get_filenames(temps)
        if not directory: return False
        # --- ---
        # --- get real sensors indexes ---
        ind = self.get_validate_sensors(os.path.basename(directory))
        if not ind: return False
        # --- end check ---
        # --- start file loading ---
        DataBase.setCycle()
        self.progress_signal.emit({'visible': True})
        QtWidgets.QApplication.setOverrideCursor(
            QtCore.Qt.CursorShape.BusyCursor)
        res_tables_list = []
        for i in ind:
            res_tables = np.full(
                shape=(13 + 1, len(temps) * 3 + 3), #len(real_sensors)),
                dtype=np.float64, fill_value=np.nan) #  * 3 because A, G, T
            res_tables_list.append(res_tables)
        for i, files_for_certain_temp in enumerate(files): # цикл обработки разных температур
            res_table = self.process_single_temp(shift=200,
                files=files_for_certain_temp, ind=ind,
                required_len=n_peaks, n_smooth=int(fs * 0.4) + 1, # n_smooth = 80
                dist_between=fs, # 1 sec
                channel=0 # 0 - acc, 1 - gyro
                )
            if res_table is False: return False
            for j, res_tables in zip(ind, res_tables_list):
                res_tables[:, i * 4:i * 4 + 3] = res_table[:, j * 3:j * 3 + 3]
                # print(res_tables)
        self.__logger.error(
            f'Шум у гирика неверно считается (потому что он зависит от наличия воздействия)')
        # -----------------------------------------------------------------------------------
        t__1 = perf_counter()
        # save table in xlsm
        person = self.person_cb.currentText()
        date = DataBase.get_date()
        scale_cell = DataBase.get('scale factors table cell')
        print('scale_cell', scale_cell)
        len1 = int(len(real_sensors) / 2)
        len2 = len(real_sensors) - len1
        print('\n\n\n lengths:', len1, len2, '\n\n')
        # status_flag

        # return False #####################################################################

        if self.write_status_checkbox.isChecked():
            status = 'На проверку'
        else:
            status = None
        if mp_flag:
            args = zip([scale_cell, scale_cell],
                    [date, date],
                    [person, person],
                    [path_to_xlsm, path_to_xlsm],
                    [res_tables_list[:len1], res_tables_list[len1:]],
                    [real_sensors[:len1], real_sensors[len1:]]
                    [status, status]
                    )
            with Pool(2) as p:
                res = p.starmap(func=self.put_in_xlsm, iterable=args)
                print('\n\n\t\tresults from Pool', res, '\n\n')
                # лучше запускать процессы отдельно и проверять их ответы в очереди
            # for r in res:
            #     if 'Недозволенное число картинок!' in r:
            #         self.__logger.error('Error!, Недозволенное число картинок!')
            #         print('Error!, Недозволенное число картинок!')
        else:
            self.put_in_xlsm(scale_cell, date, person, path_to_xlsm, res_tables_list, real_sensors, status)       
        # поиск пиков по производной
        # проверка числа пиков
        # запись в xlsm человека, который обработал настройку
        QtWidgets.QApplication.restoreOverrideCursor()
        self.progress_signal.emit({'visible': False})
        self.__logger.info(f'Завершил')
        print(f'Общее время: {perf_counter() - t__0}')
        self.__logger.info(f'Общее время: {perf_counter() - t__0}')
        print(f'Только excel: {perf_counter() - t__1}')
        self.__logger.info(f'Только excel: {perf_counter() - t__1}')
        DataBase.resetCycle()

    def get_validate_sensors(self, directory):
        sensors1 = DataBase.sensors_from_str(directory)
        real_sensors = DataBase.validate_sensors(sensors1)
        print(real_sensors)
        ind = []
        for i, sensor in enumerate(sensors1):
            if sensor in real_sensors:
                ind.append(i)
            elif len(sensor) > 2:
                self.__logger.warning(f'Не нашел СЛ для {sensor}!')
                print(f'Не нашел СЛ для {sensor}')
        if not len(ind): return False
        smoothed_array = ', '.join(real_sensors)
        print("sensors indexes", ind)
        self.__logger.info(f"sensors indexes: {ind}")
        self.__logger.info(f'Планирую обработать датчики {smoothed_array}')
        # --- ---
        # --- check xlsm ---
        path_to_xlsm = DataBase.get('excel lists folders')
        settings_cell = DataBase.get('scale factors table cell', '')
        already_processed_array = []
        for i, sensor in enumerate(real_sensors):
            path = f'{path_to_xlsm}/{sensor}.xlsm'
            check_res = DataBase.xlsm_reader(path, settings_cell)
            print('\n\n\n\n\n', 'check_res', check_res, '\n\n\n\n\n')
            if not (check_res is None or np.isnan(check_res)):
                already_processed_array.append(sensor)
        if len(already_processed_array):
            already_processed_array = ', '.join(already_processed_array)
            msg = QtWidgets.QMessageBox(
                parent=self,
                text=f"Для датчиков {already_processed_array}, скорее всего, уже есть настройка. Продолжить?")
            msg.setStandardButtons(
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No)
            # ---
            self.__logger.error(f"Здесь нужно не забыть включить проверку!")
            # if msg.exec() == msg.StandardButton.No:
            #     self.__logger.info(f"Отмена")
            #     return False
        return ind

    def get_filenames(self, temps):
        """Get filenames, check conditions"""
        if not self.on_fly_checkbox.isChecked(): # !!!!
            files = []
            path_for_file_serch = os.getcwd()
            for temp in temps:
                file, _ = QtWidgets.QFileDialog.getOpenFileName(
                    self,
                    f"Выберите файл с темературой {temp}",
                    path_for_file_serch,
                    "Text Files(*.txt)")
                if not file: return False, False
                path_for_file_serch = os.path.normpath(os.path.dirname(file))
                files.append([file])
            directory = path_for_file_serch
            # directory = os.path.basename(path_for_file_serch)
            # file = QtWidgets.QFileDialog.getExistingDirectory(
            #     self, f"Выберите папку с настройкой", os.getcwd())
            # тут тоже нужно создать переменную directory
        else:
            settings_directory = DataBase.get('settings results folder', None)  # !!!
            print('settings_directory', settings_directory)
            self.__logger.info(f'directory {settings_directory}')
            search_pattern = DataBase.get('search_pattern')
            print('search_pattern', search_pattern)
            for path in os.scandir(settings_directory):
                if not path.is_dir(): continue
                folder_search_result = re.findall(search_pattern, path.name)
                print(search_pattern, folder_search_result, path.name)
                if folder_search_result: break
                # а что если папок с таким именем несколько?
                # найдется первая или последняя?
            if not folder_search_result:
                self.__logger.error(f'Не нашел папку!')
                print(f'Не нашел папку!')
                return False, False
            else:
                directory = path
                self.__logger.info(f'Выискал папку {path.name}')
                print(f'Выискал папку {path.name}')
            files = []
            patterns = []
            for _, temp in enumerate(temps):
                # pattern = f'_\{temp}' + r'_[MK-МК]_' # f'_{temp}_[AM-АМ]_'
                patterns.append(f'_\{temp}' + r'_MK_')
                patterns.append(f'_\{temp}' + r'_МК_')
                if int(temp) > 0:
                    temp = str(int(temp))
                    patterns.append(f'_{temp}' + r'_MK_')
                    patterns.append(f'_{temp}' + r'_МК_')
                files_for_certain_temp = []
                print(patterns)
                for path in os.scandir(directory):
                    print(path)
                    # с таким же именем не должно быть папок (те же датчики, но другая дата)
                    if not (path.is_file() and os.path.splitext(path.name)[1] == '.txt'):
                        continue
                    for pattern in patterns:
                        search_result = re.findall(pattern, path.name)
                        text = f'result: {pattern}, {search_result}, {path.name}'
                        self.__logger.info(text) ; print(text)
                        if len(search_result) > 0:
                            files_for_certain_temp.append(path)
                            continue

                    # search_result = re.findall(pattern1, path.name) 
                    # print('path.name', search_result, path.name)
                    # self.__logger.info(f'path.name {search_result} {path.name}')
                    # if len(search_result) > 0:
                    #     files_for_certain_temp.append(path)
                    #     continue
                    # search_result = re.findall(pattern2, path.name) 
                    # if len(search_result) > 0:
                    #     files_for_certain_temp.append(path)
                if len(files_for_certain_temp) == 0:
                    text = f'Не сумел отыскать файл для темературы {temp}'
                    self.__logger.error(text) ; print(text)
                    return False, False
                files.append(files_for_certain_temp)
            # далее надо найти папку с датчиками и их нее выбрать нужные записи
            print(files)
        return directory, files
   
    @staticmethod
    def put_in_xlsm(scale_cell, date, person, path_to_xlsm, res_tables_list, real_sensors, status):
        # scale_cell = DataBase.get('scale factors table cell')
        print('scale_cell', scale_cell)
        # return 'ddd'
        import xlwings as xw
        with xw.App(visible=False) as app:
            for sensor, res_tables in zip(real_sensors, res_tables_list):
                path = f'{path_to_xlsm}/{sensor}.xlsm'
                # self.__logger.info(f'work with {path}')
                print(f'work with {path}')
                # print(res_tables)
                # save table in xlsm
                t0 = perf_counter()
                DataBase.xlsm_write(
                    path, ['Сопроводительный лист', 'Настройка КП'],
                    [['B46', 'G46', 'I46'], [scale_cell]],
                    [[status, date, person], [res_tables[:, :].round(4).tolist()]],  # с округлением!!!!
                    app=app
                    )
                print(f'save in Excel all for {sensor} t = ', perf_counter() - t0)
        return 'Ok'
# --- --------------------------------------------------------------------------------
    def get_current_setting(self) -> dict:
        """dict name: 'scale calculation'"""
        dict = {
            'scale calculation on_fly': self.on_fly_checkbox.isChecked(),
            'users list': [self.person_cb.itemText(i) for i in range(self.person_cb.count())],
            'last user': self.person_cb.currentText(),
            # 'last type': self.type_cb.currentIndex(),
            'write status': self.write_status_checkbox.isChecked()
            }
        common_dict = DataBase.get('__dict_with_app_settings')
        common_dict['scale calculation'] = dict
        DataBase.setParams(__dict_with_app_settings=common_dict)

    def restore_settings(self, dict: dict):
        """dict name: 'scale calculation'"""
        if res := dict.get('scale calculation on_fly', False):
            self.on_fly_checkbox.setChecked(res)
        if res := dict.get('write status'):
            self.write_status_checkbox.setChecked(res)
        # if res := dict.get('last type'): # по идее это от проекта зависит!!!!
        #     self.type_cb.setCurrentIndex(res)
        if res := dict.get('users list'):
            self.person_cb.clear()
            self.person_cb.addItems(res)
            if res := dict.get('last user'):
                i = self.person_cb.findText(res)
                if i >= 0:
                    self.person_cb.setCurrentIndex(i)
                else:
                    self.person_cb.setCurrentIndex(0)


