# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

from PyQt5 import QtCore
import pyqtgraph as pg


class CustomPlot(pg.PlotWidget):
    def __init__(self, **kwds):
        # --- set pg options ---
        # Unloads CPU, provide x2-x3 speed up
        # pg.setConfigOption('useOpenGL', True)  # works better in my PC
        pg.setConfigOption('useOpenGL', False)  # 
        # вроде при использовании useOpenGL растет потребление памяти
        pg.setConfigOption('background', '#CCCCCC')  # '#151515'
        pg.setConfigOption('foreground', '#151515')  # '#CCCCCC'
        # pg.setConfigOption('weaveDebug', True) # вроде может ускорить
        pg.setConfigOption('crashWarning', True)
        pg.setConfigOption('mouseRateLimit', 24)
        pg.PlotWidget.__init__(self, **kwds)
        # pg.setConfigOption('leftButtonPan', True)
        # --- ---
        # self.graphWidget = pg.PlotWidget(viewBox=CustomViewBox())
        # menu = self.plotItem.legend
        # self.chan
        self.plotItem.showGrid(x=True, y=True)
        menu = self.plotItem.vb.menu
        for act in menu.actions():
            if act.text() != 'View All':
                continue
            self.addAction(act)
            act.setShortcut("Ctrl+Shift+A")
            act.triggered.connect(self.__auto_range_enable)
            act.setShortcutContext(QtCore.Qt.ShortcutContext.WidgetShortcut)
            break

    @QtCore.pyqtSlot()
    def mouseClickEvent(self, event):
        print('plot mouseClickEvent', type(event))
        # if event.button() == QtCore.Qt.MouseButton.LeftButton:
        #     visible = self.item.isVisible()
        #     self.item.setVisible(not visible)

        # event.accept()
        # self.update()

    @QtCore.pyqtSlot()
    def __auto_range_enable(self):
        self.autoRange()
        self.enableAutoRange()