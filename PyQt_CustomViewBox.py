# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

import pyqtgraph as pg
from PyQt5 import QtCore


class CustomViewBox(pg.ViewBox):
    # change_curve_visibility_signal = QtCore.pyqtSignal(int)
    def __init__(self, *args, **kwds):
        # kwds['enableMenu'] = True
        # kwds['enableMenu'] = False
        # pg.ViewBoxMenu
        pg.ViewBox.__init__(self, *args, **kwds)
        # self.setMouseMode(self.RectMode)  # 1 button mode !!!
        # menu = self.getMenu(None)  # !
        STYLE_SHEETS_FILENAME = 'res\StyleSheets.css'
        with open(STYLE_SHEETS_FILENAME, "r") as style_sheets_css_file:
            self.menu.setStyleSheet(style_sheets_css_file.read())
            # print(menu.findChildren())
            # menu.actions()[0].setParent(menu)
            # menu.actions()[1].setParent(menu)
            # menu.actions()[1].setStyleSheet(style_sheets_css_file.read())
            # menu.actions()[1].setParent(menu)
            # menu.actions()[2].setStyleSheet(style_sheets_css_file.read())
        # print(self.menu.parent())
        # print(self.parent())
        # print(self)
        # print(menu)
        # hide_1 = QtWidgets.QAction('gyro 1', self.menu, objectName="1")
        # hide_1.triggered.connect(self.change_curve_visibility_signal.emit)
        # self.menu.addAction(hide_1)

    # def contextMenuEvent(self, event):
    #     menu = self.getMenu(None)
    #     someAction = menu.addAction('New_Item')

    #     res = menu.exec()
    #     if res == someAction:
    #         print('Hello')

    def mouseDoubleClickEvent(self, e):
        if (e.buttons() & QtCore.Qt.MouseButton.LeftButton):
            self.autoRange()
            self.enableAutoRange()  # возвращает в режим автоматического масштабирования

    # def contextMenuEvent(self, event):
        # menu = self.getMenu(None)
        # print(menu)
        # gotoAction = QtWidgets.QAction('action-to-add', menu)
        # menu.insertAction(menu.actions()[0], gotoAction)
        # res = menu.exec(event.globalPos())
        # print(1)
    #  reimplement right-click to zoom out
    # def mouseClickEvent(self, ev):
    #     if ev.button() == QtCore.Qt.MouseButton.RightButton:
    #         # self.autoRange()
    #         self.enableAutoRange()  # так действительно возвращает в режим автоматического масштабирования

    # #  reimplement mouseDragEvent to disable continuous axis zoom
    # def mouseDragEvent(self, ev, axis=None):
    #     if axis is not None and ev.button() == QtCore.Qt.MouseButton.RightButton:
    #         ev.ignore()
    #     else:
    #         pg.ViewBox.mouseDragEvent(self, ev, axis=axis)
