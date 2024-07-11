# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

from time import sleep, perf_counter
import os
import re
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from widgets.PyQt_CustomPushButton import CustomButton
from CustomQTextEdit import CustomQTextEdit

import DataBase


class HeaderFilesMakerGroupbox(QtWidgets.QGroupBox): # h-files
    progress_signal = QtCore.pyqtSignal(dict)
    def __init__(self, settings=None, *args, **kwds):
        QtWidgets.QGroupBox.__init__(self, *args, **kwds)
        self.status = 'error'
        self.__logger = DataBase.get('Logger', None)  # !!!
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(3, 5, 3, 3)
        # ---
        self.header_maker_button = CustomButton('Считать')
        layout.addWidget(self.header_maker_button)
        self.header_maker_button.clicked.connect(self.process)
        # ---
        self.path_te = CustomQTextEdit(
            'project/headers/...', objectName="with_border", maximumHeight=80)
        layout.addWidget(self.path_te)
        # ---
        self.open_button = CustomButton('Открыть папку')
        layout.addWidget(self.open_button)
        # --- нужна возможность брать данные по номерам из папки автоматически
        self.on_fly_checkbox = QtWidgets.QCheckBox("Get path on fly")
        layout.addWidget(self.on_fly_checkbox)
        # ---
        if settings: self.restore_settings(settings)

    # ---   -------------------------------------------------------------------------------
    def process(self, path_to_save_headers: str = None,
                path_to_xlsm_lists: str = None, sensors=None): # добавить moveToThread
        # нужно делать запрос к базе данных, чтобы получить sensors
        if not sensors:
            sensors = DataBase.get('sensors', None)  # !!!
            if not sensors:
                self.__logger.warning('Сожалею, но для вызова функции не хватает параметров')  # !!!
                return False
        if not path_to_save_headers: # учесть опцию get on fly в противном случае вызвать диалоговое окно
            path_to_save_headers = DataBase.get('h-files folders', None)  # !!!
            if not path_to_save_headers:
                self.__logger.warning('Сожалею, но для вызова функции не хватает параметров')  # !!!
                return False
        if not path_to_xlsm_lists: # учесть опцию get on fly в противном случае вызвать диалоговое окно
            path_to_xlsm_lists = DataBase.get('excel lists folders', None)  # !!!
            if not path_to_xlsm_lists:
                self.__logger.warning('Сожалею, но для вызова функции не хватает параметров')  # !!!
                return False

        if not self.on_fly_checkbox.isChecked(): # !!!!
            path_to_save_headers = QtWidgets.QFileDialog.getExistingDirectory(
                self, "Выбрать папку", '')
            if not path_to_save_headers:
                return False

        print(sensors, path_to_save_headers, path_to_xlsm_lists)
        DataBase.setCycle()

        self.progress_signal.emit({'value': 0})
        self.progress_signal.emit({'maximum': len(sensors)}) # ???
        self.progress_signal.emit({'visible': True}) # ???
        QtWidgets.QApplication.setOverrideCursor(
            QtCore.Qt.CursorShape.BusyCursor)
        
        with open(DataBase.get('h-files template', ''), mode='r',
                  encoding='utf-8') as file:
            template = file.read()
        ok_list = []
        not_ok_list = []
        for i, sensor in enumerate(sensors):  #
            res = self.process_single_item(
                template=template,
                path_to_lists=path_to_xlsm_lists,
                paths_to_save=path_to_save_headers, 
                sensor=sensor)
            if res: ok_list.append(sensor)
            else: not_ok_list.append(sensor)
            self.progress_signal.emit({'value': i + 1})
        if not_ok_list:
            not_ok_list = ', '.join(not_ok_list)
            self.__logger.error(f"Для датчиков {not_ok_list} не смог собрать h-файлы")
            msg = QtWidgets.QMessageBox(
                parent=self,
                text=f"Для датчиков {not_ok_list} не смог собрать h-файлы")
                # text=f"Для датчиков {not_ok_list} не смог собрать h-файлы. Сохранить результаты для остальных датчиков?")
            msg.setStandardButtons(
                QtWidgets.QMessageBox.StandardButton.Yes)
                # | QtWidgets.QMessageBox.StandardButton.No)
            if msg.exec() == msg.StandardButton.No:
                self.__logger.info(f"Отмена")
                return False
        if ok_list:
            ok_list = ', '.join(ok_list)
            self.__logger.info(f"Собрал и сохранил h-файлы для {ok_list}")
        else: self.__logger.error(f"Ничего не получилось...")
            # --- end check ---            
        QtWidgets.QApplication.restoreOverrideCursor()
        self.progress_signal.emit({'visible': False})
        DataBase.resetCycle()

    def process_single_item(self, template: str, path_to_lists: str, paths_to_save: str,
                            sensor: str):
        # --- ---
        self.status = 'ok'
        t0 = perf_counter()
        try:
            df = DataBase.xlsm_reader(path_to_lists + '/' + sensor + '.xlsm')
        except FileNotFoundError:
            self.__logger.warning(f'Не сумел отыскать {path_to_lists + "/" + sensor + ".xlsm"}')
            self.status = 'error'
            return False
        # print(type(df))
        # print('df.size = ', df.size)
        # print('df = ', df)
        # df.index += 1
        # можно в df переименовать заголовки строк и столбцов так, чтобы они 1 в 1 совпадали с Excel
        t1 = perf_counter()

        # --- delete comments ---
        pattern = r'\/\/(.*?)\n'
        comments = re.findall(pattern, template) # можно их удалять
        template_to_find = template
        for comment in comments:
            template_to_find = template_to_find.replace(comment, '')

        # --- single value substitution ---
        pattern = r'\s\b[A-Z]{1,3}[0-9]{1,3}\b\s'
        cells = re.findall(pattern, template_to_find)
        for cell in cells:
            template = template.replace(cell, self.repl_single(cell, df))
        
        # --- array substitution ---
        pattern = r'\s\b[A-Z]{1,3}[0-9]{1,3}\:[A-Z]{1,3}[0-9]{1,3}\b'
        cells = re.findall(pattern, template_to_find)
        for cell in cells:
            val = self.get_df(cell, df)
            template = template.replace(cell, self.repl_array(cell, val))
        # --- lengths substitution ---
        pattern = r'\s\|[A-Z]{1,3}[0-9]{1,3}\:[A-Z]{1,3}[0-9]{1,3}\|\s'
        cells = re.findall(pattern, template_to_find)
        for cell in cells:
            base2 = self.insert_len(cell, df)
            template = template.replace(cell, base2)

        # --- multi array substitution ---
        pattern = r'\([A-Z]{1,3}[0-9]{1,3}' # (.*?){1,30}
        cells_b = re.findall(pattern, template_to_find)
        pattern = r'[A-Z]{1,3}[0-9]{1,3}\)' # (.*?){1,30}
        cells_e = re.findall(pattern, template_to_find)
        for cell_b, cell_e in zip(cells_b, cells_e):
            i_b = template.find(cell_b)
            i_e = template.find(cell_e) + len(cell_e)
            new_template = template[i_b + 1:i_e - 1]
            new_template_to_repl = template[i_b:i_e]
            pattern = r'[A-Z]{1,3}[0-9]{1,3}\:[A-Z]{1,3}[0-9]{1,3}'
            cells_n = re.findall(pattern, new_template)
            data_union = []
            for cell_n in cells_n:
                res: pd.DataFrame = self.get_df(cell_n, df)
                res = res.iloc[:, 0].to_numpy()
                data_union.append(res)
                print(res)
            print(data_union)
            try:
                data_union = np.array(data_union)
            except ValueError:
                print('ValueError')
                self.__logger.warning(f'Ошибка при сборке из ячеек {cell_b}:{cell_e}!')
                self.status = 'error'
                continue
            result_df = pd.DataFrame(data_union.transpose())
            # print('result_df', result_df.columns)
            # print('result_df', result_df.index)
            # print('result_df', result_df)
            base2: str = self.repl_array(new_template_to_repl, result_df)
            # ---
            # new_template = new_template.replace(cell_n, base2)
            # new_template = base2
            # print('new_template now ', new_template)
            # pattern = r'[^:][A-Z]{1,3}[0-9]{1,3}[^:]'
            # cells_n = re.findall(pattern, new_template)
            # print(new_template, cells_n)
            # for cells_n in cells:
            #     new_template = new_template.replace(cells_n, repl_single(cells_n, df))
            # print('new_template_to_repl ', new_template_to_repl)
            # print('new_template ', new_template)
            template = template.replace(new_template_to_repl, base2)
        # ---
        print('without read & write', perf_counter() - t1)
        print('without writitng', perf_counter() - t0)
        # ---
        if self.status is 'ok':
            for path_to_save in paths_to_save:
                with open(path_to_save + sensor + '.h', mode='w+', encoding='utf-8') as file:
                    file.write(template)
        print('total', perf_counter() - t0)
        self.__logger.info(f'Full time :{perf_counter() - t0}')
        if self.status is 'ok': return True
        else: return False
    # ---   -------------------------------------------------------------------------------

    @staticmethod
    def custom_repl(date: str, to_repl: dict):
        for x, y in to_repl.items():
            date = date.replace(x, y)
        return date

    def get_df(self, cell, df: pd.DataFrame):
        cell = self.custom_repl(cell, {'\n': '', ' ': ''})
        date1, date2 = re.split(':', cell)
        # ---
        start_coords = DataBase.get_coords(date1)
        end_coords = DataBase.get_coords(date2)
        # ---
        val = df.iloc[start_coords[0]:end_coords[0] + 1,
                        start_coords[1]:end_coords[1] + 1]  # [строка, столбец]
        val = val.dropna()
        if val.shape[1] > 1:
            d_arr = np.diff(np.array(val.iloc[:, 0]))
            if not all(d_arr >= 0) and not all(d_arr <= 0):
                val = f'Нестандартная ситуация: не монотонная функция в ячейках {cell}'
                print(val)
                self.__logger.warning(val)
                self.status = 'error'
        return val

    def repl_single(self, cell: str, df: pd.DataFrame):
        base: str = cell
        cell = self.custom_repl(cell, {'\n': '', ' ': ''})
        coords = DataBase.get_coords(cell)
        val = df.iat[coords[0], coords[1]]  # [строка, столбец]
        if pd.isna(val):
            val = f'Настораживающее обстоятельство: нет числа в ячейке {cell}'
            print(val)
            self.__logger.warning(val)
            self.status = 'error'
        # print(type(val), val, pd.isna(val))
        else:
            if val == 0 or type(val) == float:
                val = int(val)
            if cell == 'A2':  # device number
                val = int(str(val)[3:])
                # print(val)
            if cell == 'H9':  # hex
                val = '0x' + val
                # print(val)
        return base.replace(cell, f'{val}')

    def repl_array(self, cell: str, val: pd.DataFrame):
        base: str = cell
        if type(val) == str:
            return base.replace(cell, val)
        val = val.astype(int)
        csv_string = val.to_csv(sep=",", index=False, header=False)
        # ---
        if (val.shape[1] == 1):
            csv_string = '\n{\n\t' + self.custom_repl(csv_string, {'\n': '\t', '\r': ',\n'})[:-3] + '\n};'
        else:
            csv_string = '\n{\n\t{' + self.custom_repl(csv_string, {'\n': '\t{', '\r': '},\n'})[:-4] + '\n};'
        # ---
        return base.replace(cell, csv_string)

    def insert_len(self, cell: str, df: pd.DataFrame):
        base: str = cell
        cell = self.custom_repl(cell, {'\n': '', ' ': ''})
        date1, date2 = re.split(':', cell)
        # ---
        start_coords = DataBase.get_coords(date1)
        end_coords = DataBase.get_coords(date2)
        val = df.iloc[start_coords[0]:end_coords[0] + 1,
                start_coords[1]:end_coords[1] + 1]  # [строка, столбец]
        val = val.dropna()
        if not val.size:
            text = f'Странное обстоятельство: нулевая длина данных в ячейках {cell}'
            self.__logger.warning(text); print(text)
            self.status = 'error'
        # template = template.replace(cell, f'{val.size}')
        return base.replace(cell, f'{val.size}')

    def get_current_setting(self):
        """dict name: 'header maker'"""
        dict = {
            'header assembly on_fly': self.on_fly_checkbox.isChecked()
            }
        common_dict = DataBase.get('__dict_with_app_settings')
        common_dict['header maker'] = dict
        DataBase.setParams(__dict_with_app_settings=common_dict)
        # return dict

    def restore_settings(self, dict: dict):
        """dict name: 'header maker'"""
        if res := dict.get('header assembly on_fly', False):
            self.on_fly_checkbox.setChecked(res)

# with open('D:\GyroResultsProcessing\h-files templates\DeviceXXXX.h') as file:
#     template = file.read()

# process_single_item(
#     template, 'D:\GyroResultsProcessing\\',
#     'D:\GyroResultsProcessing\\', '1101509', project_type=0)