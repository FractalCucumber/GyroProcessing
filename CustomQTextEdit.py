# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

from time import time, sleep, perf_counter
import sys
import os
import re
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui


class CustomQTextEdit(QtWidgets.QTextEdit):
    def __init__(self, *args, **kwds):
        QtWidgets.QTextEdit.__init__(self, *args, **kwds)
            # folder_name, objectName="with_border"
        self.setTabChangesFocus(True)
        self.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self.__textEditContextMenu)
        self.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        # self.setSizePolicy(
        #     QtWidgets.QSizePolicy.Policy.Ignored,
        #     QtWidgets.QSizePolicy.Policy.Ignored)
        self.textChanged.connect(self.__textChangedHandler)
        self.__open_folder_action = QtWidgets.QAction(
            "Open folder", self)
        self.__open_folder_action.setShortcut('Ctrl+O')
        self.__open_folder_action.setShortcutContext(
            QtCore.Qt.ShortcutContext.WidgetShortcut)  # !
        self.addAction(self.__open_folder_action)
        self.__open_folder_action.triggered.connect(self.__open_folder)
        # QtWidgets.QShortcut(
        #     QtGui.QKeySequence(f"Ctrl+O"), self,
        #     context=QtCore.Qt.ShortcutContext.WidgetShortcut,
        #     member=lambda: print(1))
            # member=lambda: os.startfile(self.toPlainText()))

    @QtCore.pyqtSlot()
    def __open_folder(self):
        path_to_sensor = os.path.realpath(self.toPlainText())  # realpath is necessary
        from win32api import ShellExecute
        if os.path.isdir(self.toPlainText()):
            ShellExecute(0, 'explore', path_to_sensor, None, None, 1)

    def setTextCarefully(self, text):
        """Select and then insert text. Ctrl+Z works"""
        self.selectAll()
        self.insertPlainText(text)
        # self.insertHtml()

    @QtCore.pyqtSlot()
    def __textChangedHandler(self): # а если несколько путей списано?
        """Check dir existence, color thr text."""
        color = "#FFFFF1;" if os.path.isdir(self.toPlainText()) else "#ACACAC;"
        self.setStyleSheet("color: " + color)
    
    @QtCore.pyqtSlot()
    def __textEditContextMenu(self):
        """Create list with txt filenames from directory."""
        _normal_menu = self.createStandardContextMenu()
        _menu = QtWidgets.QMenu(parent=self)
        _menu.addAction(self.__open_folder_action)
        if not os.path.isdir(self.toPlainText()):
            self.__open_folder_action.setDisabled(True)
        # --- ---
        # self.__path_to_sensor = os.path.realpath(self.folder_name)
        # --- ---
        other_menu = QtWidgets.QMenu('Other', self)
        other_menu.addActions(_normal_menu.actions())
        _menu.addSeparator()
        _menu.addMenu(other_menu)
        _menu.exec(QtGui.QCursor.pos())
        _menu.deleteLater()

