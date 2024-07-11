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

import DataBase

from multiprocessing import Pool, Manager

class CheckResultsProcessingGroupbox(QtWidgets.QGroupBox): # final processing
    progress_signal = QtCore.pyqtSignal(int)
    def __init__(self, settings=None, *args, **kwds):
        QtWidgets.QGroupBox.__init__(self, *args, **kwds)
        self.__logger = DataBase.get('Logger', None)  # !!!
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(3, 5, 3, 3)
        # ---
        self.lbl_table = QtWidgets.QTableWidget(6, 1, parent=self)
        self.lbl_table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.lbl_table.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch)
        # self.lbl_table.setColumnCount(1)
        # self.lbl_table.setRowCount(6)
        self.lbl_table.horizontalHeader().hide()
        self.lbl_table.setVerticalHeaderLabels([
            'Время готовности, с',
            'Малый интервал, с',
            'Время работы, с',
            'Время записи, с',
            'Интервал ненуля, с',
            'Частота приема, Гц'
            ])
        # items_text = ['3', '5', '70', '-', '-', '200'] # можно сюда настройки передавать просто
        # for i, text in enumerate(items_text):
        for i in range(6):
            item = QtWidgets.QTableWidgetItem() # text)  # не нужен текст
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.lbl_table.setItem(i, 0, item)
        # горизонтальный скролбар не появится, т.к. всего один столбец в таблице
        layout.addWidget(self.lbl_table)
        # ---
        self.process_all_button = CustomButton('Считать')
        layout.addWidget(self.process_all_button)
        self.process_all_button.clicked.connect(self.process)
        # ---
        self.path_te = CustomQTextEdit(objectName="with_border", maximumHeight=80)
        layout.addWidget(self.path_te)
        # ---
        self.on_fly_checkbox = QtWidgets.QCheckBox("Get folder on fly")
        layout.addWidget(self.on_fly_checkbox)
        # ---
        self.on_fly_files_checkbox = QtWidgets.QCheckBox("Get files in folder on fly")
        layout.addWidget(self.on_fly_files_checkbox)
        # --- ---
        from widgets.tab_widget.PyQt_CustomViewBox import CustomViewBox
        from QtCustomPlot import CustomPlot
        import pyqtgraph as pg
        # ---
        self.LABEL_STYLE = {'color': '#000000', 'font-size': '16px'}
        
        # self.COLORS = [
        #     QtGui.QColor(int('22', base=16), int('22', base=16), 255, alpha=25),
        #     QtGui.QColor(255, 0, 0, alpha=25),
        #     QtGui.QColor(0, int('BB', base=16), 0, alpha=25)]
        self.COLORS = [f"#2222FF", f"#FF0000", f"#00BB00"]
        self.CURVE_PARAMS = {'skipFiniteCheck': True, 'useCache': False, 'autoDownsample': True} # , 'dynamicRangeHyst': 1 , 'dynamicRangeLimit': 1e3
        # pg.setConfigOption('background', '#EEEEEE')  # '#151515'
        self.plot1 = CustomPlot(viewBox=CustomViewBox())
        self.plot1.setBackground(QtGui.QColor(255, 255, 255)) # alpha
        plotItem1 = self.plot1.plotItem
        plotItem1.clear()
        plotItem1.titleLabel.setMinimumHeight(30)
        plotItem1.setTitle(f', КП №', size=f'{14}pt')
        # plotItem1.setDownsampling(False)
        plotItem1.setLabel('left', 'Показания', **self.LABEL_STYLE)
        plotItem1.setLabel('bottom', 'Время', **self.LABEL_STYLE) #,
        plotItem1.addLegend(offset=(-1, 1), labelTextSize=f'{14}pt',
                            labelTextColor=pg.mkColor('#000000'))
        plotItem1.plot(
            pen=pg.mkPen(self.COLORS[0], width=0.75), name='ПЛУ', **self.CURVE_PARAMS)
        plotItem1.plot(
            pen=pg.mkPen(self.COLORS[1], width=0.75), name='ПУС', **self.CURVE_PARAMS)
        plotItem1.plot(
            pen=pg.mkPen(self.COLORS[2], width=1.25), name='Т', **self.CURVE_PARAMS)
        self.plot1.resize(800, 800) # didn't work without showing, only 640x480 image
        # --- 
        self.plot2 = CustomPlot(viewBox=CustomViewBox())
        self.plot2.setBackground(QtGui.QColor(255, 255, 255))
        plotItem2 = self.plot2.plotItem
        plotItem2.clear()
        plotItem2.titleLabel.setMinimumHeight(30)
        plotItem2.setTitle(f', КП №', size=f'{14}pt')
        # plotItem2.setDownsampling(False)
        plotItem2.setLabel('left', 'Показания', **self.LABEL_STYLE)
        plotItem2.setLabel('bottom', 'Температура', **self.LABEL_STYLE)
        plotItem2.addLegend(offset=(-1, 1), labelTextSize=f'{14}pt',
                            labelTextColor=pg.mkColor('#000000'))
        plotItem2.plot(pen=pg.mkPen(self.COLORS[0], width=0.5), name='0', **self.CURVE_PARAMS)
        plotItem2.plot(pen=pg.mkPen(self.COLORS[2], width=1.25), name='среднее', **self.CURVE_PARAMS)
        self.plot2.resize(800, 800) # didn't work without showing

        if settings: self.restore_settings(settings)
# --- -----------------------------------------------------------------------------
    def get_validate_sensors(self, check_results_folder_name):
        # --- get sensors ---
        sensors1 = DataBase.sensors_from_str(check_results_folder_name)
        real_sensors = DataBase.validate_sensors(sensors1)
        print(real_sensors)
        # --- compare ---
        ind = []
        for i, sensor in enumerate(sensors1):
            if sensor in real_sensors:
                ind.append(i)
            elif len(sensor) > 2:
                self.__logger.warning(f'Не нашел СЛ для {sensor}!')
        if not len(ind):
            return False, False, False
        res = ', '.join(real_sensors)
        print("sensors indexes", ind)
        np_ind = np.array(ind) + 1
        self.__logger.info(f"sensors indexes: {ind}")
        self.__logger.info(f'Планирую обработать КП {np_ind} c даитчиками {res}')
        path_to_xlsm = DataBase.get('excel lists folders')
        check_cell = DataBase.get('check results table cell', '')
        _scale_factors_cells: list = DataBase.get('scale factors for temps')
        check_temperatures: list = DataBase.get('check temperatures')
        # dict.values()
        all_scale_factors_cells = [*_scale_factors_cells[0].values(), *_scale_factors_cells[1].values()]
        print('\n\n\n', 'scale_factors_cells', all_scale_factors_cells, '\n') ################
        # --- check sensors ---
        already_processed_array = []
        scale_factors_array = [] # для каждого датчика 2 массива (один для первого канала, другой - для второго)
        for i, sensor in enumerate(real_sensors):
            path = f'{path_to_xlsm}/{sensor}.xlsm'
            scale_factors = DataBase.xlsm_reader(
                path,
                all_scale_factors_cells, # сначала аксель, потом гирик, по 3 в каждом
                )

            print('int(len(scale_factors) / 2):', int(len(scale_factors) / 2),
                  f'\nscale_factors for {sensor}: {scale_factors}')
            if len(check_temperatures) != len(scale_factors) / 2:
                print('Не хватает масштабников для всех проверок!')
                self.__logger.error('Не хватает масштабников для всех проверок!')
                res = (len(check_temperatures) - int(len(scale_factors) / 2)) / 2
                print(res)
                if (len(check_temperatures) - int(len(scale_factors) / 2)) % 2 == 0:
                    scale_factors1 = []
                    scale_factors2 = []
                    for i, t in enumerate(check_temperatures):
                        if int(t) == 23:
                            scale_factors1.append(scale_factors[0]) #_scale_factors_cells[0]['+23']
                            scale_factors2.append(scale_factors[3]) # _scale_factors_cells[1]['+23']
                        elif int(t) < 0:
                            scale_factors1.append(scale_factors[1]) # _scale_factors_cells[0]['-50']
                            scale_factors2.append(scale_factors[4]) # _scale_factors_cells[1]['-50']
                        elif int(t) >= 0:
                            scale_factors1.append(scale_factors[2]) #_scale_factors_cells[0]['+50']
                            scale_factors2.append(scale_factors[5])  # _scale_factors_cells[1]['+50']
                    # scale_factors1 = [scale_factors1[0] * res, *scale_factors1, scale_factors1[-1] * res]
                    # scale_factors2 = [scale_factors2[0] * res, *scale_factors2, scale_factors2[-1] * res]
                    self.__logger.error(f'Добавил масштабников. Теперь: {scale_factors1}; {scale_factors2}')
                else:
                    self.__logger.error('Не смог исправить ошибку')
                    return False, False, False
            else:
                scale_factors1 = scale_factors[:int(len(scale_factors) / 2)]
                scale_factors2 = scale_factors[int(len(scale_factors) / 2):]

            if not all(scale_factors):
                self.__logger.warning(
                    f'Сожалею, но в {os.path.basename(path)} не вписан масштабный коэффициент,' +
                    f' см. ячейки {all_scale_factors_cells}')  # !!!
                    # f' см. ячейки {scale_factors_cells}')  # !!!
                return False, False, False
            scale_factors_array.append([scale_factors1, scale_factors2])
            # --- check xlsm ---
            check_res = DataBase.xlsm_reader(path, check_cell)
            if not (check_res is None or np.isnan(check_res)):
                already_processed_array.append(sensor)
        if len(already_processed_array):
            already_processed_array = ', '.join(already_processed_array)
            msg = QtWidgets.QMessageBox(
                parent=self,
                text=f"Для датчиков {already_processed_array}, скорее всего, уже есть обработка проверок. Продолжить?")
            msg.setStandardButtons(
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No)
            # ---
            self.__logger.error(f"Здесь нужно не забыть включить проверку!")
            # if msg.exec() == msg.StandardButton.No:
            #     self.__logger.info(f"Отмена")
            #     return False, False, False
            # --- end check ---
        print('\nscale_factors_array:', scale_factors_array, '\n')
        return ind, real_sensors, scale_factors_array
    
    def get_filefolder(self, check_folder):
        if not self.on_fly_checkbox.isChecked(): # !!!!
            self.__logger.error(f'Код еще не написан!')
            check_results_folder_name = '2024-06-20_1101285_1101026_1101383_x_x_1101262_1101250.2_x_1101698_x_x_x'
        else:
            search_pattern = DataBase.get('search_pattern')
            for path in os.scandir(check_folder):
                if not path.is_dir():
                    continue
                res = re.findall(search_pattern, path.name)
                print(search_pattern, res, path.name)
                if res: break
            if not res:
                self.__logger.error(f'Не нашел папку!')
                return False
            check_results_folder_name = path.name
        return check_results_folder_name

# --- main function -----------------------------------------------------------------------
    def process(self,
                paths_to_xlsm: str = None,
                check_folder: str = None, # путь к папкам с проверками
                processing_type: int = None,
                fs: int = None,
                check_results_folder_name = None, # имя папки с проверками
                time_step: int = None,
                ready_time: int = None,
                total_time: int = None): # добавить moveToThread

        # всякие проверки и возможность выбирать папку вручную
        if not check_folder: # учесть опцию get on fly в противном случае вызвать диалоговое окно
            check_folder = DataBase.get('check results folder')  # !!!
            if not check_folder:
                self.__logger.warning('Сожалею, но для вызова функции не хватает параметров')  # !!!
                return False
        if not paths_to_xlsm: # учесть опцию get on fly в противном случае вызвать диалоговое окно
            paths_to_xlsm = DataBase.get('excel lists folders')  # !!!
            if not paths_to_xlsm:
                self.__logger.warning('Сожалею, но для вызова функции не хватает параметров')  # !!!
                return False
        if not processing_type: # учесть опцию get on fly в противном случае вызвать диалоговое окно
            processing_type = DataBase.get('processing type')  # !!!
            if not processing_type:
                self.__logger.warning('Сожалею, но для вызова функции не хватает параметров')  # !!!
                return False

        if not ready_time: #
            ready_time = int(self.lbl_table.item(0, 0).text()) #.data(0)) # 3
        if not time_step: #
            time_step = int(self.lbl_table.item(1, 0).text()) #.data(0)) # 5

        if processing_type == 2:
            initial_interval = int(self.lbl_table.item(4, 0).text()) #

        if not total_time: #
            total_time = int(self.lbl_table.item(2, 0).text()) #.data(0)) # 70
        if not fs: #
            fs = int(self.lbl_table.item(5, 0).text()) #.data(0)) # 200

        t__0 = perf_counter()

        if not check_results_folder_name: #
            check_results_folder_name = self.get_filefolder(check_folder)
            # лучше имена файлов получать здесь
            # будет более модульно
            # также проще проверить на различие в числе файлов и т.д.
        if not check_results_folder_name: return False
        # --- get sensors indexes ---
        ind, real_sensors, scale_factors_array = self.get_validate_sensors(check_results_folder_name)
        if not ind: return False
        print(ind)
        # --- end check ---
        # здесь надо 5 опций передать
        self.progress_signal.emit({'visible': True})
        QtWidgets.QApplication.setOverrideCursor(
            QtCore.Qt.CursorShape.BusyCursor)
        # --- start processing ---
        if processing_type == 1:
            # обработка температур
            index_step = time_step * fs
            n_sensors_reduced = len(ind)
            all_acc_results = []
            all_gyro_results = []
            all_acc_starts = []
            all_gyro_starts = []
            all_term_starts = []
            for i, temperature in enumerate(DataBase.get('check temperatures')):
                temp_data_acc = []
                temp_data_gyro = []
                temp_data_term = []
                folder = f'{check_folder}/{check_results_folder_name}/{i + 1}.{temperature}'
                for path in os.scandir(folder):
                    # с таким же именем не должно быть папок (те же датчики, но другая дата)
                    if not (path.is_file() and os.path.splitext(path.name)[1] == '.txt'):
                        continue
                    # лучше имена файлов получать отдельно
                    # будет более модульно
                    # также проще проверить на различие в числе файлов и т.д.
                    array_acc, array_gyro, array_term = self.get_data_from_files(
                        path=path, ind=ind, ready_time=ready_time, total_time=total_time, fs=fs)
                    if array_acc is None or array_gyro is None or array_term is None:
                        self.__logger.warning(
                            f"Сожалею, но '{os.path.basename(path)}'' не удовлетворяет требованиям")
                        return False
                    # всякие _х_ и прочее отбрасывается
                    temp_data_acc.append(array_acc)
                    temp_data_gyro.append(array_gyro)
                    temp_data_term.append(array_term)
                n_interval = int((array_acc.shape[0] - ready_time * fs) / fs / time_step)
                print(f'\narray_acc, t:{temperature}.\n', array_acc); print('\narray_gyro\n', array_gyro)
                # ---
                # first
                result_acc = self.process_item(temp_data_acc, n_sensors_reduced, index_step, n_interval,
                                               skip=ready_time * fs)
                all_acc_results.append(result_acc) # для трех температур 3 x 5 x 3
                # ---
                # second
                result_gyro = self.process_item(temp_data_gyro, n_sensors_reduced, index_step, n_interval,
                                                skip=ready_time * fs)
                all_gyro_results.append(result_gyro)
                # ---
                all_acc_starts.append(temp_data_acc)
                all_gyro_starts.append(temp_data_gyro)
                all_term_starts.append(temp_data_term)
            print(f"\n\n\nlen result_acc", len(result_acc)); print(f"len result_gyro", len(result_gyro))
            # --- загружаю непрерывку ---
            t = perf_counter() - t__0
            self.progress_signal.emit({'text': 'Process data  from files'})
            folder = f'{check_folder}/{check_results_folder_name}'
            temperature_changes_record = None
            for path in os.scandir(folder):
                if path.is_file() and os.path.splitext(path.name)[1] == '.txt':
                    temperature_changes_record = path
                    break
            if not temperature_changes_record:
                self.__logger.warning('Не найдена непрерывка!')  # !!!
                return False
            acc_continual, gyro_continual, term_continual = self.get_data_from_files(
                path=temperature_changes_record, ind=ind, cut=False)
            print(acc_continual.shape, gyro_continual.shape, term_continual.shape, len(real_sensors))
            # --- объединяю все запуски в один массив ---
            all_term_starts = self.reshape_to_table(all_term_starts)
            all_gyro_starts = self.reshape_to_table(all_gyro_starts)
            all_acc_starts = self.reshape_to_table(all_acc_starts)
            # --- ---
            cwd = os.getcwd() + '/temporary_dir/' # current directory
            if not os.path.isdir(cwd): os.mkdir(cwd)
            images_names = self.make_images(
                real_sensors, ind,
                acc_continual, gyro_continual, term_continual,
                all_acc_starts, all_gyro_starts, all_term_starts,
                cwd=cwd
                )
            self.progress_signal.emit({'text': 'Made images'})
            # --- ---
            # return
            self.put_data_in_xlsm(
                real_sensors, scale_factors_array,
                all_acc_results, all_gyro_results, images_names,
                one_by_one_flag=False) # was one_by_one_flag=False
            self.progress_signal.emit({'text': 'Write in Excel'})
            # DataBase.get('PlotsMaker').process(txt_files=temperature_changes_record)
            # DataBase.to_image(plot.plotItem)
            import shutil
            if os.path.isdir(cwd): shutil.rmtree(cwd) # delete temporary files
            # if not os.path.isdir(cwd): os.rmdir(cwd)
            
        else:
            self.__logger.warning('Сожалею, но ты еще не написал эту часть кода')  # !!!

        QtWidgets.QApplication.restoreOverrideCursor()
        self.progress_signal.emit({'visible': False})
        self.progress_signal.emit({'text': ''})
        self.__logger.info('Я сделаль.')  # !!!
        self.__logger.info(f'processing time without excel: {t}')
        self.__logger.info(f'processing full time: {perf_counter() - t__0}')
        print(f'processing time without excel:', t)
        print(f'processing full time:', perf_counter() - t__0)
        # нужна запись в xlsm человека, который обработал проверку?
# --- main function end -----------------------------------------------------------------------

    def get_data_from_files(self, path, ind, ready_time=3, total_time=70, fs=200, cut=True):
        """ind говорит о том, какие датчики читать"""
        # range_to_read = np.arange(1, n_sensors * 3 + 1) #  читать термодатчик, потом пригодится
        # range_to_read = range_to_read[range_to_read % 3 != 0]  # exclude columns that are multiples of three
        # print(n_sensors, range_to_read, range_to_read.tolist())
        if type(ind) == int:
            range_to_read = [ind + 1, ind + 2, ind + 3]
        else:
            range_to_read = []  #[0]
            for i in ind:
                __i = 1 + i * 3
                [range_to_read.append(__i + n) for n in range(3)]
        frame = DataBase.txt_reader(path_to_list=path, usecols=range_to_read)
        array = frame.to_numpy()
        # print(array.shape)
        if cut:
            end_index = (total_time + ready_time) * fs
            if array.shape[0] < end_index:
                self.__logger.warning('Сожалею, но пакетов недостаточно для обработки!')  # !!!
                return None, None, None
            # print(np.arange(1, n_sensors * 3 + 1) % 3 != 0)
            array = array[:end_index, :].astype(np.float32)  # or ready_time * fs - 1 ?????
        else:
            array = array.astype(np.float32)
        custom_range = np.arange(0, len(ind) * 3)
        range_acc = custom_range[custom_range % 3 == 0]
        range_gyro = custom_range[custom_range % 3 == 1]
        range_term = custom_range[custom_range % 3 == 2]
        # self.__logger.error(f'{path}, {range_to_read}. {range}, {range_acc}, {range_gyro}\{array.shape} {array}') ############################################
        # self.__logger.error(f'{path}, {range_to_read}. {range}, {range_acc}, {range_gyro}\{array.shape} {array}') ############################################
        # print(f'{path}, {range_to_read}, {range}, {range_acc}, {range_gyro}\{array.shape} {array}') ############################################
        print(f'{path}, {range_to_read}, {custom_range}, {range_acc}, {range_gyro}\{array.shape}') ############################################
        return array[:, range_acc], array[:, range_gyro], array[:, range_term]
        # return array
        # также нужно взять только аксели или только гирики

    @staticmethod
    def reshape_to_table(all_lists_data):
        n_temp = len(all_lists_data) # 3 температуры
        n_starts = len(all_lists_data[0]) # 5 запусков в каждой
        sh = all_lists_data[0][0].shape
        res_data = np.ndarray(shape=(sh[0] * n_starts * n_temp, sh[1]))
        for i, list_data in enumerate(all_lists_data): # по температурам
            for j, data in enumerate(list_data):
                n = i * n_starts + j
                res_data[n * sh[0]:((n + 1) * sh[0]), :] = data
        return res_data

    def fff(self, plotItem1, text, name, ext, x2, current_plot1, *opts):
        plotItem1.setTitle(text, size=f'{14}pt')
        for i, o in enumerate(opts):
            plotItem1.curves[i].setData(x=x2, y=o, **self.CURVE_PARAMS)
        DataBase.to_image(current_plot1, name, ext)

    def make_images(self,
                    sensors, ind,
                    acc_continual, gyro_continual, term_continual,
                    acc_starts_data, gyro_starts_data, term_starts_data,
                    cwd,
                    ext='png', # 'jpg', # 'png',
                    decimation: int = 1 # прореживание
                    ):
        import pyqtgraph as pg
        """Make images and save them."""
        plotItem1 = self.plot1.plotItem
        plotItem2 = self.plot2.plotItem
        items = plotItem2.legend.items
        flag = True
        # flag = False
        t0 = perf_counter()
        # --- ---
        if flag:
            widget1 = QtWidgets.QWidget()
            layout1 = QtWidgets.QHBoxLayout(widget1)
            layout1.setContentsMargins(0,0,0,0)
            layout1.addWidget(self.plot1)
            widget1.resize(900, 750)
            widget1.move(0, 0)
            widget2 = QtWidgets.QWidget()
            layout2 = QtWidgets.QHBoxLayout(widget2)
            layout2.setContentsMargins(0,0,0,0)
            layout2.addWidget(self.plot2)
            widget2.resize(850, 700)
            widget2.move(200, 200)
        t1 = perf_counter()
        # --- ---
        temps = ', '.join(DataBase.get('check temperatures'))
        x2 = np.arange(0, acc_continual.shape[0], step=decimation)
        all_sensor_img_names = []
        current_plot1 = widget1 if flag else plotItem1
        current_plot2 = widget2 if flag else plotItem2
        for i, (sensor, index) in enumerate(zip(sensors, ind)):
            names = []
            for curve1 in plotItem1.curves: curve1.setVisible(True)
            # сохраняю:
            # --- непрерывку (1 график, лежит в другой папке) ---
            plotItem1.setTitle(f'{sensor}, КП №{index + 1}', size=f'{14}pt')
            plotItem1.curves[0].setData(x=x2, y=acc_continual[::decimation, i], **self.CURVE_PARAMS)
            plotItem1.curves[1].setData(x=x2, y=gyro_continual[::decimation, i], **self.CURVE_PARAMS)
            plotItem1.curves[2].setData(x=x2, y=term_continual[::decimation, i], **self.CURVE_PARAMS)
            names.append(cwd + f'img_{sensor}_continual.{ext}')
            # self.fff(
            #     plotItem1, f'{sensor}, КП №{index + 1}', names[-1], ext, x2, current_plot1,
            #     acc_continual[::decimation, i], gyro_continual[::decimation, i], term_continual[::decimation, i]
            #     )
            DataBase.to_image(current_plot1, names[-1], ext)
            # ---
            # --- запуски (3 графика) ---
            plotItem1.setTitle(f'{sensor}, КП №{index + 1}. Температуры: {temps}', size=f'{14}pt')
            x1 = np.arange(0, acc_starts_data[:, i].shape[0], step=decimation)
            plotItem1.curves[0].setData(x=x1, y=acc_starts_data[::decimation, i], **self.CURVE_PARAMS)
            plotItem1.curves[1].setData(x=x1, y=gyro_starts_data[::decimation, i], **self.CURVE_PARAMS)
            plotItem1.curves[2].setData(x=x1, y=term_starts_data[::decimation, i], **self.CURVE_PARAMS)
            names.append(cwd + f'img_{sensor}_starts.{ext}')
            # self.fff(
            #     plotItem1, f'{sensor}, КП №{index + 1}. Температуры: {temps}', names[-1], ext, x1, current_plot1,
            #     acc_starts_data[::decimation, i], gyro_starts_data[::decimation, i], term_starts_data[::decimation, i]
            #     )
            DataBase.to_image(current_plot1, names[-1], ext)
            # --- запуски, приближение по оси Y (3 графика) ---
            plotItem1.setTitle(f'{sensor}, ПЛУ, КП №{index + 1}', size=f'{14}pt')
            plotItem1.curves[0].setVisible(True)
            plotItem1.curves[0].setData(x=x1, y=acc_starts_data[::decimation, i], **self.CURVE_PARAMS)
            plotItem1.curves[1].setVisible(False)
            plotItem1.curves[2].setVisible(False)
            names.append(cwd + f'img_{sensor}_starts_acc.{ext}')
            # self.fff(
            #     plotItem1, f'{sensor}, ПЛУ, КП №{index + 1}', names[-1], ext, x1, current_plot1,
            #     acc_starts_data[::decimation, i]
            #     )
            DataBase.to_image(current_plot1, names[-1], ext)
            # ---
            plotItem1.setTitle(f'{sensor}, ПУС, КП №{index + 1}', size=f'{14}pt')
            plotItem1.curves[0].setVisible(False)
            plotItem1.curves[1].setVisible(True)
            plotItem1.curves[1].setData(x=x1, y=gyro_starts_data[::decimation, i], **self.CURVE_PARAMS)
            plotItem1.curves[2].setVisible(False)
            names.append(cwd + f'img_{sensor}_starts_gyro.{ext}')
            DataBase.to_image(current_plot1, names[-1], ext)
            # self.fff(
            #     plotItem1, f'{sensor}, ПУС, КП №{index + 1}', names[-1], ext, x1, current_plot1,
            #     [], acc_starts_data[::decimation, i]
            #     )
            # ---
            # --- температурные зависимости (для акселя и для гирика) ---
            term_data_2, unite_data = DataBase.clear_repeats(
                term_continual[::decimation, i], np.array(
                    [acc_continual[::decimation, i], gyro_continual[::decimation, i]]).transpose())
            plotItem2.setTitle(f'{sensor}, ПУС, КП №{index + 1}', size=f'{14}pt')
            items[0][1].setText(f"ПУС")
            plotItem2.curves[0].setPen(pg.mkPen(self.COLORS[1], width=0.5))
            plotItem2.curves[0].setData(x=term_data_2, y=unite_data[:, 0], **self.CURVE_PARAMS)
            plotItem2.curves[1].setData(
                x=term_data_2, y=DataBase.smooth_data(
                    unite_data[:, 0], n=151, type='savgol', polyorder=3),
                    **self.CURVE_PARAMS)
            names.append(cwd + f'img_{sensor}_gyro.{ext}')
            DataBase.to_image(current_plot2, names[-1], ext)
            # ---
            plotItem2.setTitle(f'{sensor}, ПЛУ, КП №{index + 1}', size=f'{14}pt')
            items[0][1].setText(f"ПЛУ")
            plotItem2.curves[0].setPen(pg.mkPen(self.COLORS[0], width=0.5))
            plotItem2.curves[0].setData(x=term_data_2, y=unite_data[:, 1], **self.CURVE_PARAMS)
            plotItem2.curves[1].setData(
                x=term_data_2, y=DataBase.smooth_data(
                    unite_data[:, 1], n=151, type='savgol', polyorder=3),
                    **self.CURVE_PARAMS)
            names.append(cwd + f'img_{sensor}_acc.{ext}')
            DataBase.to_image(current_plot2, names[-1], ext)
            # ---
            all_sensor_img_names.append(names)

        print(f'image making t = {perf_counter() - t0}, {perf_counter() - t1}')
        self.__logger.error(f'image making t = {perf_counter() - t0}, {perf_counter() - t1}')
        for curve1 in plotItem1.curves: curve1.setData([])
        for curve2 in plotItem2.curves: curve2.setData([])
        if flag:
            self.plot1.setParent(None)
            self.plot2.setParent(None)
        return all_sensor_img_names

    def put_data_in_xlsm(self, sensors, scale_factors_array,
                         all_acc_results, all_gyro_results, image_names, one_by_one_flag=True):
        """Save data and pictures in xlsm."""
        date = DataBase.get_date()
        date_cell = DataBase.get('date cell')

        res_table_cell = DataBase.get('check results table cell')
        path_to_xlsm = DataBase.get('excel lists folders')
        check_res_img_cells = DataBase.get('check results image cells')

        result_np_arr = []
        for j, scale_factors in enumerate(scale_factors_array):
            # j - num of sensor 
            sh = all_acc_results[0].shape
            result_np = np.ndarray(
                shape=(sh[0] * len(all_acc_results), sh[1] * 2), dtype=np.float64)
            for i, (res1, res2) in enumerate(zip(all_acc_results, all_gyro_results)): # цикл по темпертатурам
                # scale_factors должен иметь тот же размер, что и scale_factors[j][:],
                result_np[i*5:(i+1)*5, :sh[1]] = res1[:, :, j] / np.array(scale_factors[0][i]) # тут будет массив из 3х чисел (если НИСП, то из 5)
                result_np[i*5:(i+1)*5, sh[1]:] = res2[:, :, j] / np.array(scale_factors[1][i])
            result_np = np.round(result_np, 5) ############################## round #############################
            result_np_arr.append(result_np)
        # exit()
        t = perf_counter()
        # if True:
        if one_by_one_flag:
            self.save_in_xlsm_multi(
                self.save_in_xlsm_single,
                path_to_xlsm,
                sensors,
                result_np_arr,
                image_names,
                date_cell,
                res_table_cell,
                check_res_img_cells,
                date
            )
        else: # multiprocessing, parallel
            # length = len(sensors)
            # args = zip([path_to_xlsm] * length,
            #         sensors,
            #         result_np_arr,
            #         image_names,
            #         [date_cell] * length,
            #         [res_table_cell] * length,
            #         [check_res_img_cells] * length,
            #         [date] * length,
            #         [None] * length
            #         )
            # with Pool(4) as p:
            #     p.starmap(func=self.save_in_xlsm_single, iterable=args)

            with Pool(processes=2) as p:
                manager = Manager()
                queue = manager.Queue()

                len1 = int(len(sensors) / 2)
                len2 = len(sensors) - len1
                print('\n\n\n lengths:', len1, len2, '\n\n')
                args = zip(
                    [self.save_in_xlsm_single, self.save_in_xlsm_single],
                    [path_to_xlsm, path_to_xlsm],
                    [sensors[:len1], sensors[len1:]],
                    [result_np_arr[:len1], result_np_arr[len1:]],
                    [image_names[:len1], image_names[len1:]],
                    [date_cell, date_cell],
                    [res_table_cell, res_table_cell],
                    [check_res_img_cells, check_res_img_cells],
                    [date, date],
                    [queue, queue]
                    )
                results = p.starmap_async(func=self.save_in_xlsm_multi, iterable=args)
                while (not results.ready()):
                    if not queue.empty():
                        text = queue.get(block=False, timeout=0.5)
                        print('queue1 text:', text)
                    else: sleep(0.5)
                    if perf_counter() - t > 30: break ; print('error!')
                for result in results.get(timeout=5):
                    if result != 'Ok':
                        self.__logger.error(result) ; print(result)
        print('EXCEL:', perf_counter() - t)

    @staticmethod
    def save_in_xlsm_multi(save_in_xlsm_single, path_to_xlsm, sensors,
                            result_np_arr, image_names,
                            date_cell, res_table_cell, check_res_img_cells, date,
                            queue=None):
        res_arr = []
        print('save_in_xlsm_multi')
        import xlwings as xw
        with xw.App(visible=False) as app:
            for _, (sensor, images, result_np) in enumerate(zip(sensors, image_names, result_np_arr)):
                if not queue is None: queue.put(f'Работаю с {sensor}')
                res = save_in_xlsm_single(
                    path_to_xlsm=path_to_xlsm, sensor=sensor, result_np=result_np, images=images,
                    date_cell=date_cell, res_table_cell=res_table_cell,
                    check_res_img_cells=check_res_img_cells, date=date, app=app
                )
                res_arr.append(res)
                if not queue is None: queue.put(res)
        return res_arr

    @staticmethod
    def save_in_xlsm_single(path_to_xlsm, sensor,
                            result_np, images,
                            date_cell, res_table_cell, check_res_img_cells, date, app=None):
        print(f'save_in_xlsm_single {sensor}')
        path = f'{path_to_xlsm}/{sensor}.xlsm'
        t0 = perf_counter()
        # save image in xlsm
        if len(check_res_img_cells) != len(images):
            # Несообразное, Несовместимое, Недозволенное, Неподходящее
            return f'{len(images)} - недозволенное число картинок. Должно быть {len(check_res_img_cells)}! '
        DataBase.xlsm_write(
            path, 'Настройка КП',
            # [date_cell, res_table_cell],
            [date_cell, res_table_cell, *check_res_img_cells],
            # [date, result_np.tolist()],
            [date, result_np.tolist(), *images],
            app
            )
        print(f'save in Excel all for {sensor} t = ', perf_counter() - t0)
        return 'Ok'

    def process_item(self, temperature_data: list[np.ndarray],
                     n_sensors: int, index_step: int,
                     n_interval: int, skip=0): # добавить moveToThread
        """skip - время готовности.
        Бойница, Протазан, НИСП"""
        t0 = perf_counter()
        # print('temperature_data[0].shape', temperature_data[0].shape)
        n_starts = len(temperature_data)
        mean_matrix = np.ndarray(shape=(n_starts, n_sensors))
        mean_vector = np.ndarray(shape=(1, n_sensors))
        for i, single_file_data in enumerate(temperature_data):
            mean_matrix[i, :] = single_file_data[skip:, :].mean(axis=0) # A.mean
            # print(mean_matrix)
        mean_vector = mean_matrix.max(axis=0) # A.meanALL
        print("\nmean_matrix\n", mean_matrix.shape, mean_matrix)
        print("\nmean_vector\n", mean_vector.shape, mean_vector)
        # end first part! mean_vector - смещение общее, а нужно по каждому файлу отдельно!
        # mean_matrix - нужный мне выход
        #
        # subtract mean
        mean_vector_by_interval = np.ndarray(shape=(n_starts, n_sensors))
        std_vector_by_interval = np.ndarray(shape=(n_starts, n_sensors))
        for i, single_file_data in enumerate(temperature_data):
            single_file_data_normalize = np.subtract(single_file_data[skip:, :], mean_vector)
            mean_by_interval = np.ndarray(shape=(n_interval, n_sensors))
            std_by_interval = np.ndarray(shape=(n_interval, n_sensors))
            for j in range(n_interval):
                # правильнее было бы изменить форму массива и найти минимумы по новому измерению
                section = single_file_data_normalize[index_step * j:index_step * (j + 1), :]
                # print(single_file_data_normalize.shape, section.shape, index_step * (j + 1))
                mean_by_interval[j, :] = np.mean(section, axis=0) # np.mean(section, axis=0) - число, если речь об одном датчике
                std_by_interval[j, :] = np.std(section, axis=0)
                # if j ==1:
                #     print(section.shape) # (1000, n) = n - число датчиков
            mean_vector_by_interval[i, :] = np.max(np.abs(mean_by_interval), axis=0)
            std_vector_by_interval[i, :] = np.mean(std_by_interval, axis=0)
        print(" \n mean_vector_by_interval", mean_vector_by_interval)
        print(" \n std_vector_by_interval", std_vector_by_interval)
        #
        result: np.ndarray = np.ndarray(shape=(n_starts, 3, n_sensors), dtype=np.float32)
        result[:, 0, :] = mean_vector
        result[:, 1, :] = mean_vector_by_interval
        result[:, 2, :] = std_vector_by_interval
        # self.__logger.info(f'Вот так вот вышло: <br/>{result}')  # !!! :.3f
        print(f'process item time:', perf_counter() - t0)
        return result

# --- settings -------------------------------------------------------------------------------
    def get_current_setting(self):
        """dict name: 'check processing'"""
        dict = {
            'result processing on_fly': self.on_fly_checkbox.isChecked(),
            }
        for i in range(self.lbl_table.rowCount()):
            header_item = self.lbl_table.verticalHeaderItem(i)
            if header_item is not None and self.lbl_table.item(i, 0) is not None:
                dict[header_item.text()] = self.lbl_table.item(i, 0).text()
        common_dict = DataBase.get('__dict_with_app_settings')
        common_dict['check processing'] = dict
        DataBase.setParams(__dict_with_app_settings=common_dict)
        return True

    # def restore_settings(self, dict: dict, default: dict):
    def restore_settings(self, dict: dict):
        """dict name: 'check processing'"""
        if res := dict.get('result processing on_fly', False):
            self.on_fly_checkbox.setChecked(res)
        for i in range(self.lbl_table.rowCount()):
            header_item = self.lbl_table.verticalHeaderItem(i)
            if header_item is not None and self.lbl_table.item(i, 0) is not None:
                self.lbl_table.item(i, 0).setText(
                    dict.get(header_item.text(), '?')
                    # dict.get(header_item.text(), default.get(header_item.text()))
                    )
        return True

