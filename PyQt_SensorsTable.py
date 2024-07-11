# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g
from time import time, sleep, perf_counter
import numpy as np
import os
import re
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt_Functions import get_icon_by_name
from widgets.PyQt_CustomPushButton import CustomButton
from widgets.PyQt_CustomComboBox import CustomComboBox
from PyQt_Functions import get_res_path  #, natural_keys

import DataBase


class TableItem(QtWidgets.QWidget):
    def __init__(self, n, parent=None, **kwds):
        QtWidgets.QWidget.__init__(self, parent, **kwds)
        self.__logger = DataBase.get('Logger', None)  # !!!
        # ---
        # self.setMinimumHeight(15)
        # layout = QtWidgets.QGridLayout(self, spacing=10)
        layout = QtWidgets.QHBoxLayout(self)
        # ---
        # layout.addWidget(QtWidgets.QLabel(f'КП: {n + 1}', minimumHeight=20), 0, 0, 1, 1)
        label = QtWidgets.QLabel(f'КП: {n + 1}')
        label.setAutoFillBackground(False)
        label.setAttribute(
            QtCore.Qt.WidgetAttribute.WA_TranslucentBackground
            ) # для красивого выделения, чтобы фон тоже выделялся
        layout.addWidget(label)

        self.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenu)

        self.name_line_edit = QtWidgets.QLineEdit()
        self.name_line_edit.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.name_line_edit.customContextMenuRequested.connect(
            self.__contextMenu)
        # layout.addWidget(self.name_line_edit, 0, 1, 1, 1)
        layout.addWidget(self.name_line_edit)
        self.name_line_edit.textChanged.connect(self.__textChangedHandler)
        self.custom_event = self.name_line_edit.keyPressEvent
        self.name_line_edit.keyPressEvent = self.keyPressEvent
        # ---
        # self.__open_folder_action = QtWidgets.QAction(
        #     "Open xlsm", self, shortcut='Ctrl+O')
        # self.__open_folder_action.setShortcutContext(
        #     QtCore.Qt.ShortcutContext.WidgetWithChildrenShortcut)  # !
        # self.__open_folder_action.triggered.connect(
        #     lambda: self.open_excel_file(self.path)) 
        # self.name_line_edit.addAction(self.__open_folder_action)
        # ---
        # self.__update_action = QtWidgets.QAction(
        #     "Update", self, shortcut='Ctrl+U')
        # self.__update_action.setShortcutContext(
        #     QtCore.Qt.ShortcutContext.WidgetWithChildrenShortcut)  # !
        # self.__update_action.triggered.connect(self.update1) 
        # self.name_line_edit.addAction(self.__update_action)
        # ---

    @property
    def path(self):
        to_xlsm = DataBase.get('excel lists folders', '')
        path = f'{to_xlsm}/{self.name_line_edit.text()}.xlsm'
        return path

    def keyPressEvent(self, event): # не работает толком, потому что надо именно на lineedit ставить
        cur = self.name_line_edit.cursorPosition()
        # print('event.key()', event.key())
        # print(cur, len(self.name_line_edit.text()))
        # print(cur == 0, cur == len(self.name_line_edit.text()),
        #       event.key() == QtCore.Qt.Key.Key_Escape,
        #       event.key() == QtCore.Qt.Key.Key_Right)
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.name_line_edit.clearFocus()
        elif event.key() == QtCore.Qt.Key.Key_Left:
            if cur == 0:
                # print('11111!!!!')
                return super().keyPressEvent(event)
        elif event.key() == QtCore.Qt.Key.Key_Right:
            if cur == len(self.name_line_edit.text()):
                # print('222222!!!!')
                return super().keyPressEvent(event)
        # print('custom_event!!!!')
        self.custom_event(event)

    @QtCore.pyqtSlot()
    def __contextMenu(self):
        xlsm_path = self.path
        open_excel_action = QtWidgets.QAction("Открыть Excel файл", self, shortcut='Ctrl+O')
        open_excel_action.triggered.connect(
            lambda: self.open_excel_file(xlsm_path))
        if hasattr(self.sender(), 'createStandardContextMenu'):
            _normal_menu: QtWidgets.QMenu = self.sender().createStandardContextMenu()
            _normal_menu.insertAction(_normal_menu.actions()[0], open_excel_action)
            _normal_menu.insertSeparator(_normal_menu.actions()[1])
        else:
            _normal_menu = QtWidgets.QMenu(self)
            _normal_menu.addAction(open_excel_action)
        # ---
        __update_action = QtWidgets.QAction("Обновить", self, shortcut='Ctrl+U')
        if not self.name_line_edit.text():
            __update_action.setDisabled(True)
        no_file_check = not self.name_line_edit.text() or not os.path.isfile(xlsm_path)
        if no_file_check:
            open_excel_action.setDisabled(True)
            open_excel_action.setStatusTip('Файл не обнаружен')
        # ---
        _normal_menu.insertAction(_normal_menu.actions()[0], __update_action)
        __update_action.triggered.connect(self.update1)
        # ---
        res_cells: dict = DataBase.get('cells to check in context menu') # можно функцию сделать, а лучше объединить
        names = [key for key in res_cells.keys()][::-1]
        request = [key for key in res_cells.values()][::-1]
        res = ['?'] * len(request)
        if not no_file_check:
            res = DataBase.xlsm_reader(xlsm_path, *request)
            for i in range(len(res)):
                res[i] = '-' if res[i] is None or np.isnan(res[i]) else '+'
        for r, req in zip(res, names):
            action = QtWidgets.QAction(f'{req}:\t{r}', self, enabled=False)
            _normal_menu.insertAction(_normal_menu.actions()[0], action)
        # ---
        res_cells: dict = DataBase.get('params to show in context menu')
        names = [key for key in res_cells.keys()][::-1]
        request = [key for key in res_cells.values()][::-1]
        res = ['?'] * len(request)
        if not no_file_check:
            res = DataBase.xlsm_reader(xlsm_path, *request)
        for r, req in zip(res, names):
            action = QtWidgets.QAction(f'{req}:\t{r}', self, enabled=False)
            _normal_menu.insertAction(_normal_menu.actions()[0], action)
        # ---
        _normal_menu.exec(QtGui.QCursor.pos())
        _normal_menu.deleteLater()

    @QtCore.pyqtSlot()
    def __textChangedHandler(self): # а если несколько путей списано?
        """Check dir existence, color thr text."""
        if not self.sender().text():
            self.setStyleSheet("color: " + "#EEEEEE;")
            return
        color = "#00FF00;" if os.path.isfile(self.path) else "#FF1111;"
        self.setStyleSheet("color: " + color)

    def update1(self):
        lists = DataBase.get('excel lists folders', '') + '/'
        text = self.text()
        if not text: return
        xlsm_path = f'{lists}{text}.xlsm' # 1. составляю имя файла
        
        if not os.path.isfile(xlsm_path):
            color = "#FF1111;"
            try: # 2. если номер меньше минимального номера, то добавляю к нему префикс проекта
                if float(text) < float(DataBase.get('base number', '')):
                    n = float(DataBase.get('base number', '')) + float(text)
                    print('text before:', text)
                    text = f'{n}'.rstrip('0').rstrip('.')
                    print('text after:', text)
                    self.setText(text)
                    xlsm_path = f'{lists}{text}.xlsm'
                    if os.path.isfile(xlsm_path): color = "#00FF00;"
            except ValueError:
                pass
        else:
            color = "#00FF00;"

        k = 1
        # text = re.split(r'\.', text)[0]
        while (os.path.isfile(xlsm_path)):
            # 3. проверяю, есть ли СЛ с большими номерами
            k += 1
            xlsm_path = f'{lists}{text}.{k}.xlsm'
            print('os.path.isfile(xlsm_path)', os.path.isfile(xlsm_path), k)
            xlsm_prev_path = f'{lists}{text}.{k - 1}.xlsm'
        if k > 1 and os.path.isfile(xlsm_prev_path): 
            self.setText(text + f'.{k - 1}')
            color = "#00FF00;"
        self.setStyleSheet("color: " + color)
        # else: 
            # self.__logger.warning(f'Не сумел отыскать {xlsm_path}!')

    def clear1(self):
        self.name_line_edit.clear()
        # self.name_line_edit.setText('')

    def setText(self, text):
        """Select and then insert text. Ctrl+Z works"""
        if text:
            self.name_line_edit.selectAll()
            self.name_line_edit.insert(text)
        # self.name_line_edit.setText(text)

    def text(self):
        return self.name_line_edit.text()

    def data(self, n):
        return self.name_line_edit.text()

    @QtCore.pyqtSlot()
    def open_excel_file(self, filename: str): # проверить, будет ли в одном окне открываться
        """Open xlsm file."""
        print('start excel file') #  + '.xlsm' 2540
        self.__logger.debug('start excel file') #  + '.xlsm' 2540
        if not os.path.isfile(filename):
            self.__logger.warning(f'Не сумел отыскать файл {filename}')
            return
        import win32com.client as win32  # --- !!! ---
        try:
            excel_com_object = win32.DispatchEx('Excel.Application')
            excel_com_object.Visible = True
            excel_com_object.Workbooks.Open(filename) #.Save() # позволяет не сохранять перед выходом, но меняется дата обновления файла
        except Exception as e:
            self.__logger.warning(f"Ошибка при открытии файла: {e}")
        # excel_com_object.Interactive = True
        # excel_com_object.DisplayAlerts = True
        # self.excel_com_object.Quit  # !
        # del self.excel_com_object

# ------------------------------------------------------------------------

class TableGroupbox(QtWidgets.QGroupBox): # plots
    _signal = QtCore.pyqtSignal()
    def __init__(self, settings=None, n=16, *args, **kwds):
        QtWidgets.QGroupBox.__init__(self, *args, **kwds)
        self.__logger = DataBase.get('Logger', None)  # !!!
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(3, 5, 3, 3)
        self.setLayout(layout)      
        # ---
        SETTINGS_NAME = 'config.ini' #self.get_settings_from_sysargv(
        self.settings = QtCore.QSettings(
            get_res_path(f'settings/{SETTINGS_NAME}.ini'), # пусть среди args может быть имя ini файла
            QtCore.QSettings.Format.IniFormat)
        self.settings.setIniCodec("UTF-8")
        self.sensors_num_groupbox = QtWidgets.QGroupBox('N КП') 
        sensors_num_layout = QtWidgets.QHBoxLayout(self.sensors_num_groupbox)
        sensors_num_layout.setContentsMargins(5, 5, 5, 5)
        self.sensors_num = CustomComboBox(
            settings=self.settings,
            name=f"N_kp",
            default_items_list=['6', '12', '16'])
        n = int(self.sensors_num.currentText())
        sensors_num_layout.addWidget(self.sensors_num)
        layout.addWidget(self.sensors_num_groupbox, 0, 0, 1, 2)
        self.sensors_num.currentIndexChanged.connect(
            lambda: self.table_widget.set_size(int(self.sensors_num.currentText())))
        # ---
        self.table_widget = SensorsTableWidget(n)
        # self.table_widget.setTabKeyNavigation(False)
        # layout.addWidget(self.table_widget)
        layout.addWidget(self.table_widget, 1, 0, 4, 4)
        # ---
        self.to_clipboard_btn = CustomButton('Имя в буфер')
        self.to_clipboard_btn.setToolTip('Ctrl+C')
        QtWidgets.QShortcut(
            QtGui.QKeySequence(f"Ctrl+C"), self,
            context=QtCore.Qt.ShortcutContext.ApplicationShortcut,
            member=lambda: self.to_clipboard_btn.animateClick(100))
        layout.addWidget(self.to_clipboard_btn, 6, 0, 1, 2)
        self.to_clipboard_btn.clicked.connect(
            lambda: self.table_widget.make_folder_name(to_clipboard=True))
        # ---
        self.from_clipboard_btn = CustomButton('Вставить из буфера')
        self.from_clipboard_btn.setToolTip('Ctrl+V')
        QtWidgets.QShortcut(
            QtGui.QKeySequence(f"Ctrl+V"), self,
            context=QtCore.Qt.ShortcutContext.ApplicationShortcut,
            member=lambda: self.from_clipboard_btn.animateClick(100))
        layout.addWidget(self.from_clipboard_btn, 6, 2, 1, 2)
        self.from_clipboard_btn.clicked.connect(
            self.table_widget.fill_table)
            # lambda: self.table_widget.fill_table(
                # ))
        # ---
        self.open_xlsm_btn = CustomButton('Открыть СЛ')
        self.open_xlsm_btn.setToolTip('Ctrl+O')
        QtWidgets.QShortcut(
            QtGui.QKeySequence(f"Ctrl+O"), self,
            context=QtCore.Qt.ShortcutContext.ApplicationShortcut,
            member=self.table_widget.open_in_excel)
        layout.addWidget(self.open_xlsm_btn, 7, 0, 1, 2)
        self.open_xlsm_btn.clicked.connect(self.table_widget.open_in_excel)
        # ---
        self.update_names_btn = CustomButton('Обновить КП')
        self.update_names_btn.setToolTip('Ctrl+U')
        layout.addWidget(self.update_names_btn, 7, 2, 1, 2)
        self.update_names_btn.clicked.connect(self.table_widget.update_cells)
        QtWidgets.QShortcut(
            QtGui.QKeySequence(f"Ctrl+U"), self,
            context=QtCore.Qt.ShortcutContext.ApplicationShortcut,
            member=self.table_widget.update_cells)
        # ---
        self.clear_cells_btn = CustomButton('Очистить')
        layout.addWidget(self.clear_cells_btn, 8, 0, 1, 2)
        self.clear_cells_btn.clicked.connect(self.table_widget.clear_cells)
        # ---
        self.set_names_btn = CustomButton('Установить имена')
        layout.addWidget(self.set_names_btn, 8, 2, 1, 2)
        self.set_names_btn.clicked.connect(self.table_widget.set_names)
        # ---
        self.selection_clear_btn = CustomButton('Сбросить выделение')
        layout.addWidget(self.selection_clear_btn, 9, 2, 1, 2)
        self.selection_clear_btn.clicked.connect(lambda: self.table_widget.clearSelection())
        # --- ---
        # self.useless_so_far_bnt = CustomButton('Выделенные имена показать')
        # layout.addWidget(self.useless_so_far_bnt, 8, 0, 1, 2)
        # self.useless_so_far_bnt.clicked.connect(self.table_widget.get_items)
        # ---
        if settings: self.restore_settings(settings)

    def keyPressEvent(self, event):
        print('event.key():', event.key())
        if event.key() == QtCore.Qt.Key.Key_Escape:
            print('Key_Escape')
            self.table_widget.clearSelection()
            # self.clearFocus()
            # self.setFocus()
        if event.key() == QtCore.Qt.Key.Key_Left:
            print('Key_Left')
        if event.key() == QtCore.Qt.Key.Key_Right:
            print('Key_Right')
        if event.key() == QtCore.Qt.Key.Key_Delete:
            print('Key_Delete')
        if event.key() == QtCore.Qt.Key.Key_Return:
            print('Key_Return')
        if event.key() == QtCore.Qt.Key.Key_Down:
            print('Key_Down')
        elif event.key() == QtCore.Qt.Key.Key_Up:
            print('Key_Up')
        return super().keyPressEvent(event)

    def get_current_setting(self):
        """dict name: 'table'"""
        print(self.table_widget.make_folder_name(to_clipboard=False))
        dict = {
            'sensors': self.table_widget.make_folder_name(to_clipboard=False)
            }
        common_dict = DataBase.get('__dict_with_app_settings')
        common_dict['table'] = dict
        print(dict)
        DataBase.setParams(__dict_with_app_settings=common_dict)

    def restore_settings(self, dict: dict):
        """dict name: 'table'"""
        if res := dict.get('sensors', None):
            self.table_widget.fill_table(text=res)
            # self.update()

# -------------------------------------------------------------------------------------------------
class SensorsTableWidget(QtWidgets.QTableWidget):
    def __init__(self, n=16, parent=None, **args):
        super(SensorsTableWidget, self).__init__(parent, **args)
        self.__logger = DataBase.get('Logger', None)  # !!!
        self.n = n
        self.set_size(self.n)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setTabKeyNavigation(True)
        self.horizontalHeader().hide() # скрываю, но с ними удобнее выделять строки/столбцы
        self.verticalHeader().hide()

        # print('\n\n\n\n', self.getContentsMargins())
        # self.setCellWidget(0, 0, button)
        # self.setContentsMargins(0,0,0,0)
        # self.setContentsMargins(20,10,20,10)
        # self.setViewportMargins(50,50,50,50)
        # self.setAutoScrollMargin(55)
        self.itemSelectionChanged.connect(self.selection_changed)
        self.setAcceptDrops(True)

    @QtCore.pyqtSlot()
    def selection_changed(self):
        if self.selectedIndexes():
            self.item(
                self.selectedIndexes()[-1].row(),
                # self.selectedIndexes()[-1].column()).name_line_edit.activateWindow()
                self.selectedIndexes()[-1].column()).name_line_edit.setFocus()
                # self.selectedIndexes()[-1].column()).name_line_edit.clearFocus()
        # self.item(0,0).activateWindow()
        print('selection_changed')

    @QtCore.pyqtSlot(QtGui.QDropEvent)
    def dragEnterEvent(self, event: QtGui.QDropEvent):
        # if event.mimeData().hasUrls():
            # action = QtWidgets.QAction('AAAAA', self)
            # action.triggered.connect(lambda: print(213))
            # event.setDropAction(QtCore.Qt.DropAction(action))
        print('event', event.mimeData().hasUrls())
        event.setDropAction(QtCore.Qt.DropAction.CopyAction)
        event.accept()
        # event.acceptProposedAction()

    @QtCore.pyqtSlot(QtGui.QDropEvent)
    def dropEvent(self, event: QtGui.QDropEvent):
        print('dropEvent', event.mimeData().hasUrls())
        # files_to_fft = []
        # if not event.mimeData().hasUrls():
        #     return
        # for url in event.mimeData().urls():
        #     _, ext = os.path.splitext(url.toLocalFile())
        #     if ext != '.txt':
        #         continue
        #     files_to_fft.append(url.toLocalFile())
        # if len(files_to_fft):
        #     self.gyro_fft_results_groupbox.get_filename_signal.emit(files_to_fft)

    def set_names(self):
        text = self.make_folder_name(to_clipboard=False)
        text = DataBase.sensors_from_str(text)
        before = len(text)
        text = DataBase.validate_sensors(text)
        after = len(text)
        if before > after:
            self.__logger.info(f'Не для всех датчиков нашел СЛ!')
            # можно здесь в принципе выходить из функцииы
        DataBase.setParams(sensors=text)
        print('sensors', text)
        self.__logger.info(f'Установил: {text}')

    def set_size(self, n):
        print('n new =', n, 'n old =', self.rowCount() * self.columnCount())
        current_n = self.rowCount() * self.columnCount()
        if n == current_n:
            return False
        self.n = n
        if n > 3:
            k = n - 1
            kl = [1]
            while (k > 1):
                if n % k == 0: kl.append(k)
                k -= 1
            min = 65000
            min_r = kl[0]
            root = n**0.5
            for k in kl:
                va = abs(root - k)
                if va < min:
                    min = va
                    min_r = k
            print(kl, min_r, root)
        else:
            min_r = n
        text = self.make_folder_name(to_clipboard=False)
        self.setColumnCount(int(min_r))
        self.setRowCount(int(n / min_r))
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                item = self.item(row, column)
                self.setCellWidget(
                    row, column, TableItem(n=row * self.columnCount() + column))
        self.fill_table(text)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch)

    def update_cells(self):
        # find last excel files
        print('update!')
        for item in self.get_items():
            item.update1()

    def item(self, row, col) -> TableItem:
        return self.cellWidget(row, col)

    def clear_cells(self):
        print('clear!')
        for item in self.get_items():
            item.clear1()

    def open_in_excel(self): # надо убедиться, что листы именно вкладками открываются
        print('open_in_excel!')
        # path = DataBase.get('excel lists folders', '')
        for item in self.get_items():
            # xlsm_path = f'{path}/{item.text()}.xlsm'
            # item.open_excel_file(xlsm_path)
            item.open_excel_file(item.path)

    def get_items(self) -> list[TableItem]:
        """Get selected items. If no selection, get all items"""
        # print(self.selectedIndexes())
        res1 = []
        if self.selectedIndexes():
            for ind in self.selectedIndexes():
                if self.item(ind.row(), ind.column()) is not None:
                    res1.append(self.item(ind.row(), ind.column()))
        else:
            for row in range(self.rowCount()):
                for column in range(self.columnCount()):
                    if self.item(row, column) is not None:
                        res1.append(self.item(row, column))
        print('valid sensors:', res1)
        return res1

    def make_folder_name(self, to_clipboard=True):
        # """."""
        print('\n\nmake_folder_name', to_clipboard, '\n\n')
        import time
        # current GMT Time
        gmt_time = time.gmtime(time.time())
        date = f'{gmt_time.tm_year}-{gmt_time.tm_mon}-{gmt_time.tm_mday}_'
        sensors = []
        # sensors_to_search = []
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                item: TableItem = self.item(row, column)
                if row * self.columnCount() + column > self.n:
                    print(f"break, row={row}, col={column}")
                    break
                if item is not None:
                    text = item.text()
                    if text is None or len(text) <= 2:
                        text = 'x'
                else:
                    text = 'x'
                sensors.append(text)
                # sensors_to_search.append(re.split(r'\.', text)[0])
        name = date + '_'.join(sensors)
        print(name)
        if to_clipboard:
            QtWidgets.QApplication.clipboard().setText(name)
        pattern = '_'.join(sensors)
        # pattern = '_'.join(sensors_to_search)
        DataBase.setParams(search_pattern=pattern) ##################################################
        self.__logger.info(f'search_pattern {pattern}')
        self.__logger.info(f'Отправил {name} в буфер обмена')
        return name
        # import datetime
        # current_time = datetime.datetime.now()

    def fill_table(self, text=None): #, text):
        """."""
        if text is None or not text:
            text = QtWidgets.QApplication.clipboard().text()
        self.__logger.info(f'Получил имя {text}')
        print('\tfill_table', text)
        list_text = DataBase.sensors_from_str(text)
        i = 0
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                item = TableItem(n=row * self.columnCount() + column)
                self.setCellWidget(row, column, item)
                try:
                    if len(list_text[i]) >= 3: # and len(re.split(r"\b", list_text[i])) == 3:
                        item.setText(list_text[i])
                    else:
                        item.setText('')
                    i += 1
                except IndexError:
                    item.setText('')
        print('text ', list_text)


    def forward(self):
        print('forward!')

    def prev(self):
        print('prev!')
    


