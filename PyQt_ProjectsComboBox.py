# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

import os
import json
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt_Functions import get_icon_by_name, get_res_path
from widgets.PyQt_CustomPushButton import CustomButton


# по идее не влияет на основную программу, так что проблем при открытии во время цикла быть не должно
class CustomDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CustomDialog, self).__init__(
            parent, maximumSize=QtCore.QSize(500, 150),
            windowTitle="Окно добавления пользователей")
        STYLE_SHEETS_FILENAME = 'res\StyleSheetsDialog.css'
        with open(get_res_path(STYLE_SHEETS_FILENAME), "r") as style_sheets:
            self.setStyleSheet(style_sheets.read())
        app_icon = QtGui.QIcon(get_res_path(f'res\icon_48.png'))
        self.setWindowIcon(app_icon)
        self.setWindowFlags(QtCore.Qt.WindowType.CustomizeWindowHint |
                            QtCore.Qt.WindowType.WindowCloseButtonHint)
        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.button_box = QtWidgets.QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QtWidgets.QGridLayout()
        # message = QtWidgets.QLabel("Выберите путь к проекту и дайте название",
        #                            wordWrap=True, maximumHeight=80)
        # layout.addWidget(message, 0, 0, 1, 3)
        name_label = QtWidgets.QLabel("Имя:")
        layout.addWidget(name_label, 1, 0, 1, 1)
        self.person_name = QtWidgets.QLineEdit()
        # self.project_name.textChanged.connect(self.check)
        layout.addWidget(self.person_name, 1, 1, 1, 2)
        # path_label = QtWidgets.QLabel("Путь:")
        # layout.addWidget(path_label, 2, 0, 1, 1)
        # self.path_to_prj = QtWidgets.QLineEdit()
        # layout.addWidget(self.path_to_prj, 2, 1, 1, 1)
        # self.path_to_prj.textChanged.connect(self.check)
        # open_folder_btn = CustomButton(  # QtWidgets.QPushButton((
        #     icon=get_icon_by_name('open_folder'))
        # layout.addWidget(open_folder_btn, 2, 2, 1, 1)
        # open_folder_btn.clicked.connect(self.get_path)
        layout.addWidget(self.button_box, 3, 0, 1, 3)
        self.setLayout(layout)


class ProjectsComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None, projects_dict=None):
        super(ProjectsComboBox, self).__init__(parent, editable=True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)
        # QToolButton  # есть wordWrap
        self.installEventFilter(self)
        self.dlg = CustomDialog()
        # self.projects_dict = projects_dict if projects_dict else {}

    # @property
    # def current_project(self) -> str:
    #     """Path to elected project."""
    #     return self.projects_dict.get(self.currentText(), '')

    @QtCore.pyqtSlot()
    def delete_project_item(self):
        self.removeItem(self.currentIndex())

    @QtCore.pyqtSlot()        
    def change_current_project_item(self):  # сделать этот пункт недоступным просто
        self.dlg.person_name.setText(self.currentText())
        if self.dlg.exec():  # сделать запуск с open(), потом принять сигнал завершения вместе с флагом
            self.setCurrentText('')
            self.apply_changes()

    @QtCore.pyqtSlot()
    def add_project_item(self):
        if self.dlg.exec():
            name = self.dlg.person_name.text()
            self.insertItem(0, name)
            self.setCurrentIndex(0)
            self.apply_changes()

    def apply_changes(self):
        name = self.dlg.person_name.text()
        self.setCurrentText(self.dlg.person_name.text())
        self.setItemText(self.currentIndex(), name)
        
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.ContextMenu:
            menu = QtWidgets.QMenu(self)
            change_action = QtWidgets.QAction('Изменить пункт', menu)
            change_action.triggered.connect(self.change_current_project_item)
            menu.addAction(change_action)
            add_action = QtWidgets.QAction('Добавить пункт', menu)
            add_action.triggered.connect(self.add_project_item)
            menu.addAction(add_action)
            delete_action = QtWidgets.QAction('Удалить текущий пункт', menu)
            delete_action.triggered.connect(self.delete_project_item)
            if not self.count():
                change_action.setDisabled(True)
                delete_action.setDisabled(True)
            menu.addAction(delete_action)
            menu.exec(event.globalPos())
            menu.deleteLater()
            return True
        return False

    # def get_current_setting(self):
    #     """dict name: 'header maker'"""
    #     dict = {
    #         'header assembly on_fly': self.on_fly_checkbox.isChecked()
    #         }
    #     common_dict = DataBase.get('__dict_with_app_settings')
    #     common_dict['header maker'] = dict
    #     DataBase.setParams(__dict_with_app_settings=common_dict)
    #     # return dict

    # def restore_settings(self, dict: dict):
    #     """dict name: 'header maker'"""
    # # def save_json(self, PROJECT_FILE_NAME):
    # #     with open(PROJECT_FILE_NAME, 'w', encoding='utf-8') as f:
    # #         json.dump(self.projects_dict,
    # #                   f, ensure_ascii=False, indent=4)
    # #     #     d = {"dict": self.tab_plot_widget.projects_combo_box.projects_dict, 
    # #     #           "ddd22": False, "2ddd22": "f"}
    # #     #     json.dump(d, f, ensure_ascii=False, indent=4)

    # # def load_json(self, PROJECT_FILE_NAME):
    #     # with open(PROJECT_FILE_NAME, 'r', encoding='utf-8') as f:
    #     #     self.projects_dict = json.load(f)
    #     self.clear()
    #     if not dict:  # keys сортируются автоматически
    #         return
    #     self.addItems(dict.keys())
    #     for i in range(self.count()):
    #         self.setItemData(
    #             i, dict.get(self.itemText(i)),
    #             QtCore.Qt.ItemDataRole.ToolTipRole)    
# ----------------------------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------------------------