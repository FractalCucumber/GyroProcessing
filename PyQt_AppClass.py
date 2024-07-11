# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g
from time import sleep, perf_counter
t0 = perf_counter()
import sys
import os
import re
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from widgets.PyQt_Logger import QTextEditLogger

from widgets.PyQt_CustomComboBox import CustomComboBox
from widgets.PyQt_CustomPushButton import CustomButton
# from PyQt_Thread import SecondThread
from PyQt_Functions import get_res_path  #, natural_keys
from PyQt_SensorsTable import TableGroupbox
# from win32api import ShellExecute
from widgets.PyQt_ProjectsComboBox import ProjectsComboBox
from QtPlotsMakerGroupbox import PlotsMakerGroupbox # import pg here, 0.16 sec
from QtHeaderFilesMakerGroupbox import HeaderFilesMakerGroupbox # import pandas here, 0.4 sec
from ScaleFactorsCalculatorGroupbox import ScaleFactorsCalculatorGroupbox
from CheckResultsProcessingGroupbox import CheckResultsProcessingGroupbox
from CustomQTextEdit import CustomQTextEdit


import DataBase
print(perf_counter() - t0)


# description:
# __Author__ = """By: _
# Email: _"""
# __Copyright__ = 'Copyright (c) 2024 _'
# __Version__ = 1.0


# python -m pip install memory-profiler  # так устанавливается 
# C:\Users\zinkevichav\AppData\Roaming\Code\User\settings.json - настройки проверки орфографии
# d:/GyroVibroTest/venv3.6/Scripts/Activate.bat                
# pyinstaller PyQt_ApplicationOnefolder.spec
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# from memory_profiler import profile
# from pympler import asizeof
# print(asizeof.asizeof(self.MAX_WIDTH_FIRST_COL))

# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------

class ProjectGroupBox(QtWidgets.QGroupBox): # info about project
    _signal = QtCore.pyqtSignal()
    def __init__(self, *args, **kwds):
    # def __init__(self, read_csv=None, logger=None, log_flag=False, gyro_num=3, *args, **kwds):
        QtWidgets.QGroupBox.__init__(self, *args, **kwds)
        self.__logger = DataBase.get('Logger', None)  # !!!
        self.start_folder = "."  # !

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(3, 5, 3, 3)
        self.setLayout(layout)
        # ---
        self.projects_combo_box = ProjectsComboBox(self)
        layout.addWidget(self.projects_combo_box, 0, 0)
        # ---
        self.path_te = CustomQTextEdit(
            'projects/СЛ/...', objectName="with_border", maximumHeight=80)
        layout.addWidget(self.path_te, 1, 0)
        # ---
        self.open_button = CustomButton('Открыть папку')
        layout.addWidget(self.open_button, 2, 0)
        # ---
        self.on_fly_checkbox = QtWidgets.QCheckBox("Get path on fly")
        layout.addWidget(self.on_fly_checkbox, 3, 0)
        self.show_all_checkbox = QtWidgets.QCheckBox("Показывать все проекты")
        layout.addWidget(self.show_all_checkbox, 4, 0)

        # ------    ----------------------------------------------------------
        self.unable_settings_change = QtWidgets.QCheckBox('режим Бога') 
        layout.addWidget(self.unable_settings_change, 5, 0)
# ------  ---------------------------------------------------------------
# ------  ---------------------------------------------------------------
# ------  ---------------------------------------------------------------
# ------  ---------------------------------------------------------------


class AppWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, args=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.args = args
        # SETTINGS_NAME = 'config.json' #self.get_settings_from_sysargv(
        # SETTINGS_NAME = 'config.ini' #self.get_settings_from_sysargv(
            # 'settings', 'config.ini', str)
        # SETTINGS_NAME, _ = os.path.splitext(SETTINGS_NAME)
        PATH_TO_PROJECTS = os.getcwd() + '/projects/'
        DataBase.setParams(__path_to_projects=PATH_TO_PROJECTS)  # !!!
        __path_to_save_app_settings = os.getcwd() + '/settings/config.json'
        DataBase.setParams(__path_to_save_app_settings=__path_to_save_app_settings)  # !!!
        # DataBase.setParams(calamine_xlsm_reader=)  # !!!
        FILE_LOG_FLAG = True #self.get_settings_or_sysargv("FILE_LOG_FLAG", True)
# ------ Logger ---------------------------------------------------------------
        self.log_text_box = QTextEditLogger(file_log=FILE_LOG_FLAG)
            # self, file_log=FILE_LOG_FLAG, debug_enable=DEBUG_ENABLE_FLAG)
        self.logger = self.log_text_box.getLogger()
        self.logger.debug("Начало загрузки")
        DataBase.setParams(Logger=self.logger)  # !!!
        print(DataBase.get('Logger'))  # !!!
# ------ vars ---------------------------------------------------------------
        LOGGER_NAME = 'main'
        # __path = '\\\\fs\\Public\\Зинкевич Алексей Васильевич\\GyroVibroTest\\Руководство оператора GyroVibroTest.docx' # !!!
        # self.MAIN_PATH_TO_MANUAL = self.get_settings(
        #     'PATH_TO_MANUAL', __path)
        # self.PATH_TO_MANUAL = 'settings\\Руководство оператора GyroVibroTest.docx' # !!!
        # STYLE_SHEETS_FILENAME = get_res_path('res\StyleSheets.css')
        STYLE_SHEETS_FILENAME = 'res\\StyleSheets.css'
# ------ GUI ------------------------------------------------------------------
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.ApplicationAttribute.
            AA_UseStyleSheetPropagationInWidgetStyles,
            True)  # наследование свойств оформления потомков от родителей
        self.main_grid_layout = self.set_visual_style(STYLE_SHEETS_FILENAME)
# ------ Load settings ---------------------------------------------------------------------
        # self.load_previous_settings(self.settings)
        __path_to_save_app_settings = DataBase.get('__path_to_save_app_settings')
        import json
        try:
            with open(__path_to_save_app_settings, 'r', encoding='utf-8') as file:
                settings: dict = json.load(file)
        except FileNotFoundError:
            self.logger.warning('Файл с настройками не обнаружен!')
        self.apply_settings_dict(settings)
# ------  --------------------------------------------------------
        self.gyro_project_groupbox = ProjectGroupBox(title='Проект')
# ------    ----------------------------------------------------------
        self.check_num_groupbox = QtWidgets.QGroupBox(title='Проверки (N темератур)') 
        check_num_groupbox_layout = QtWidgets.QHBoxLayout(self.check_num_groupbox)
        check_num_groupbox_layout.setContentsMargins(5, 5, 5, 5)
        self.check_num_spinbox = QtWidgets.QSpinBox(
            minimum=1, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        check_num_groupbox_layout.addWidget(self.check_num_spinbox)

# ------    ----------------------------------------------------------
        self.settings_temps_le = QtWidgets.QLineEdit('') 
        check_num_groupbox_layout.addWidget(self.settings_temps_le)
        self.check_temps_le = QtWidgets.QLineEdit('') 
        check_num_groupbox_layout.addWidget(self.check_temps_le)
# ------  -----------------------------------------------------------------
        self.table_groupbox = TableGroupbox(
            title='КП', minimumWidth=300, minimumHeight=200,
            settings=settings.get('table', {}))
        # Logs
        self.logs_groupbox = QtWidgets.QGroupBox(
            'Лог', minimumHeight=160)  # Logs
        logs_groupbox_layout = QtWidgets.QVBoxLayout(self.logs_groupbox)
        logs_groupbox_layout.setContentsMargins(3, 5, 3, 3)
        logs_groupbox_layout.addWidget(self.log_text_box)
        self.logs_clear_button = CustomButton(
            'Очистить', clicked=lambda: self.log_text_box.clear())  # Clear logs
        logs_groupbox_layout.addWidget(self.logs_clear_button)

# ------   ---------------------------------------------------------------------
        self.header_maker_groupbox = HeaderFilesMakerGroupbox(
            title='Собрать h-файлы', settings=settings.get('header maker', {}))
        self.header_maker_groupbox.progress_signal.connect(
            self.pr_bar_event
        )
# ------   ---------------------------------------------------------------------
        self.scale_factors_groupbox = ScaleFactorsCalculatorGroupbox(
            title='Масштабники', settings=settings.get('scale calculation', {})) 
        self.scale_factors_groupbox.progress_signal.connect(
            self.pr_bar_event
        )
# ------   ---------------------------------------------------------------------
        self.result_process_groupbox = CheckResultsProcessingGroupbox(
            title='Обработать проверки', settings=settings.get('check processing', {}))
# ------   ---------------------------------------------------------------------
        self.plots_groupbox = PlotsMakerGroupbox(
            title='Графики', settings=settings.get('plot settings', {})) 
# ------   ---------------------------------------------------------------------
        self.pr_bar = QtWidgets.QProgressBar(
            format='%v/%m Ожидаю веления', maximum=1, value=0) #, visible=False)
# ------ Signal Connect --------------------------------------------------------------------
        self.gyro_project_groupbox.projects_combo_box.currentIndexChanged.connect(
            self.project_change_event)
        self.gyro_project_groupbox.show_all_checkbox.stateChanged.connect(
            self.load_projects # по возможности нужно не менять выбранный проект
            # lambda: self.load_projects(self.settings) # по возможности нужно не менять выбранный проект
        )
        self.gyro_project_groupbox.unable_settings_change.stateChanged.connect(
            self.unlock
        )
# ------ --------------------------------------------------------
        self.load_projects()
# ------ Add menu --------------------------------------------------------
        self.fill_menu()
# ------  --------------------------------------------------------
        main_frame = QtWidgets.QScrollArea(minimumWidth=300)  # удобный виджет
        main_frame_layout = QtWidgets.QGridLayout()
        scroll_widget = QtWidgets.QWidget()
        main_frame.setWidget(scroll_widget)
        scroll_widget.setLayout(main_frame_layout)

        main_frame.setWidgetResizable(True)
#         # ---
#         gyro_info_frame_layout.setContentsMargins(3, 0, 3, 3)
#         self.gyro_info_groupbox_list: list[GyroInfoGroupBox] = []
#         # for i in range(self.GYRO_NUMBER):
#         #     self.gyro_info_groupbox_list.append(GyroInfoGroupBox(
#         #         k_spacing=self.GYRO_NUMBER, ind=i,
#         #         logger=self.logger, flag_getter=self.processing_thr.isRunning,
#         #         file_processing_handler=self.run_thread_for_file_processing,
#         #         max_width_first_col=self.MAX_WIDTH_FIRST_COL / 1.7))
        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setColumnCount(1)
        self.tree.header().hide()
        # self.tree.setHeaderLabels(['Key'])
        # self.tree.setMaximumWidth(500)
        # self.tree.setColumnWidth(0, 500)
        # item = QtWidgets.QTreeWidgetItem(self.tree)
        # # self.tree.addTopLevelItem(root)
        # item.setText(0, 'Root item')
        item = self.tree
        
        # item222 = QtWidgets.QTreeWidgetItem(item)
        # self.tree.setItemWidget(item222, 0, CustomButton('собрать h-файлы'))

        headers_child = QtWidgets.QTreeWidgetItem(item)
        headers_child.setText(0,'настройки h-файлов')
        headers_child.setText(1,'ios')

        # item2221 = QtWidgets.QTreeWidgetItem(item)
        # self.tree.setItemWidget(item2221, 0, CustomButton('обработать масштабники'))
        # child1.setCheckState(0, QtCore.Qt.CheckState.Checked)
        # item.addChild(child1)
        scale_fastors_child = QtWidgets.QTreeWidgetItem(item)
        scale_fastors_child.setText(0,'масштабники')
        scale_fastors_child.setText(1,'')

        # item2222 = QtWidgets.QTreeWidgetItem(item)
        # self.tree.setItemWidget(item2222, 0, CustomButton('обработать проверки'))
        child3 = QtWidgets.QTreeWidgetItem(item)
        child3.setText(0,'проверки')
        child3.setText(1,'')
        child23 = QtWidgets.QTreeWidgetItem(scale_fastors_child)
        child23.setText(0,'child3')
        child23.setText(1,'android')
        # # Загрузить все свойства и элементы управления корневого узла
        # #TODO Optimization 3 Добавить события ответа к узлам
        # # self.tree.clicked.connect(self.onClicked)
        # #Node Развернуть все
        # child4 = QtWidgets.QTreeWidgetItem(item)
        # child4.setText(0,'child22')
        # item.addChild(child4)
        child24 = QtWidgets.QTreeWidgetItem(headers_child)
        # child24.setText(0,'child2222')
        self.tree.setItemWidget(child24, 0, self.header_maker_groupbox)

        child34 = QtWidgets.QTreeWidgetItem(scale_fastors_child)
        # child34.setText(0,'child3333')
        self.tree.setItemWidget(child34, 0, self.scale_factors_groupbox)

        child44 = QtWidgets.QTreeWidgetItem(child3)
        self.tree.setItemWidget(child44, 0, self.result_process_groupbox)



        self.tree.expandAll()
        main_frame_layout.addWidget(self.tree, 0, 0, 1, 1)
# ------ Set main grid --------------------------------------------------------
        self._groupbox = QtWidgets.QGroupBox() #, minimumHeight=120, maximumWidth=460)  # Logs
        _groupbox_layout = QtWidgets.QVBoxLayout(self._groupbox)
        _groupbox_layout.addWidget(self.gyro_project_groupbox)
        _groupbox_layout.addWidget(self.check_num_groupbox)
        # _groupbox_layout.addWidget(self.plots_groupbox)
        _groupbox_layout.addWidget(self.table_groupbox)
        _groupbox_layout.addWidget(self.logs_groupbox)

        self._groupbox2 = QtWidgets.QGroupBox() #, minimumHeight=120, maximumWidth=460)  # Logs
        _groupbox_layout2 = QtWidgets.QVBoxLayout(self._groupbox2)
        _groupbox_layout2.addWidget(main_frame)
        _groupbox_layout2.addWidget(self.pr_bar)

        self.h_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, parent=self)
        self.h_splitter.setChildrenCollapsible(False)
        self.h_splitter.addWidget(self._groupbox)
        self.h_splitter.addWidget(self._groupbox2)
        self.h_splitter.addWidget(self.plots_groupbox)

        if settings.get('h_splitter sizes', {}) and settings.get('h_splitter orientation', {}):
            self.h_splitter.setSizes(settings['h_splitter sizes'])
            self.h_splitter.setOrientation(settings['h_splitter orientation'])
        self.main_grid_layout.addWidget(self.h_splitter, 0,0,100,100)
        # self.main_grid_layout.addWidget(self.plots_groupbox,
        #                                 3, 0, 1, 1)
        # self.main_grid_layout.addWidget(self.check_num_groupbox,
        #                                 2, 0, 1, 1)
        # self.main_grid_layout.addWidget(self.gyro_project_groupbox,
        #                                 0, 0, 2, 1)
        # self.main_grid_layout.addWidget(self.result_process_groupbox,
        #                                 4, 0, 3, 1)
        
        # self.main_grid_layout.addWidget(self.scale_factors_groupbox,
        #                                 0, 1, 3, 1)
        # self.main_grid_layout.addWidget(self.header_maker_groupbox,
        #                                 3, 1, 4, 1)
        # self.main_grid_layout.addWidget(v_splitter,
        #                                 1, 2, 18, 1)
        # self.main_grid_layout.addWidget(self.table_groupbox,
        #                                 4, 0, 4, 1)
        # self.main_grid_layout.addWidget(self.logs_groupbox,
        #                                 8, 0, 4, 1)
        # self.main_grid_layout.addWidget(self.pr_bar,
        #                                 11, 3, 1, 1)
        # self.main_grid_layout.addWidget(main_frame,
        #                                 0, 3, 10, 10)
# ------  ----------------------------------------------------------------
        self.animation()
        self.show()
        self.logger.debug("start import pandas in thread")
        # self.processing_thr.start()  # post init! (import pandas)
        self.logger.info("Программа запущена")
# ------  ---------------------------------------------------------------------
        # folder = QtWidgets.QFileDialog.getExistingDirectory(
        #     self, "Выбрать папку", self.folder_name)
        # if folder:
        #     self.save_res_fld_label.selectAll()
        #     self.save_res_fld_label.insertPlainText(folder)
        from scipy.signal import savgol_filter ###################################################

    def unlock(self):
        # разрешить менять таблицы, число температур и пути
        self.header_maker_groupbox.unlock() 
        self.scale_factors_groupbox.unlock()
        self.result_process_groupbox.unlock()

    def fill_menu(self):
        """Create application menu bar."""
        menu_bar = self.menuBar()
        settings_menu = menu_bar.addMenu("Настройки")
        self.settings_autosave_action = self.add_action(
            menu=settings_menu,
            text="Автосохранение настроек", checkable=True)
        self.settings_autosave_action.setChecked(True)

    @staticmethod
    def add_action(menu: QtWidgets.QMenu, text: str,
                   action_fun=None, shortcut=None, **opts):
        action = QtWidgets.QAction(
            text=text, parent=menu, **opts)#, opts)  # Measure
        if shortcut:
            if type(shortcut) != list:
                shortcut = [shortcut]
            action.setShortcuts(shortcut)
            action.setShortcutVisibleInContextMenu(True)
        if action_fun:
            action.triggered.connect(action_fun)
        menu.addAction(action)
        return action

    def apply_settings_dict(self, settings: dict):
        # self.result_process_groupbox.restore_settings(
        #     settings.get('check processing', {}), default={})
        # self.header_maker_groupbox.restore_settings(
        #     settings.get('header maker', {}))
        # self.scale_factors_groupbox.restore_settings(
        #     settings.get('scale calculation', {}))
        # self.table_groupbox.restore_settings(
        #     settings.get('table', {}))
        # self.table_groupbox.table_widget.set_size(
        #     int(self.sensors_num.currentText())
        #     )
        if settings.get('window_pos', {}):
            self.move(QtCore.QPoint(*settings.get('window_pos', {})))
        if settings.get('window_size', {}):
            self.resize(QtCore.QSize(*settings.get('window_size', {})))

    def save_settings(self, settings_path, settings_dict):
        import json
        with open(settings_path, 'w', encoding='utf-8') as file:
            json.dump(
                settings_dict, file, ensure_ascii=False, indent=4)

    def load_projects(self):
        print('load_settings')
        # __path_to_save_app_settings = DataBase.get('__path_to_save_app_settings')
        # self.load_settings_dict(__path_to_save_app_settings)

        prj_cb = self.gyro_project_groupbox.projects_combo_box
        prev_text = prj_cb.currentText()
        prj_cb.clear()
        import json
        res = DataBase.get('__path_to_projects', None)
        if not os.path.isdir(res):
            self.logger.error(f'Не могу отыскать путь к проектам (вы ввели: {res})')
        for path in os.scandir(res):
            # print(path, path.name)
            if path.is_file() and os.path.splitext(path.name)[1] == '.json':
                with open(path, 'r', encoding='utf-8') as file:
                    prj_dict: dict = json.load(file) # need error handler?
                if prj_dict.get("visible in app", False) or self.gyro_project_groupbox.show_all_checkbox.isChecked():
                    prj_cb.addItem(os.path.basename(os.path.splitext(path.name)[0]))
                # print(prj_dict)

        if prev_text and prj_cb.findText(prev_text) > 0:
            prj_cb.setCurrentIndex(prj_cb.findText(prev_text))
        else:
            prj_cb.setCurrentIndex(
                0  # load from settings!
            )
            self.project_change_event()

    def project_change_event(self):
        print('project_change_event')
        prj_cb = self.gyro_project_groupbox.projects_combo_box
        prj_path = DataBase.get('__path_to_projects', '') + prj_cb.currentText() + '.json'
        print('prj_path ', prj_path)
        import json
        try:
            with open(prj_path, 'r', encoding='utf-8') as file:
                prj_dict: dict = json.load(file)
                # self.logger.debug(self.fft_opt)
        except FileNotFoundError:
            self.logger.debug('FileNotFoundError')
            print('FileNotFoundError!')
            return
        # self.project: dict = prj_dict
        prj_dict['name'] = prj_cb.currentText()
        DataBase.setParams(**prj_dict)  # !!!

        self.header_maker_groupbox.path_te.setTextCarefully(
            ';'.join(prj_dict.get("h-files folders", ['']))
            ) # возможно, лучше несколько виджетов создавать, по одному на каждый путь
        # ---
        self.scale_factors_groupbox.path_te.setTextCarefully(
            prj_dict.get("settings results folder", ""))
        # ---
        self.result_process_groupbox.path_te.setTextCarefully(
            prj_dict.get("check results folder", ""))
        # ---
        self.gyro_project_groupbox.path_te.setTextCarefully(
            prj_dict.get("excel lists folders", ""))
        # ---
        self.table_groupbox.path_to_books = prj_dict.get(
            "excel lists folders", "") # или getter сделать
        # ---
        self.settings_temps_le.setText(
            ' '.join(prj_dict.get("settings temperatures", "")))
        self.check_temps_le.setText(
            ' '.join(prj_dict.get("check temperatures", "")))
        # "visible in app": True,
        # "h-files template": "D:/GyroResultsProcessing/h-files templates23/DeviceXXXX.h",
        # "h-files folders": ["D:/GyroResultsProcessing/h-files"],
        # "excel lists folders": "D:/GyroResultsProcessing",
        # "settings_results_folder": "D:/GyroResultsProcessing/настройки",
        # "check_results_folder": "D:/GyroResultsProcessing/проверки",
        # "settings_temperatures": [-50, 23, 60],
        # "check_temperatures": [-50, 23, 50]
        self.table_groupbox.table_widget.update_cells()

    # @QtCore.pyqtSlot(dict)
    # def pr_bar_event(self, info: dict):
    def pr_bar_event(self, **info):
        print('\t\tprogress info:', info)
        if info.get('visible'):
            self.pr_bar.setVisible(info.get('visible'))
        if info.get('value'):
            self.pr_bar.setValue(info.get('value'))
        elif info.get('maximum'):
            self.pr_bar.setMaximum(info.get('maximum'))
        elif info.get('format'):
            self.pr_bar.setFormat(info.get('format'))  # '%v/%m сек (определение смещения)')
        elif info.get('text'):
            self.pr_bar.setFormat('%v/%m ' + info.get('text'))  # '%v/%m сек (определение смещения)')

    def animation(self):
        effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self.anim = QtCore.QPropertyAnimation(effect, b"opacity")
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1)
        self.anim.setDuration(10)
        self.anim.start()

    def set_visual_style(self, filename, spacing=2, style='Fusion'):
        self.setWindowTitle(f"ResultProcessing") # в названии номер стенда писать
        QtWidgets.QApplication.setStyle(style)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(widget, spacing=spacing)
        self.logger.debug(f"os info: {sys.getwindowsversion()}")
        layout.setContentsMargins(10, 0, 10, 10)
        self.setCentralWidget(widget)
        # ------ Style ----------------------------------------------------
        try:
            with open(filename, "r") as style_sheets_css_file:
                self.setStyleSheet(style_sheets_css_file.read())
        except FileNotFoundError:
            self.logger.warning(f'No file {filename}!')
        try:
            self.app_icon_not_busy = QtGui.QIcon()
            self.app_icon_not_busy.addFile(
                get_res_path('res\icon_not_busy.png'))
            self.app_icon_busy = QtGui.QIcon(
                get_res_path('res\icon_busy.png'))
            self.setWindowIcon(self.app_icon_not_busy)
        except FileNotFoundError:
            pass
        return layout

    def closeEvent(self, event):
        self.plots_groupbox.graphWidgetGroupBox.deleteLater()
        self.scale_factors_groupbox.graphWidget.deleteLater()
        self.result_process_groupbox.plot1.deleteLater()
        self.result_process_groupbox.plot2.deleteLater()
        # текущий проект сохранять
        # выбранное число КП сохранять
        if self.settings_autosave_action.isChecked():
            DataBase.setParams(__dict_with_app_settings={})
            self.plots_groupbox.get_current_setting()
            self.result_process_groupbox.get_current_setting()
            self.header_maker_groupbox.get_current_setting()
            self.scale_factors_groupbox.get_current_setting()
            self.table_groupbox.get_current_setting()
            common_dict = DataBase.get('__dict_with_app_settings')
            common_dict['window_pos'] = [self.pos().x(), self.pos().y()]
            common_dict['window_size'] = [self.size().width(), self.size().height()]
            common_dict['h_splitter sizes'] = self.h_splitter.sizes()
            common_dict['h_splitter orientation'] = self.h_splitter.orientation()
            DataBase.setParams(__dict_with_app_settings=common_dict)
            settings_dict = DataBase.get('__dict_with_app_settings', None)
            # settings_dict['N KP'] = self.sensors_num.currentIndex()
            self.table_groupbox.sensors_num.save_all()
            path = DataBase.get('__path_to_save_app_settings', None)
            if settings_dict is None or path is None:
                self.logger.warning('Не сумел запомнить настройки перед отключением!')
                return
            self.save_settings(path, settings_dict)
            self.logger.info('Сохранил настройки')
        else:
            self.logger.info('Выход без сохранения настроек')

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
#
###############################################################################
###############################################################################
#
###############################################################################
###############################################################################
#
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    splash = QtWidgets.QSplashScreen(
        QtGui.QPixmap(get_res_path('res/load_icon.png')))
    splash.show()
    window = AppWindow(args=sys.argv)
    splash.finish(window)
    sys.exit(app.exec())



# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------



# class AppWindow2(QtWidgets.QMainWindow):
#     # @profile
#     def __init__(self, parent=None, args=None):
#         QtWidgets.QMainWindow.__init__(self, parent)
# # ------ Settings -------------------------------------------------------------
#         self.args = args
#         SETTINGS_NAME = self.get_settings_from_sysargv(
#             'settings', 'config.ini', str)
#         # settings=config181.ini GYRO_NUMBER=1
#         # settings=config184.ini GYRO_NUMBER=3
#         SETTINGS_NAME, _ = os.path.splitext(SETTINGS_NAME)
#         self.settings = QtCore.QSettings(
#             get_res_path(f'settings\\{SETTINGS_NAME}.ini'), # пусть среди args может быть имя ini файла
#             QtCore.QSettings.Format.IniFormat)
#         self.settings.setIniCodec("UTF-8")
#         self.GYRO_NUMBER = self.get_settings_or_sysargv("GYRO_NUMBER", 1)
# # ------ Logger ---------------------------------------------------------------
#         FILE_LOG_FLAG = self.get_settings_or_sysargv("FILE_LOG_FLAG", True)
#         self.log_text_box = QTextEditLogger(file_log=FILE_LOG_FLAG)
#             # self, file_log=FILE_LOG_FLAG, debug_enable=DEBUG_ENABLE_FLAG)
#         self.logger = self.log_text_box.getLogger()
#         self.logger.debug("Начало загрузки")
# # ------ Init vars ------------------------------------------------------------
#         self.MAX_WIDTH_FIRST_COL = 192 # 315  # не расширяется
#         self.PAUSE_INTERVAL_MS = self.get_settings(
#             f'{self.GYRO_NUMBER}/PAUSE_INTERVAL_MS', 500)
#         self.READ_INTERVAL_MS = self.get_settings(
#             f'{self.GYRO_NUMBER}/READ_INTERVAL_MS', 75 * 2)
#         AMP_LOG10_FLAG = self.get_settings_or_sysargv('AMP_LOG10_FLAG', False)
#         self.count: int = 0
#         self.progress_value = 0  # убрать?
#         self.current_cycle: int = 0
#         self.check_time = 0
#         self.flag_send = False
#         self.bytes_flag = False
#         self.wait_time = 0
#         # self.blink_flag = 0 # now useless
#         self.time_error = 0 
#         self.__no_data_flag = 0 # флаг, который показывает, идут ли данные с порта или нет

#         LOGGER_NAME = 'main'
#         __path = '\\\\fs\\Public\\Зинкевич Алексей Васильевич\\GyroVibroTest\\Руководство оператора GyroVibroTest.docx'
#         self.MAIN_PATH_TO_MANUAL = self.get_settings(
#             'PATH_TO_MANUAL', __path)
#         self.PATH_TO_MANUAL = 'settings\\Руководство оператора GyroVibroTest.docx'
#         # STYLE_SHEETS_FILENAME = get_res_path('res\StyleSheets.css')
#         STYLE_SHEETS_FILENAME = 'res\\StyleSheets.css'
#         self.FFT_OPTIONS_FILE_NAME = 'settings\\fft_options.json'
#         # self.PROJECT_FILE_NAME = get_res_path('settings/projects.json')  # get_res_path не нужен по идее
#         self.PROJECT_FILE_NAME = 'settings\\projects.json'
#         self.ICON_COLOR_LIST = ['red', 'green', 'blue']

# # ------ GUI ------------------------------------------------------------------
#         QtWidgets.QApplication.setAttribute(
#             QtCore.Qt.ApplicationAttribute.
#             AA_UseStyleSheetPropagationInWidgetStyles,
#             True)  # наследование свойств оформления потомков от родителей
#         self.main_grid_layout = self.set_visual_style(STYLE_SHEETS_FILENAME)
# # ------ Thread ---------------------------------------------------------------

#         self.processing_thr = SecondThread(
#             gyro_number=self.GYRO_NUMBER,
#             read_interval_ms=self.READ_INTERVAL_MS,
#             logger_name=LOGGER_NAME,
#             wait_time_sec=self.get_settings("WAIT_TIME_SEC", 0.5),
#             options_file_name=self.FFT_OPTIONS_FILE_NAME)
#         self.processing_thr.package_num_signal.connect(
#             self.get_and_show_data_from_thread)
#         self.processing_thr.fft_data_signal.connect(self.plot_fft)
#         self.processing_thr.median_data_ready_signal.connect(
#             self.plot_fft_final)
#         self.processing_thr.info_signal.connect(
#             lambda text: self.logger.info(text))
#         self.processing_thr.warning_signal.connect(
#             lambda text: self.logger.warning(text))

#         self.processing_thr.finished.connect(self.after_init_in_thread)

# # ------ Plots in tab widget --------------------------------------------------

#         # грузится 0.5 секунды
#         self.tab_plot_widget = CustomTabWidget(
#             GYRO_NUMBER=self.GYRO_NUMBER,
#             logger_name=LOGGER_NAME, log_flag=AMP_LOG10_FLAG)  # !

# # ------ gyro_fft_results --------------------------------------------------------
#         self.gyro_fft_results_groupbox = GyroResultsGroupBox(  # лучше np для чтения использовать, чтобы не зависеть от pd
#         read_csv=None, logger=self.logger,
#         title='Проект',
#         # gyro_num=self.GYRO_NUMBER,
#         # maximumWidth=180, minimumWidth=120
#         )  # !
#         # self.tab_plot_widget.gyro_fft_results_groupbox.get_filename_signal.connect(
#         self.gyro_fft_results_groupbox.get_filename_signal.connect(
#             self.run_thread_for_file_processing)
#         # self.tab_plot_widget.log_flag
# # ------  fs  ----------------------------------------------------------

#         self.sensors_num_groupbox = QtWidgets.QGroupBox(
#             'N КП') 
#         sensors_num_layout = QtWidgets.QHBoxLayout()
#         sensors_num_layout.setContentsMargins(5, 5, 5, 5)
#         self.sensors_num_groupbox.setLayout(sensors_num_layout)
#         self.sensors_num = CustomComboBox(
#             settings=self.settings,
#             name=f"{self.GYRO_NUMBER}/N_kp",
#             default_items_list=['6', '12', '16'])
#         sensors_num_layout.addWidget(self.sensors_num)
# # ------  cycle num  ----------------------------------------------------------

#         self.check_num_groupbox = QtWidgets.QGroupBox(
#             title='Проверки (N temp)') 
#         check_num_groupbox_layout = QtWidgets.QHBoxLayout()
#         check_num_groupbox_layout.setContentsMargins(5, 5, 5, 5)
#         self.check_num_groupbox.setLayout(check_num_groupbox_layout)

#         self.check_num_spinbox = QtWidgets.QSpinBox(
#             minimum=1, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
#         # cycle_number_groupbox_layout.addWidget(
#             # QtWidgets.QLabel(''), 0, 0, 3, 2)  # Cycle number
#         check_num_groupbox_layout.addWidget(self.check_num_spinbox)
#         self.check_num_spinbox.setToolTip(
#             'Число повторений циклограммы (методики).')
# # ------ Measurement File -----------------------------------------------------
#         """Block with button to open and edit measurement file."""
#         self.measurements_file_groupbox = FileGroupBox(
#             logger=self.logger,
#             title='Методика измерений', minimumWidth=self.MAX_WIDTH_FIRST_COL,
#             maximumHeight=300, file_processing_handler=self.get_data_from_file)
#         # self.measurements_file_groupbox = FileGroupBox(
#         #     logger=self.logger, flag_getter=self.processing_thr.isRunning,
#         #     file_processing_handler=self.get_data_from_file,
#         #     max_width_first_col=self.MAX_WIDTH_FIRST_COL)
# # ------ Saving results -------------------------------------------------------

#         gyro_info_frame = QtWidgets.QScrollArea()  # удобный виджет
#         gyro_info_frame_layout = QtWidgets.QGridLayout()
#         scroll_widget = QtWidgets.QWidget()
#         gyro_info_frame.setWidget(scroll_widget)
#         scroll_widget.setLayout(gyro_info_frame_layout)

#         gyro_info_frame.setWidgetResizable(True)
#         # ---
#         gyro_info_frame_layout.setContentsMargins(3, 0, 3, 3)
#         self.gyro_info_groupbox_list: list[GyroInfoGroupBox] = []
#         # for i in range(self.GYRO_NUMBER):
#         #     self.gyro_info_groupbox_list.append(GyroInfoGroupBox(
#         #         k_spacing=self.GYRO_NUMBER, ind=i,
#         #         logger=self.logger, flag_getter=self.processing_thr.isRunning,
#         #         file_processing_handler=self.run_thread_for_file_processing,
#         #         max_width_first_col=self.MAX_WIDTH_FIRST_COL / 1.7))
#         #     gyro_info_frame_layout.addWidget(
#         #         self.gyro_info_groupbox_list[i], i, 0, 1, 1)

# # ------ Output logs and data from file ---------------------------------------

#         table_groupbox = QtWidgets.QGroupBox(
#             'КП', maximumWidth=750,
#             minimumWidth=150, minimumHeight=175)
#         table_groupbox_layout = QtWidgets.QGridLayout()
#         table_groupbox_layout.setContentsMargins(3, 5, 3, 3)
#         table_groupbox.setLayout(table_groupbox_layout)

#         self.table_widget = SensorsTableWidget()
#         # self.table_widget.setTabKeyNavigation(False)
#         self.table_widget.itemSelectionChanged.connect(self.show_certain_data)
#         table_groupbox_layout.addWidget(self.table_widget)

#         self.logs_groupbox = QtWidgets.QGroupBox(
#             'Лог', minimumHeight=200)  # Logs
#         logs_groupbox_layout = QtWidgets.QVBoxLayout()
#         logs_groupbox_layout.setContentsMargins(3, 5, 3, 3)
#         self.logs_groupbox.setLayout(logs_groupbox_layout)

#         logs_groupbox_layout.addWidget(self.log_text_box)

#         self.logs_clear_button = CustomButton(
#             'Очистить', clicked=lambda: self.log_text_box.clear())  # Clear logs
#         logs_groupbox_layout.addWidget(self.logs_clear_button)

#         v_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
#         v_splitter.setChildrenCollapsible(False)
#         v_splitter.addWidget(table_groupbox)
#         v_splitter.addWidget(self.logs_groupbox)
# # ------ START & STOP buttons -----------------------------------------------

#         self.process_all_button = CustomButton(
#             'Обработать', objectName="start_button")
#         self.process_all_button.installEventFilter(self)
#         self.stop_button = CustomButton(
#             'Стоп', enabled=False, objectName="stop_button")  # STOP
#         self.stop_button.installEventFilter(self)
# # ------ Others ------------------------------------------------------------

#         self.plot_groupbox = QtWidgets.QGroupBox(minimumWidth=180)
#         plot_groupbox_layout = QtWidgets.QGridLayout()
#         plot_groupbox_layout.setContentsMargins(5, 5, 5, 5)
#         self.plot_groupbox.setLayout(plot_groupbox_layout)

#         plot_groupbox_layout.addWidget(
#             self.tab_plot_widget.check_box_groupbox, 0, 0, 1, 21)

#         self.progress_bar = QtWidgets.QProgressBar(
#             format='%v/%m сек', maximum=36000, value=self.progress_value)  # sec
#         plot_groupbox_layout.addWidget(self.progress_bar,
#                                             1, 0, 1, 15)

#         package_number_label = QtWidgets.QLabel('Пакеты:')  # Package number
#         plot_groupbox_layout.addWidget(package_number_label,
#                                             1, 15, 1, 4)
#         plot_groupbox_layout.setAlignment(
#             package_number_label, QtCore.Qt.AlignmentFlag.AlignCenter)
#         self.package_num_label = QtWidgets.QLabel('0')
#         plot_groupbox_layout.addWidget(self.package_num_label,
#                                             1, 19, 1, 2)
#         # QToolButton # есть wordWrap

# # ------ Add menu --------------------------------------------------------
#         self.fill_menu()

# # ------ Set main grid --------------------------------------------------------

#         self.main_grid_layout.addWidget(self.sensors_num_groupbox,
#                                         0, 0, 1, 1)
#         self.main_grid_layout.addWidget(self.check_num_groupbox,
#                                         1, 0, 1, 1)
#         self.main_grid_layout.addWidget(self.gyro_fft_results_groupbox,
#                                         2, 0, 1, 2)
#         # self.main_grid_layout.addWidget(gyro_info_frame,
#         #                                 7, 0, 13, 2)
#         # self.main_grid_layout.addWidget(self.measurements_file_groupbox,
#         #                                 2, 0, 5, 2)
#         self.main_grid_layout.addWidget(v_splitter,
#                                         0, 2, 18, 1)
#         self.main_grid_layout.addWidget(self.process_all_button,
#                                         18, 2, 1, 1)
#         # self.main_grid_layout.addWidget(self.stop_button,
#         #                                 19, 2, 1, 1)

#         # self.main_grid_layout.addWidget(self.tab_plot_widget,
#         #                                 0, 3, 17, 1)
#         # self.main_grid_layout.addWidget(self.plot_groupbox,
#         #                                 17, 3, 3, 2)
# # ------ Load settings ---------------------------------------------------------------------

#         self.load_previous_settings(self.settings)
# # ------ Signal Connect --------------------------------------------------------------------

#         self.process_all_button.clicked.connect(self.full_measurement_start)
#         self.stop_button.clicked.connect(self.stop)
#         self.check_num_spinbox.valueChanged.connect(self.progress_bar_set_max)
# # ------  ----------------------------------------------------------------

#         effect = QtWidgets.QGraphicsOpacityEffect(self)
#         self.setGraphicsEffect(effect)
#         self.anim = QtCore.QPropertyAnimation(effect, b"opacity")
#         self.anim.setStartValue(0.0)
#         self.anim.setEndValue(1)
#         self.anim.setDuration(10)
#         self.anim.start()
#         self.show()

#         self.logger.debug("start import pandas in thread")
#         self.processing_thr.start()  # post init! (import pandas)
#         self.logger.debug("Программа запущена")

#         print(self.gyro_fft_results_groupbox.isVisible())
# # ----------------------------------------------------------------------------------------------
# #
# # ----------------------------------------------------------------------------------------------
# #
# # ----------------------------------------------------------------------------------------------

#     @QtCore.pyqtSlot()
#     def after_init_in_thread(self): #5678
#         self.processing_thr.finished.disconnect(self.after_init_in_thread)
#         self.processing_thr.finished.connect(self.show_all_time_data)
#         self.logger.debug("end thread_for_file_processing")
#         # self.show_certain_data()
#         self.logger.debug("start getting excel in thread")
#         self.tab_plot_widget.read_csv = self.processing_thr.read_csv
#         # self.tab_plot_widget.gyro_fft_results_groupbox.read_csv = \
#         self.gyro_fft_results_groupbox.read_csv = \
#             self.processing_thr.read_csv
#         self.tab_plot_widget.get_requirements()
#         # self.tab_plot_widget.gyro_fft_results_groupbox.exl_handler.start()  # post init!
#         self.gyro_fft_results_groupbox.exl_handler.start()  # post init!


# # ----------------------------------------------------------------------------------------------

#     @staticmethod
#     def add_action(menu: QtWidgets.QMenu, text: str,
#                    action_fun=None, shortcut=None, **opts):
#         action = QtWidgets.QAction(
#             text=text, parent=menu, **opts)#, opts)  # Measure
#         if shortcut:
#             if type(shortcut) != list:
#                 shortcut = [shortcut]
#             action.setShortcuts(shortcut)
#             action.setShortcutVisibleInContextMenu(True)
#         if action_fun:
#             action.triggered.connect(action_fun)
#         menu.addAction(action)
#         return action

#     def fill_menu(self):
#         """Create application menu bar."""
#         menu_bar = self.menuBar()
#         options_menu = menu_bar.addMenu("Измерения")
#         self.add_action(
#             menu=options_menu, text="Графики в png (Print)",
#             shortcut="Ctrl+P", action_fun=self.save_image)
#         self.save_action = self.add_action(
#             menu=options_menu, text="Сохранить последние данные (Save)",
#             shortcut="Ctrl+S", action_fun=self.save_results)
#         self.save_xlsx_action = self.add_action(
#             menu=options_menu, text="Сохранить в Excel (Write)",
#             shortcut="Ctrl+W",
#             action_fun=None
#         )
#         # self.gyro_fft_results_groupbox.path_te.click)
#             # action_fun=self.tab_plot_widget.gyro_fft_results_groupbox.write_xlsx_btn.click)
#         options_menu.addSeparator()
#         self.start_full_measurement_action = self.add_action(
#             menu=options_menu, text='Старт',
#             shortcut=["Return", "Ctrl+Return"],
#             action_fun=self.full_measurement_start)
#         self.stop_action = self.add_action(
#             menu=options_menu, text='Стоп', action_fun=self.stop, enabled=False)
#         options_menu.addSeparator()

#         self.measurement_action = self.add_action(
#             menu=options_menu, text="Старт без сохранения (Measure)",
#             shortcut="Ctrl+M", action_fun=self.measurement_start)
#         self.stop_with_no_save_action = self.add_action(
#             menu=options_menu, text="Стоп без сохранения",
#             shortcut=["Esc", "Ctrl+Space"],
#             action_fun=self.stop_no_save, enabled=False)
#         self.single_measurement_action = self.add_action(
#             menu=options_menu, text="Посмотреть байты",
#             shortcut="Ctrl+Alt+M", action_fun=self.single_measurement)
#         options_menu.addSeparator()

#         self.add_action(menu=options_menu, text="Выход",
#                    action_fun=self.close, statusTip="Exit application")
#         # statusTip - надпись, которая будет видна в строке состояния
#         # (надо включить строку состояния для этого)

#         # --- Mode menu ---
#         mode_menu = menu_bar.addMenu("Режим измерений")  # !
#         self.enable_crc_action = self.add_action(
#             menu=mode_menu, text="Контрольная сумма (CRC8)",
#             action_fun=self.change_crc_mode, checkable=True)
#         self.change_gyro_count_action = self.add_action(
#             menu=mode_menu, text="Изменить число гироскопов",
#             action_fun=self.change_gyro_num)

#         if self.GYRO_NUMBER == 1:
#             self.gyro1_4_action = self.add_action(
#                 menu=mode_menu, text="Сохранять все данные по RboxV1",
#                 action_fun=self.gyro_full_data_or_not, checkable=True)
#         # mode_menu.addSeparator()

#         # self.change_pause_time_action = self.add_action(
#         #     menu=mode_menu, text="Изменить паузу между вибрациями",
#         #     action_fun=self.change_pause_time)
#         # self.change_read_interval_action = self.add_action(
#         #     menu=mode_menu, text="Изменить период чтения СОМ порта",
#         #     action_fun=self.change_read_interval)
#         # self.change_frame_width_action = self.add_action(
#         #     menu=mode_menu, text="Изменить окно",
#         #     action_fun=self.change_frame_width)
#         # --- ---
#         self.form_group_box = QtWidgets.QGroupBox(objectName='no_border')
#         layout = QtWidgets.QFormLayout()
#         self._spin_widget = QtWidgets.QSpinBox(
#             mode_menu, maximumWidth=200, maximum=100_000,
#             minimum=75, value=self.PAUSE_INTERVAL_MS,
#             alignment=QtCore.Qt.AlignmentFlag.AlignHCenter) #, maximumHeight=220)
#         def ff():
#             self.PAUSE_INTERVAL_MS = self._spin_widget.value()
#         self._spin_widget.valueChanged.connect(ff) 
#         self._spin_widget2 = QtWidgets.QSpinBox(
#             mode_menu, maximumWidth=200, maximum=1_000,
#             minimum=20, value=self.READ_INTERVAL_MS,
#             alignment=QtCore.Qt.AlignmentFlag.AlignHCenter) #, maximumHeight=220)
#         def ff2():
#             self.READ_INTERVAL_MS = self._spin_widget2.value()
#         self._spin_widget2.valueChanged.connect(ff2) 
#         layout.addRow(QtWidgets.QLabel("Пауза между вибрациями:"), self._spin_widget)
#         layout.addRow(QtWidgets.QLabel("Период чтения:"), self._spin_widget2)
#         self.form_group_box.setLayout(layout)
#         layout.setContentsMargins(17, 5, 5, 5)
#         _widget_action = QtWidgets.QWidgetAction(mode_menu)
#         _widget_action.setDefaultWidget(self.form_group_box)
#         mode_menu.addAction(_widget_action)
#         mode_menu.addSeparator()
#         # --- Settings control ---
#         settings_menu = menu_bar.addMenu("Настройки")

#         self.settings_autosave_action = self.add_action(
#             menu=settings_menu,
#             text="Автосохранение настроек", checkable=True)
#         self.settings_autosave_action.setChecked(True)
#         self.save_settings_action = self.add_action(
#             menu=settings_menu, text="Сохранить текущие настройки",
#             action_fun=self.save_settings)
#         self.open_settings_folder_action = self.add_action(
#             menu=settings_menu, text="Открыть папку с настройками",
#             action_fun=lambda: ShellExecute(
#                 0, 'explore', 'settings', None, None, 1))
#             # lambda: os.system(r'start settings'))
#         self.load_settings_folder_action = self.add_action(
#             menu=settings_menu, text="Загрузить настройки",
#             action_fun=lambda: self.load_previous_settings(self.settings))
#         # self.load_settings_folder_action.triggered.connect(
#         #     lambda: self.processing_thr.load_settings(self.FFT_OPTIONS_FILE_NAME))
        
#         info_menu = menu_bar.addMenu("Справка")
#         self.add_action(
#             menu=info_menu, text="Руководство пользователя",
#             action_fun=lambda: self.open_manual(self.MAIN_PATH_TO_MANUAL, self.PATH_TO_MANUAL))
# # ------  ---------------------------------------------------------------------

#     def set_visual_style(self, filename, spacing=2, style='Fusion'):
#         self.setWindowTitle(f"GyroVibroTest ({self.GYRO_NUMBER})") # в названии номер стенда писать
#         # print(QtWidgets.QStyleFactory.keys())
#         QtWidgets.QApplication.setStyle(style)
#         # 'Fusion' 'Windows' 'windowsvista' ... QtWidgets.QStyle
#         widget = QtWidgets.QWidget()
#         layout = QtWidgets.QGridLayout(widget, spacing=spacing)
#         self.logger.debug(layout.getContentsMargins())
#         self.logger.debug(f"os info: {sys.getwindowsversion()}")
#         if sys.getwindowsversion().major <= 7:
#             layout.setContentsMargins(5, 0, 5, 5)
#             layout.setSpacing(int(spacing/2))
#         else:
#             layout.setContentsMargins(10, 0, 10, 10)
#         # self.statusBar().showMessage("this is status bar.") 
#         self.setCentralWidget(widget)
#         # ------ Style ----------------------------------------------------
#         try:
#             with open(filename, "r") as style_sheets_css_file:
#                 self.setStyleSheet(style_sheets_css_file.read())
#         except FileNotFoundError:
#             self.logger.warning(f'No file {filename}!')
#         try:
#             self.app_icon_no_com = QtGui.QIcon()
#             for i in [16, 24, 32, 48]:
#                 self.app_icon_no_com.addFile(
#                     get_res_path(f'res\icon_{i}.png'),
#                     QtCore.QSize(i, i))
#             self.app_icon_com_busy = QtGui.QIcon(
#                 get_res_path('res\icon_48_2.png'))
#             self.setWindowIcon(self.app_icon_no_com)
#         except FileNotFoundError:
#             pass
#         return layout
# # ------  ---------------------------------------------------------------------
# # ------  ---------------------------------------------------------------------
# # ------  ---------------------------------------------------------------------
    
#     @property
#     def package_num(self):
#         return int(self.package_num_label.text())
    
#     @property
#     def fs(self):
#         """Sampling frequency."""
#         return int(self.sensors_num.currentText())
    
#     def open_manual(self, main_path, path: str):
#         import pywintypes
#         main_path = os.path.realpath(main_path)  # realpath is necessary
#         try:
#             # os.startfile(path)
#             ShellExecute(0, 'open', main_path, '', '', 1)
#         except pywintypes.error:
#             self.logger.warning(f"File {main_path} not found!")
#             path = os.path.realpath(path)
#             try:
#                 ShellExecute(0, 'open', path, '', '', 1)
#             except pywintypes.error:
#                 self.logger.warning(f"File {path} not found!")

#     @QtCore.pyqtSlot()
#     def change_pause_time(self):
#         self.PAUSE_INTERVAL_MS, _ = QtWidgets.QInputDialog.getInt(
#            self, 'Изменение параметра', 'Введите время паузы в мс:',
#            max=100_000, min=75, value=self.PAUSE_INTERVAL_MS)
#         self.progress_bar_set_max()

#     @QtCore.pyqtSlot()
#     def change_frame_width(self):
#         self.processing_thr.time_frame_len, _ = QtWidgets.QInputDialog.getInt(
#            self, 'Изменение параметра', 'Введите ширину окна в секундах:',
#            max=50, min=0.5, value=self.processing_thr.time_frame_len) # что если данных слишком много будет получено?


#     def gyro_full_data_or_not(self):
#         self.processing_thr.pack_len = (4 if self.gyro1_4_action.isChecked() else 2)  # !
#         if self.processing_thr.pack_len == 2 and self.GYRO_NUMBER == 1:
#             self.enable_crc_action.setChecked(False)
#             self.processing_thr.crc_flag = False
#             self.enable_crc_action.setDisabled(True)
#         else:
#             self.enable_crc_action.setDisabled(False)

#     @QtCore.pyqtSlot()
#     def change_crc_mode(self):
#         if self.processing_thr.pack_len == 2 and self.GYRO_NUMBER == 1:
#             self.enable_crc_action.setChecked(False)
#         self.processing_thr.crc_flag = self.enable_crc_action.isChecked()

#     @QtCore.pyqtSlot()
#     def change_gyro_num(self):
#         msg = QtWidgets.QMessageBox(
#             parent=self, text="Перезапустить программу?")
#         msg.setStandardButtons(
#             QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
#         if msg.exec() != msg.Ok:
#             return
#         # QtCore.QCoreApplication.quit(); self.restart()
#         self.settings.setValue("GYRO_NUMBER", (3 if self.GYRO_NUMBER == 1 else 1))
#         self.close()  # self.save_settings()
#         status = QtCore.QProcess.startDetached(sys.executable, sys.argv)
#         self.logger.debug(f"Restart {status}")

# # ---------------------------------------------------------------------------------------------
# # ----- context menu --------------------------------------------------------------------------
#     @QtCore.pyqtSlot()
#     def eventFilter(self, obj, event):
#         # print(time())
#         if event.type() != QtCore.QEvent.ContextMenu:
#             return False
#         if obj is self.stop_button:
#             if not self.processing_thr.isRunning():
#                 return True
#             action = QtWidgets.QAction('Стоп без сохранения', self)
#             action.triggered.connect(self.stop_no_save)
#         elif obj is self.process_all_button:
#             if self.processing_thr.isRunning():
#                 return True
#                 # action.setDisabled(True)
#             action = QtWidgets.QAction('Старт без сохранения', self)
#             action.triggered.connect(self.measurement_start)
#         else:
#             return False
#         _menu = QtWidgets.QMenu(self)
#         _menu.addAction(action)
#         _menu.exec(event.globalPos())
#         _menu.deleteLater()
#         return True

# # ----------------------------------------------------------------------------------------------
# ################################################################################################
# #
# # ----------------------------------------------------------------------------------------------
# # ----------------------------------------------------------------------------------------------
# #
# ################################################################################################

#     @QtCore.pyqtSlot()
#     def save_results(self):  # ! предлагать изменить имя файла
#         "Open dialog and save last fft results after confirmation."
#         # text = ''
#         msg = QtWidgets.QMessageBox(
#             parent=self, text="Сохранить последний результат fft?")
#         # if self.processing_thr.total_pack_num and self.processing_thr.flag_by_name_:
#             # name_list = [name.replace('/', '\\') for name in self.processing_thr.save_file_name if len(name)]
#         #     if name_list:
#         #         text = '\nFilenames:\n' + ', '.join(name_list)
#         #         msg.setText("Сохранить последний результат fft?" + text)
#         #     else:
#         #         msg.setText("Нечего сохранять")
#         #         msg.exec()
#         #         return
#         if not self.processing_thr.total_pack_num:
#             msg.setText("Нечего сохранять")
#             msg.exec()
#             return
#         msg.setStandardButtons(
#             QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
#         if msg.exec() != msg.Ok:
#             return False
#         self.logger.debug("Try to save last data")
#         if self.check_thread():
#             self.logger.warning("Thread still work")
#             return False
#         # Check filenames
#         if not self.processing_thr.flag_by_name_:
#             for i in range(self.GYRO_NUMBER):  # !
#                 self.processing_thr.save_file_name[i] = \
#                     self.gyro_info_groupbox_list[i].make_filename()  # !  # без создания имени не получится
#         self.processing_thr.start()
#         return True

#     @QtCore.pyqtSlot(list)
#     def run_thread_for_file_processing(self, items: list):  ################### изменить для трех, изменить имена
#         """Process files to create medial frequency plot."""
#         self.logger.debug(f"files: {items}")
#         if self.check_thread():
#             self.logger.warning("Thread still work")
#             return False
#         self.tab_plot_widget.clear_plots(fs=self.fs)
#         # Copy variables to another classes and start thread
#         self.tab_plot_widget.fs = self.fs
#         self.processing_thr.fs = self.fs
#         self.processing_thr.flag_by_name = True
#         self.processing_thr.selected_files_to_fft = items
#         self.processing_thr.start()
#         # self.processing_thr.finished.connect(self.show_all_time_data)
#         return True

#     @QtCore.pyqtSlot()
#     def show_all_time_data(self):
#         self.logger.debug("end thread_for_file_processing")
#         if (not self.processing_thr.total_pack_num or 
#             self.processing_thr.time_data is None or
#             len(self.processing_thr.time_data.shape) != 2):
#             self.tab_plot_widget.time_plot.clear_time_plots()
#             return
#         # if self.processing_thr.time_data.shape[0] < 100_000:
#         if self.processing_thr.time_data.shape[0] > 1000_000:
#             k = 1 + int(self.processing_thr.time_data.shape[0] / 1000_000)
#             num = self.processing_thr.total_pack_num
#             self.logger.warning(
#                 f"The file contains a large number of packages! ({num})")
#             self.logger.warning(f'Display the points with thinning! ({k})')
#             QtCore.QCoreApplication.processEvents()
#         else:
#             k = 1
#         data = self.processing_thr.change_data(
#             self.processing_thr.time_data[:self.processing_thr.total_pack_num:k, :],
#             self.processing_thr.k_amp,
#             self.fs, self.processing_thr.pack_len)
#         # self.tab_plot_widget.plot_time_graph2(data_arr=data)
#         self.tab_plot_widget.time_plot.plot_time_graph(
#             data[:, 0], data[:, 2], data[:, 1::self.processing_thr.pack_len])
#         self.tab_plot_widget.region.setVisible(False)
#         self.tab_plot_widget.time_plot.autoRange()
#         self.logger.debug('end')
# # --- For start events --------------------------------------------------------------------------------

#     def preparation_before_start(self):
#         self.setWindowIcon(self.app_icon_com_busy)
#         self.process_all_button.setDisabled(True)
#         self.set_available_buttons(flag_running=True)  # disable widgets
#         self.tab_plot_widget.fs = self.fs
#         self.tab_plot_widget.clear_plots(fs=self.fs)

#     def reset_vars_before_start(self):
#         self.tab_plot_widget.fs = self.fs
#         self.tab_plot_widget.setCurrentIndex(0)
#         self.progress_value = 0  # не создавать эту переменную
#         self.progress_bar.setValue(0)
#         self.package_num_label.setText('0')
#         self.time_error = 0  # !
#         self.count = 0
#         self.current_cycle = 1
#         self.wait_time = 0
#         self.tab_plot_widget.change_visibility(False)

# # ---------------------------------------------------------------------------------------

#     @QtCore.pyqtSlot()
#     def single_measurement(self):
#         """Try to start measurement without sending command and saving results."""
#         self.reset_vars_before_start()
#         # Check and open COM port
#         self.preparation_before_start()
#         self.progress_bar.setMaximum(36000)
#         self.log_text_box.insertHtml('<br />')
#         self.logger.info("Read bytes")
#         self.bytes_flag = True
#         self.start_time = time()
#         return True

# # ---------------------------------------

#     def check_thread(self):
#         if not self.processing_thr.read_csv:
#             self.logger.debug("not imported yet")
#             for _ in range(8):
#                 sleep(0.1)
#                 if self.processing_thr.read_csv:
#                     break
#         self.logger.debug(
#             f"data_recieved_event {self.processing_thr.data_received_event.is_set()}")
#         # self.processing_thr.flag_full_measurement_start = False
#         # self.processing_thr.flag_measurement_start = False
#         return self.processing_thr.isRunning()

#     @QtCore.pyqtSlot()
#     def measurement_start(self):
#         """Try to start measurement without sending command and saving results."""
#         self.reset_vars_before_start()
#         self.tab_plot_widget.region.setVisible(False)
#         if self.check_thread():
#             self.logger.warning("Thread still work")
#             return False
#         # Check and open COM port
#         self.preparation_before_start()
#         self.progress_bar.setMaximum(36000)

#         self.log_text_box.insertHtml('<br />')
#         self.logger.info("Start without saving results")
#         # Start timers
#         self.start_time = time()
#         # Copy variables to another classes and start thread
#         self.processing_thr.fs = self.fs
#         self.processing_thr.flag_measurement_start = True
#         self.processing_thr.flag_do_not_save = True
#         # self.processing_thr.total_time = self.table_widget.total_time
#         self.processing_thr.start()
#         self.set_available_buttons(flag_running=True)  # disable widgets
#         return True

#     @QtCore.pyqtSlot()
#     def full_measurement_start(self):
#         self.reset_vars_before_start()
#         self.tab_plot_widget.region.setVisible(True)
        
#         if self.check_thread():
#             self.logger.warning("Thread still work")
#             return False
#         # Check measurement file
#         if not self.table_widget.total_time:
#             if not self.measurements_file_groupbox.choose_and_load_file():
#                 self.logger.debug("No data from file")
#                 return False
#             self.logger.debug("Data from file was loaded")
#         # Check COM port
#         self.preparation_before_start()
#         self.progress_bar.setFormat('%v/%m сек (определение смещения)')
#         # надо понять, можно ли 2 раза нажать на старт или нажать на стоп, пока еще запуск не произошел
#         self.tab_plot_widget.append_fft_plot_tab()
#         self.progress_bar_set_max()
#         self.logger.debug(f"cycle_num = {self.check_num_spinbox.value()}")

#         # Start timers
#         self.start_time = time()  # !!!!!
#         # Copy variables to another classes and start thread
#         self.processing_thr.fs = self.fs
#         self.processing_thr.flag_measurement_start = True  # !!!!!
#         # self.processing_thr.total_time = self.table_widget.total_time
#         self.processing_thr.num_measurement_rows = self.table_widget.rowCount()
#         self.processing_thr.flag_do_not_save = True
#         self.processing_thr.total_cycle_num = self.check_num_spinbox.value()
#         self.processing_thr.start()
#         self.table_widget.selectRow(0)
#         self.log_text_box.insertHtml('<br />')
#         self.logger.info("Start")
#         self.progress_bar.setFormat('%v/%m сек')
#         self.logger.debug('start full measurements')
#         return True

#     @QtCore.pyqtSlot()
#     def stop_no_save(self):
#         self.processing_thr.flag_do_not_save = True
#         self.stop()

#     @QtCore.pyqtSlot()
#     def stop(self):
#         """Stop timers, stop measurement processing in thread,
#         send filenames to thread and stop command to vibrostand."""
#         self.__no_data_flag = 0 # флаг, который показывает, идут ли данные с порта или нет
#         self.setWindowIcon(self.app_icon_no_com)
#         # --- Check filenames ---
#         flag = self.processing_thr.flag_full_measurement_start
#         if self.processing_thr.isRunning() and flag:
#             if self.processing_thr.flag_do_not_save:
#                 self.logger.info("No saving")
#             else:
#                 for i in range(self.GYRO_NUMBER):
#                     self.processing_thr.save_file_name[i] = \
#                         self.gyro_info_groupbox_list[i].make_filename()
#         # --- ---
#         self.processing_thr.flag_full_measurement_start = False
#         self.processing_thr.flag_measurement_start = False
#         self.processing_thr.data_received_event.set()
#         self.flag_send = False
#         # --- ---
#         self.set_available_buttons(False)

#         try: # only for debug
#             pass
#         except Exception:
#             pass
# ###############################################################################
# # ----- plotting --------------------------------------------------------------

#     @QtCore.pyqtSlot(int, np.ndarray)
#     def get_and_show_data_from_thread(
#         self, package_num_signal: int, plot_data: np.ndarray):
#         """Receiving the processed measurement data
#             (package num, time data to graph)."""
#         self.package_num_label.setText(str(package_num_signal))
#         self.progress_value = time() - self.start_time
#         self.progress_bar.setValue(int(round(self.progress_value)))
#         # if self.count == 0:
#         self.tab_plot_widget.time_plot.plot_time_graph(
#             plot_data[:, 0], plot_data[:, 2],
#             plot_data[:, 1::self.processing_thr.pack_len],
#             # )
#             not self.processing_thr.flag_full_measurement_start and self.progress_bar.maximum() == 36000)
#         self.logger.debug(
#             f"plot time graph; real progress_value: {self.progress_value}," +
#             f"thr_stop, count = {self.count}, " +
#             f"package_num = {package_num_signal} ")

#     @QtCore.pyqtSlot()
#     def show_certain_data(self):  # работает, просто менять окно, пусть будут выведены все данные
#         """Show part of time plot when you select row in table."""
#         if self.processing_thr.isRunning():
#             return False
#         package_num = self.package_num
#         if not (package_num and len(self.processing_thr.package_num_list) >= 2):
#             return False
#         time = self.table_widget.get_summary_time() / 1000
#         time += self.PAUSE_INTERVAL_MS / 1000 * self.table_widget.currentRow()
#         self.logger.debug(
#             f"currRow:{self.table_widget.currentRow()} currCycle:{self.current_cycle} time:{time}")
#         start = int(time) * self.fs  # - self.processing_thr.points_shown / 4
#         start += self.processing_thr.package_num_list[-2]
#         self.logger.debug(f"package_num_list: {self.processing_thr.package_num_list} {start}")
#         if start > package_num or start > self.processing_thr.time_data.shape[0]:
#             self.logger.warning("Selected row out of range")
#             return False
#         end = start + self.processing_thr.time_frame_len * self.fs  # self.processing_thr.to_plot.shape[0]
#         if end > package_num or end > self.processing_thr.time_data.shape[0]:
#             end = package_num
#         self.logger.debug(f"start={start}, end={end}")
#         self.tab_plot_widget.time_plot.plot_time_graph(
#             self.processing_thr.time_data[start:end, 0] / self.fs,
#             self.processing_thr.time_data[start:end, 2] / 1000,
#             # self.processing_thr.time_data[start:end, 2::self.processing_thr.pack_len]  / 1000,
#             self.processing_thr.time_data[start:end, 1::self.processing_thr.pack_len] / 1000 / self.processing_thr.k_amp)
#         self.tab_plot_widget.region.setVisible(False)
#         self.tab_plot_widget.time_plot.autoRange()
#         # self.tab_plot_widget.time_plot.plotItem.setYRange(0, 20)  # !!!!!!!s
#         # self.tab_plot_widget.region.setVisible(True)

#     @QtCore.pyqtSlot(bool)
#     def plot_fft(self, _):
#         """Adds points to frequency graphs."""
#         self.logger.debug("start plot_fft")
#         # if self.count == 1:  # можно установить ссылку на массив,
#         # тогда при его заполнении график будет меняться автоматически (не будет)
#         cycle = self.current_cycle
#         self.tab_plot_widget.set_fft_data(
#             self.processing_thr.all_fft_data[:, (cycle-1)*4:cycle*4, :],
#             self.processing_thr.border)
#         self.logger.debug("end plot_fft")

#     @QtCore.pyqtSlot(list, np.ndarray)
#     def plot_fft_final(self, name: list, data: np.ndarray):
#         self.package_num_label.setText(
#             str(self.processing_thr.total_pack_num))
#         # здесь число пакетов получать, чтобы можно было прежние записи просматривать
#         self.tab_plot_widget.set_fft_median_data(data, name)

#     @QtCore.pyqtSlot()
#     def save_image(self):
#         check_box_list = self.tab_plot_widget.plot_check_box_list[1:-1]
#         for i, plot_check_box in enumerate(check_box_list):
#             if plot_check_box.isChecked():
#                 self.processing_thr.save_file_name[i] = \
#                     self.gyro_info_groupbox_list[i].make_filename()
#                 if self.processing_thr.save_file_name[i]:
#                     self.tab_plot_widget.save_plot_image(
#                         self.processing_thr.save_file_name[i])
#         self.logger.debug("Saving complete")
# # ------ Widgets events -------------------------------------------------------

#     @QtCore.pyqtSlot()
#     def progress_bar_set_max(self):
#         self.progress_bar.setMaximum(1)

#     def set_available_buttons(self, flag_running: bool):
#         """Enable or disable widgets."""
#         self.check_num_spinbox.setDisabled(flag_running)  # по идее стоит запрещать только увеличивать число циклов !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#         self.measurements_file_groupbox.open_file_btn.setDisabled(flag_running) #########
#         self.measurements_file_groupbox.choose_file_btn.setDisabled(flag_running) #######
#         self.process_all_button.setDisabled(flag_running)
#         self.stop_button.setDisabled(not flag_running)
#         self.start_full_measurement_action.setDisabled(flag_running)
#         self.single_measurement_action.setDisabled(flag_running)
#         self.measurement_action.setDisabled(flag_running)
#         self.stop_action.setDisabled(not flag_running)
#         self.stop_with_no_save_action.setDisabled(not flag_running) 
#         self.save_action.setDisabled(flag_running)
#         self.sensors_num_groupbox.setDisabled(flag_running)

#         self.enable_crc_action.setDisabled(flag_running)
#         self.change_gyro_count_action.setDisabled(flag_running)
#         # self.change_frame_width_action.setDisabled(flag_running) # !
#         # self.change_pause_time_action.setDisabled(flag_running) # !
#         # for groupbox in self.gyro_info_groupbox_list: # на 300-400 мс может блокировать считывание данных
#         #     groupbox.choose_path_button.setDisabled(flag_running)
#         # if self.GYRO_NUMBER == 1:
#         #     self.gyro1_4_action.setDisabled(flag_running)  # !
# # -------------------------------------------------------------------------------------------------------------

#     def get_data_from_file(self, filename_path_watcher: str):
#         """Get data from file and put it in table."""
#         try:
#             with open(filename_path_watcher, 'r') as file:
#                 self.table_widget.set_table(file)
#                 self.progress_bar_set_max()
#             return 1
#         except FileNotFoundError:
#             self.logger.debug("FileNotFoundError " + filename_path_watcher)
#             return 0
# # -------------------------------------------------------------------------------------------------------------

#     @QtCore.pyqtSlot()
#     def closeEvent(self, _):
#         """Sending stop command to the vibrostand and saving user settings."""
#         self.logger.info("Saving the settings and exit")
#         QtWidgets.QApplication.setOverrideCursor(
#             QtCore.Qt.CursorShape.WaitCursor)
#         self.stop()
#         for i in range(self.tab_plot_widget.count()):
#             # во избежание 'Warning: ViewBox should be closed before application exit.'
#             self.tab_plot_widget.widget(i).deleteLater() 
#         self.save_settings()
#         self.logger.debug("Close COM object")
#         # self.tab_plot_widget.gyro_fft_results_groupbox.exl_handler.quit() # !!!!!
#         self.gyro_fft_results_groupbox.exl_handler.quit() # !!!!!
#         QtWidgets.QApplication.restoreOverrideCursor()

# # ------ settings --------------------------------------------------------------------
#     def save_settings(self):
#         """Check condition and write settings in .ini and .json files."""
#         self.tab_plot_widget.projects_combo_box.save_json(self.PROJECT_FILE_NAME)
#         # self.settings.setValue('GYRO_NUMBER', self.GYRO_NUMBER)
#         # --- ---
#         self.settings.setValue(f'{self.GYRO_NUMBER}/autosave',
#                                int(self.settings_autosave_action.isChecked()))
#         if self.settings_autosave_action.isChecked():
#             self.save_all_settings(self.settings)

#     def save_all_settings(self, settings: QtCore.QSettings):
#         """Write settings in ini file."""
#         self.sensors_num.save_all()

#         settings.beginGroup(f'{self.GYRO_NUMBER}')
#         settings.setValue('WINDOW_POS', self.pos())
#         settings.setValue('WINDOW_SIZE', self.size())
#         settings.setValue('SPLITTER', 
#                           self.findChild(QtWidgets.QSplitter).saveState())
#         settings.setValue('cycle_num',
#                           self.check_num_spinbox.value())
#         for groupbox in self.gyro_info_groupbox_list:
#             groupbox.save_settings(settings)
#         self.measurements_file_groupbox.save_settings(settings)
#         self.tab_plot_widget.save_settings(settings)  # !
#         settings.setValue(
#             'enable_debug_in_file',
#             int(self.log_text_box.enable_file_debug_action.isChecked()))
#         # лучше сохранять и распаковывать эти настройки в отдельном файле в классе комбобокса
#         # или, как максимум, одну функцию оставить
#         settings.setValue(
#             'PAUSE_INTERVAL_MS', self.PAUSE_INTERVAL_MS)
#         settings.setValue(
#             'READ_INTERVAL_MS', self.READ_INTERVAL_MS)
#         settings.setValue('crc_enable',
#                           int(self.enable_crc_action.isChecked()))
#         settings.setValue('time_frame_len',
#             self.processing_thr.time_frame_len)
#         if self.GYRO_NUMBER == 1:
#             settings.setValue(
#                 'full_data_flag', int(self.gyro1_4_action.isChecked()))
#         settings.endGroup()
#         self.logger.info("Save settings")

#     def load_previous_settings(self, settings: QtCore.QSettings):
#         """Get previous settings from .ini and .json files."""
#         # section = f'{self.GYRO_NUMBER}/'
#         settings.beginGroup(f'{self.GYRO_NUMBER}')
#         if settings.contains('WINDOW_POS'):
#             self.move(settings.value('WINDOW_POS'))
#         if settings.contains('WINDOW_SIZE'):
#             self.resize(settings.value('WINDOW_SIZE'))
#         if settings.contains('SPLITTER'):
#             self.findChild(QtWidgets.QSplitter).restoreState(
#                 settings.value('SPLITTER'))
#         self.processing_thr.time_frame_len = self.get_settings(
#             "time_frame_len", 16)  # !
#         self.log_text_box.enable_file_debug_action.setChecked(
#             self.get_settings("enable_debug_in_file", True))
#         self.enable_crc_action.setChecked(
#             self.get_settings("crc_enable",
#                               (False if self.GYRO_NUMBER == 1 else True)))
#         self.settings_autosave_action.setChecked(
#             self.get_settings("autosave", True))
#         self.check_num_spinbox.setValue(
#             self.get_settings("cycle_num", 1))
#         self.change_crc_mode()
#         self.tab_plot_widget.plot_check_box_list[-1].setChecked(
#             self.get_settings("ref_check_box", True))
#         if self.GYRO_NUMBER == 1:
#             self.gyro1_4_action.setChecked(
#                 self.get_settings("1/full_data_flag", False))
#             # self.gyro1_4_action.setChecked(int(self.settings.value("1/full_data_flag")))
#             self.gyro_full_data_or_not()

#         for groupbox in self.gyro_info_groupbox_list:
#             groupbox.get_settings(settings)
#         self.measurements_file_groupbox.get_settings(settings)

#         self.tab_plot_widget.load_settings(
#             settings, self.PROJECT_FILE_NAME) # 
#         settings.endGroup()
#         self.processing_thr.load_settings(self.FFT_OPTIONS_FILE_NAME)
#         self.logger.info('Settings is successfully loaded')

#     def get_settings_or_sysargv(self, name: str, otherwise_val):
#         """Get attribute from sys.argv or from settings or set default value."""
#         # name = name.upper()
#         if self.args:
#             for arg in self.args[1:]:
#                 try:
#                     command = re.split("=", arg)
#                     if (command[0] == name):
#                         return int(command[1]) # !
#                 except ValueError:
#                     print(f"Wrong argument {arg}, ValueError")
#                 except IndexError:
#                     print(f"Wrong argument {arg}, IndexError")
#         return self.get_settings(name, otherwise_val)

#     def get_settings_from_sysargv(self, name: str, otherwise_val, to_type=int):
#         """Get attribute from sys.argv or from settings or set default value."""
#         # name = name.upper()
#         if self.args:
#             for arg in self.args[1:]:
#                 try:
#                     command = re.split("=", arg)
#                     if (command[0] == name):
#                         return to_type(command[1]) # !
#                 except ValueError:
#                     print(f"Wrong argument {arg}, ValueError")
#                 except IndexError:
#                     print(f"Wrong argument {arg}, IndexError")
#         return otherwise_val

#     def get_settings(self, name: str, otherwise_val):
#         """Get settings or set default value."""
#         if not self.settings.contains(name):
#             return otherwise_val
#         try:
#             return int(self.settings.value(name))
#         except ValueError:
#             return otherwise_val
