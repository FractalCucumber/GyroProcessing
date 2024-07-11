# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

from PyQt5 import QtWidgets, QtCore, QtGui


class CustomButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super(CustomButton, self).__init__(*args, **kwargs)
        # QtWidgets.QPushButton.__init__(self, *args, **kwargs)
        # self.clicked.connect(self.animation)
        self.flag = 0

    # @QtCore.pyqtSlot()
    # def animation(self):
    #     if self.flag:
    #         print(0)
    #         return
    #     self.flag = 1
    #     rect_start = QtCore.QRect(self.geometry())
    #     rect_end = QtCore.QRect(
    #         self.x(), self.y(), rect_start.width() - 8, rect_start.height() - 4)
    #     rect_end.moveCenter(rect_start.center())
    #     anim_1 = QtCore.QPropertyAnimation(self, b'geometry')
    #     anim_1.setStartValue(rect_start)
    #     anim_1.setEndValue(rect_end)
    #     anim_1.setDuration(100)
    #     anim_2 = QtCore.QPropertyAnimation(self, b'geometry')
    #     anim_2.setStartValue(rect_end)
    #     anim_2.setEndValue(rect_start)
    #     anim_2.setDuration(100)
    #     anim_group = QtCore.QSequentialAnimationGroup(self)
    #     anim_group.addAnimation(anim_1)
    #     anim_group.addAnimation(anim_2)
    #     anim_group.start()
    #     anim_group.finished.connect(lambda: self.__setattr__("flag", 0))
    #     print(1)

    @QtCore.pyqtSlot(QtGui.QMouseEvent)
    def mousePressEvent(self, event):
        super(QtWidgets.QPushButton, self).mousePressEvent(event)
        # self.clicked
        if not self.flag:
            self.flag = 1
            rect_start = QtCore.QRect(self.geometry())
            rect_end = QtCore.QRect(
                self.x(), self.y(), rect_start.width() + 8, rect_start.height() + 4)
            rect_end.moveCenter(rect_start.center())
            anim_1 = QtCore.QPropertyAnimation(self, b'geometry')
            anim_1.setStartValue(rect_start)
            anim_1.setEndValue(rect_end)
            anim_1.setDuration(50)
            anim_2 = QtCore.QPropertyAnimation(self, b'geometry')
            anim_2.setStartValue(rect_end)
            anim_2.setEndValue(rect_start)
            anim_2.setDuration(100)
            anim_group = QtCore.QSequentialAnimationGroup(self)
            anim_group.addAnimation(anim_1)
            anim_group.addAnimation(anim_2)
            anim_group.finished.connect(lambda: self.__setattr__("flag", 0))
            anim_group.start()

