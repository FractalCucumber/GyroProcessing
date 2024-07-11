# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

from time import time, sleep, perf_counter
# import sys
import os
# import re
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from widgets.PyQt_CustomPushButton import CustomButton

from widgets.tab_widget.PyQt_CustomViewBox import CustomViewBox

from QtCustomPlot import CustomPlot
import DataBase



class PlotsMakerGroupbox(QtWidgets.QGroupBox): # plots
    progress_signal = QtCore.pyqtSignal(int)
    # можно сделать так, чтобы графики автоматически
    # (или по нажатию на кнопку) перестраивались при изменении в модели
    def __init__(self, settings=None, *args, **kwds):
        QtWidgets.QGroupBox.__init__(self, *args, **kwds)
        self.__logger = DataBase.get('Logger', None)  # !!!

        DataBase.setParams(PlotsMaker=self)  # !!!!!

        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(3, 5, 3, 3)
        # ---
        self.frame = None
        # PlotDataItem
        
        # self.CURVE_PARAMS = {'skipFiniteCheck': True, 'clipToView': True, 'useCache': False} #, 'autoDownsample': True}
        self.CURVE_PARAMS = {'skipFiniteCheck': True, 'autoDownsample': True} #, 'autoDownsample': True}
        # self.CURVE_PARAMS = {'skipFiniteCheck': True} #, 'autoDownsample': True}
        # self.CURVE_PARAMS = {}
        # ---
        self.plot_button = CustomButton('Построить')
        layout.addWidget(self.plot_button, 0, 0, 1, 1)
        self.plot_button.clicked.connect(lambda: self.process)
        # ---
        self.window_cb = QtWidgets.QCheckBox('В окне', checked=True)
        layout.addWidget(self.window_cb, 0, 1, 1, 1)
        self.window_cb.stateChanged.connect(lambda: self.change_layout(self.window_cb.isChecked()))
        # ---
        self.graphWidgetGroupBox = QtWidgets.QGroupBox('График')
        graph_layout = QtWidgets.QGridLayout(self.graphWidgetGroupBox)

        self.graphWidget = CustomPlot(viewBox=CustomViewBox())  # !!!
        # self.graphWidget.setDownsampling(False)
        graph_layout.addWidget(self.graphWidget, 0, 2, 20, 20)

        import pyqtgraph as pg
        self.singleCurveGraph = CustomPlot(viewBox=CustomViewBox(), visible=False)  # !!!
        # self.singleCurveGraph.setDownsampling(False)
        self.singleCurveGraph.plotItem.clear()
        self.singleCurveGraph.plotItem.addLegend(offset=(-1, 1), labelTextSize=f'{12}pt')
        self.singleCurveGraph.plotItem.legend.setColumnCount(2)
        self.singleCurveGraph.plotItem.plot(pen=pg.mkPen("#FF0000", width=1),
                                        name='1', **self.CURVE_PARAMS)
        self.singleCurveGraph.plotItem.plot(pen=pg.mkPen("#55FF55", width=1.75),
                                        name='2', **self.CURVE_PARAMS)
        self.singleCurveGraph.plotItem.plot(pen=pg.mkPen("#0000FF", width=1),
                                        name='3', **self.CURVE_PARAMS)
        self.singleCurveGraph.plotItem.plot(pen=pg.mkPen("#00AFAF", width=1),
                                        name='4', **self.CURVE_PARAMS)
        self.singleCurveGraph.plotItem.plot(pen=pg.mkPen("#000000", width=1),
                                        name='5', **self.CURVE_PARAMS)
        self.singleCurveGraph.plotItem.plot(
            pen=pg.mkPen("#222222", width=1.75), name='6', **self.CURVE_PARAMS)
        self.singleCurveGraph.plotItem.plot(
            pen=pg.mkPen("#0000FF", width=1.75), name='7', **self.CURVE_PARAMS)
        graph_layout.addWidget(self.singleCurveGraph, 0, 2, 20, 20)

        # --- ---
        self.multiGroupBox = QtWidgets.QGroupBox(visible=False)
        multiGroupBox_layout = QtWidgets.QGridLayout(self.multiGroupBox)
        graph_layout.addWidget(self.multiGroupBox, 0, 0, 10, 2)
        # ---
        self.btn0_3 = CustomButton('(1)')
        self.btn0_3.clicked.connect(lambda: self.shift(0))
        multiGroupBox_layout.addWidget(self.btn0_3, 0, 0, 2, 2)
        self.btn1_3 = CustomButton('(2)')
        self.btn1_3.clicked.connect(lambda: self.shift(2))
        multiGroupBox_layout.addWidget(self.btn1_3, 2, 0, 2, 2)
        self.btn2_3 = CustomButton('(3)')
        self.btn2_3.clicked.connect(lambda: self.shift(1))
        multiGroupBox_layout.addWidget(self.btn2_3, 4, 0, 2, 2)

        self.flag1 = CustomButton('hide')
        self.flag1.clicked.connect(lambda: self.change_visibility(False))
        multiGroupBox_layout.addWidget(self.flag1, 6, 0, 2, 1)
        self.flag2 = CustomButton('show')
        self.flag2.clicked.connect(lambda: self.change_visibility(True))
        multiGroupBox_layout.addWidget(self.flag2, 6, 1, 2, 1)
        # --- ---
        self.singleGroupBox = QtWidgets.QGroupBox(visible=False)
        singleGroupBox_layout = QtWidgets.QGridLayout(self.singleGroupBox)
        graph_layout.addWidget(self.singleGroupBox, 0, 0, 10, 2)
        # ---
        lbl = QtWidgets.QLabel('Индексы:')
        singleGroupBox_layout.addWidget(lbl, 1, 0, 2, 1)
        self.cb1 = QtWidgets.QComboBox()
        singleGroupBox_layout.addWidget(self.cb1, 1, 0, 2, 1)
        self.cb2 = QtWidgets.QComboBox()
        singleGroupBox_layout.addWidget(self.cb2, 1, 1, 2, 1)
        self.show_btn = CustomButton('показать')
        singleGroupBox_layout.addWidget(self.show_btn, 2, 0, 2, 1)
        self.show_btn.clicked.connect(self.show_certain)
        # ---
        self.next_btn = CustomButton('next_btn') 
        # или они должны смещать именно выбранную характеристику через комбобоксы?
        singleGroupBox_layout.addWidget(self.next_btn, 3, 0, 2, 1)
        self.next_btn.clicked.connect(lambda: self.shift_visibility(1))
        self.prev_btn = CustomButton('prev_btn')
        # или они должны смещать именно выбранную характеристику через комбобоксы?
        singleGroupBox_layout.addWidget(self.prev_btn, 3, 1, 2, 1)
        self.prev_btn.clicked.connect(lambda: self.shift_visibility(-1))
        # ---
        lbl = QtWidgets.QLabel('Окно:')
        singleGroupBox_layout.addWidget(lbl, 5, 0, 2, 1)
        self.show_spinbox = QtWidgets.QSpinBox()
        self.show_spinbox.setMaximum(10000000)
        self.show_spinbox.setValue(40)
        singleGroupBox_layout.addWidget(self.show_spinbox, 5, 1, 2, 1)
        lbl = QtWidgets.QLabel('Метод:')
        singleGroupBox_layout.addWidget(lbl, 6, 0, 2, 1)
        self.method_cb = QtWidgets.QComboBox()
        self.method_cb.addItems(['Савицкий-Голей', 'среднее'])
        singleGroupBox_layout.addWidget(self.method_cb, 6, 1, 2, 1)
        # ---
        self.smooth = CustomButton('smooth')
        singleGroupBox_layout.addWidget(self.smooth, 7, 1, 2, 1)
        self.smooth.clicked.connect(self.__smooth)
        # ---
        self.save_btn = CustomButton('save in xlsm')
        singleGroupBox_layout.addWidget(self.save_btn, 8, 0, 2, 1)
        self.save_btn.clicked.connect(self.save)
        self.cut_on_load_lbl = QtWidgets.QCheckBox('cut')
        singleGroupBox_layout.addWidget(self.cut_on_load_lbl, 9, 0, 2, 1)
        # ---
        # или они должны смещать именно выбранную характеристику через комбобоксы?
        lbl = QtWidgets.QLabel('Обрезать при загрузке:')
        singleGroupBox_layout.addWidget(lbl, 11, 0, 2, 1)
        self.cut_on_load = QtWidgets.QSpinBox()
        self.cut_on_load.setMaximum(10000000)
        self.cut_on_load.setValue(0)
        singleGroupBox_layout.addWidget(self.cut_on_load, 11, 1, 2, 1)
        # ---
        self.single = QtWidgets.QCheckBox('single')
        # или они должны смещать именно выбранную характеристику через комбобоксы?
        layout.addWidget(self.single, 0, 2, 1, 1)
        self.single.stateChanged.connect(self.switch)
        # ---
        self.setAcceptDrops(True)

        # self.graphWidgetGroupBox.setParent(self)
        layout.addWidget(self.graphWidgetGroupBox, 2, 0, 5, 5)
        self.graphWidgetGroupBox.show()

        if settings: self.restore_settings(settings)


    def save(self):
        # проверка на то, что коррекция уже есть !!!!!
        # sensor num
        plotItem = self.singleCurveGraph.plotItem
        # ---
        sensor: str = plotItem.legend.items[0][1].text # 0 - curve number
        i = 0 # i - acc or gyro
        path_to_xlsm = DataBase.get('excel lists folders')
        path = f'{path_to_xlsm}/{sensor}.xlsm'
        if not os.path.isfile(path):
            self.__logger.error(f'Не сумел отсыкать {path}')
            return False
        cell = DataBase.get('thermal correction cells')[i]
        # ---
        img_name = f'{sensor}_term_corr_{i + 1}'
        approximation = plotItem.curves[2].getData()
        DataBase.to_image(plotItem, img_name, 'png')
        # ---
        DataBase.xlsm_write(
            path, 'Настройка КП',
            [cell, DataBase.shift_coords(cell, (2, 0))],
            [img_name, approximation],
            app=None
            )
        print('save!')

    def __smooth(self):
        t = perf_counter()
        # from scipy.signal import savgol_filter
        print('perf_counter', perf_counter() - t)
        t = perf_counter()
        n = self.show_spinbox.value()
        length = len(self.singleCurveGraph.plotItem.curves[0].xData)
        xdata = self.singleCurveGraph.plotItem.curves[0].xData#[:int(length/20)]#[::200]
        ydata = self.singleCurveGraph.plotItem.curves[0].yData#[:int(length/20)]#[::200]
        # print(self.singleCurveGraph.plotItem.curves[0].xData)
        # print(self.singleCurveGraph.plotItem.curves[0].yData)
        print(xdata, ydata)
        ydata = DataBase.smooth_data(ydata, n=n, type='savgol', polyorder=3)
        # ydata = savgol_filter(ydata, window_length=int(n), polyorder=3)
        # filter = np.ones(int(n), dtype=np.float32) / int(n)
        # ydata = np.convolve(ydata, filter, mode='same')
        filtered_ydata = np.copy(ydata)#[::200]
        self.singleCurveGraph.plotItem.curves[1].setData(
            xdata, filtered_ydata, **self.CURVE_PARAMS)

        # filter = np.ones(int(n/4), dtype=np.float32) / int(n/4)
        # ydata = np.convolve(ydata, filter, mode='same')
        # # self.graphWidget2.plotItem.curves[2].setData(xdata, ydata)

        # filter = np.ones(int(n/4), dtype=np.float32) / int(n/4)
        # ydata = np.convolve(ydata, filter, mode='same')

        # filter = np.ones(int(n/8), dtype=np.float32) / int(n/8)
        # ydata = np.convolve(ydata, filter, mode='same')

        # self.singleCurveGraph.plotItem.curves[2].setData(xdata, ydata)
        # d = np.diff(ydata) * 50
        # filter = np.ones(int(n/8), dtype=np.float32) / int(n/8)
        # d = np.convolve(d, filter, mode='same')
        # self.singleCurveGraph.plotItem.curves[3].setData(xdata[:-1], d)
        # # self.graphWidget2.plotItem.curves[3].setData(xdata[:-2], np.diff(d))
        # # filter = np.ones(int(n/10), dtype=np.float32) / int(n/10)
        # # d = np.convolve(d, filter, mode='same')
        # __d2 = np.diff(d)
        # self.singleCurveGraph.plotItem.curves[3].setData(xdata[:-2], __d2 * 10)
        # filter = np.ones(int(n/8), dtype=np.float32) / int(n/8)
        # __d2 = np.convolve(__d2, filter, mode='same')

        # self.singleCurveGraph.plotItem.curves[4].setData(xdata[:-2], __d2 * 10)

        # d2 = np.abs(__d2)

        # average = np.median(d2)
        # print('average', average)
        # print('max', np.max(d2)); print('min', np.min(d2))
        # d2_extr = np.where(
        #     (d2[1:-2] > d2[0:-3]) & (d2[1:-2] > d2[2:-1]) 
        #     )[0] + 1

        # d2_extr_new = d2_extr[np.where(
        #     (d2[d2_extr] > average * 1) #.25)
        #     )[0]]

        # # d2_extr_new1 = d2_extr[np.where(
        # #     (((d2_extr)[:-1] - (d2_extr)[1:] < 5) & (d2[d2_extr[:-1]] > d2[d2_extr[1:]]) & (d2[d2_extr[:-1]] * d2[d2_extr[1:]] > 0))
        # #     )[0]]
        # # d2_extr_new = d2_extr[np.where(
        # #     (np.diff(d2_extr) > 4)
        # #     )[0]]
        # # print('d2_extr', d2_extr)
        # # print('d2_extr_new', d2_extr_new)
        # # print('d2_extr_new1', d2_extr_new1)
        
        # print('\n len(d2_extr) !!! :', len(d2_extr), '\n')
        # print('\n len(d2_extr_new) !!! :', len(d2_extr_new), '\n')
        # optimize = np.abs(d2[d2_extr_new]) # то, что ранжируем optimize
        # # print('\n optimize', optimize)
        # # optimize = optimize[:-1] * np.diff(d2_extr_new) # то, что ранжируем optimize
        # # print('\n optimize', optimize)
        # d2_extr_new2 = np.argsort(-optimize)[:95]
        # d2_extr_new2 = np.sort(d2_extr_new2)
        # d2_extr_new__ = d2_extr_new[d2_extr_new2]
        # # print('\n ydata[d2_extr_new]', ydata[d2_extr_new])
        # # print('\n d2_extr_new__', d2_extr_new__)
        # # print('\n d2_extr_new', d2_extr_new)
        # # print('\n d2_extr_new2', d2_extr_new2)
        # self.singleCurveGraph.plotItem.curves[5].setData(xdata[d2_extr_new__], ydata[d2_extr_new__])
        # self.singleCurveGraph.plotItem.curves[6].setData(xdata[d2_extr_new], ydata[d2_extr_new])

        # res = np.interp(xdata, xdata[d2_extr_new__], filtered_ydata[d2_extr_new__])
        # error = np.max(np.abs(res - filtered_ydata))
        # print(error)
        # print('perf_counter', perf_counter() - t)

        t = perf_counter()
        _extr = [0, xdata.shape[0] - 1]
        _extr2 = [0, xdata.shape[0] - 1]
        _extr222 = [0, 0]
        print(_extr)
        # print(filtered_ydata[0]); print(filtered_ydata[1], '\n')
        # y_points = xdata[_extr].tolist()
        for n in range(1, 94):
            res = np.interp(xdata, xdata[_extr], filtered_ydata[_extr])
            err_arr = res - filtered_ydata
            error_ind = np.argmax(np.abs(err_arr))
            _extr.append(error_ind)
            # y_points.append(xdata[_extr][-1])
            if err_arr[error_ind] > 0: _extr222.append(1)
            else: _extr222.append(-1)
            _extr2.append(error_ind)
            _extr.sort()
            print(error_ind, err_arr[error_ind], _extr2[-1], _extr222[-1])
        ind = np.array(_extr2).argsort()
        _extr2 = np.array(_extr2)[ind]
        _extr222 = np.array(_extr222)[ind]
        self.singleCurveGraph.plotItem.curves[5].setData(
            xdata[_extr], ydata[_extr], **self.CURVE_PARAMS)
        print('perf_counter 2:', perf_counter() - t)
        # print(_extr)
        print('len ', len(_extr), '\n\n')
        
        max_min = err_arr[error_ind]

        # t = perf_counter()
        # _extr2 = [0, 0]
        # print(_extr)
        # # print(filtered_ydata[0]); print(filtered_ydata[1], '\n')
        # # y_points = xdata[_extr].tolist()
        # for n in range(1, 94):
        #     res = np.interp(xdata, xdata[_extr2], filtered_ydata[_extr2])
        #     err_arr = res - filtered_ydata
        #     if err_arr[_extr[n]] > 0: _extr2.append(1)
        #     else: _extr2.append(-1)
        #     error_ind = np.argmax(err_arr)
        #     _extr2.append(error_ind)
        #     # y_points.append(xdata[_extr][-1])
        #     _extr2.sort()
        #     print(error_ind, err_arr[error_ind])
        # self.singleCurveGraph.plotItem.curves[4].setData(xdata[_extr2], ydata[_extr2])
        # print('perf_counter 2:', perf_counter() - t)
        # # print(_extr)
        # print('len ', len(_extr2), '\n\n')
        # err_arr2 = res - filtered_ydata
        res = np.interp(xdata,
            xdata[_extr],
            filtered_ydata[_extr] + (_extr222 > 0).astype(np.float32) * 2 * max_min / 3 - max_min / 3)
        self.singleCurveGraph.plotItem.curves[4].setData(
            xdata[_extr],
            ydata[_extr] + (_extr222 > 0).astype(np.float32) * 2 * max_min / 3 - max_min / 3,
            **self.CURVE_PARAMS)
        err_arr = np.abs(res - filtered_ydata)
        print(_extr222)
        print(_extr222 > 0)
        print(-(_extr222 > 0).astype(np.float32) * 2 * max_min / 3 - max_min / 3)
        # print(err_arr[_extr])
        # print((err_arr2[np.array(_extr)[1:-1] + 1] > 0).astype(np.float32) * err_arr[error_ind] / 2)
        # print((err_arr2[np.array(_extr)[1:-1] + 1] <= 0).astype(np.float32) * err_arr[error_ind] / 2)
        print(np.max(err_arr))

        # diff2_extr1 = np.insert(d2_extr, 0, 0)
        # diff2_extr1 = diff2_extr1[np.where(
        #     (np.diff(diff2_extr1) > 5)
        #     )[0]]
        # print('diff2_extr 1:', diff2_extr1)
        # diff2_extr2 = np.insert(d2_extr, d2_extr.size, len(d2) - 1)
        # diff2_extr2 = diff2_extr2[np.where(
        #     (np.diff(diff2_extr2) > 5)
        #     )[0]]
        # print('diff2_extr 2:', diff2_extr2)
        # d2_extr.reshape(d2_extr)

    def switch(self):
        res = self.single.isChecked()
        self.singleCurveGraph.setVisible(res) 
        self.singleGroupBox.setVisible(res) 
        self.multiGroupBox.setVisible(not res) 
        self.graphWidget.setVisible(not res) 

    def process(self, txt_files=None): # добавить moveToThread
        t_0 = perf_counter()
        self.progress_signal.emit(0)
        QtWidgets.QApplication.setOverrideCursor(
            QtCore.Qt.CursorShape.BusyCursor)
        if not txt_files:
            DataBase.getParams('sensors')  # !!!
            if not txt_files:
                self.__logger.warning('Сожалею, но для вызова функции не хватает параметров')  # !!!
                return
            
        import pyqtgraph as pg
        import numpy as np
        self.frame = None
        frames: np.ndarray = np.ndarray(shape=(0, 1))
        last = 0
        for txt_file in txt_files:
            t0 = perf_counter()
            if int(self.cut_on_load.value()) > 0:
                frame = DataBase.txt_reader(txt_file, skiprows=int(self.cut_on_load.value()))
            else:
                frame = DataBase.txt_reader(txt_file)
            print(frame.shape)
            self.frame = frame.to_numpy()
            print(self.frame.dtype)
            print(self.frame.shape)
            self.frame[:, 0] += last
            last = self.frame[-1, 0]
            rows = frames.shape[0]
            if len(txt_files) > 1:
                frames.resize((rows + self.frame.shape[0], self.frame.shape[1]), refcheck=False)
                frames[rows:, :] = self.frame
            self.__logger.info(f'frames.shape: {frames.shape}, {self.frame.shape}')
            # print(f'frames.shape: {frames.shape}')
            print(f'only read time! {txt_file}', perf_counter() - t0)
        if len(txt_files) > 1:
            self.frame = frames # !!!!


        t1 = perf_counter()

        if len(self.graphWidget.plotItem.curves) != self.frame.shape[1]:
            items_names = []
            items_names.append('Time')
            names = [':A', ':G', ':T']
            for i in range(1, self.frame.shape[1]):
                items_names.append(f'{(i + 2) // 3}{names[(i - 1) % 3]}')
            self.cb1.clear()  # на 1 больше будет!
            self.cb1.addItems(items_names)
            self.cb2.clear()
            self.cb2.addItems(items_names)
            # потом добавить управление для этих штук
        
            self.graphWidget.plotItem.clear()
            self.graphWidget.plotItem.showGrid(x=True, y=True)
            self.graphWidget.plotItem.addLegend(offset=(-1, 1), labelTextSize=f'{10}pt',
                                                labelTextColor=pg.mkColor('#000000'))
            self.graphWidget.plotItem.legend.setColumnCount(3)
            step = int((255) / self.frame.shape[1]) * 1
            colors = ['', '', '']
            for i in range(1, self.frame.shape[1]):
                for j, k in enumerate([i * step, 107 + i * step, 215 - i * step]):
                    colors[j] = ('0' + str(hex(k % 255)[2:]))[-2:]
                    # colors[j] = ('0' + str(hex(k % 215 + 20)[2:]))[-2:]
                pen = pg.mkPen(
                    f"#{''.join(colors)}", dash=[6, 1 * (i % 4)],
                    # f'#{color1[-2:]}{color2[-2:]}{color3[-2:]}',dash=[6, 1 * (i % 4)],
                    width=(0.5 + 0.5 * i % 2)
                    )
                std = np.std(self.frame[:, i])
                if std > 10:
                    std = f'{std:.0f}'
                elif std > 1:
                    std = f'{std:.1f}'
                else:
                    std = f'{std:.2f}'.rstrip('0').rstrip('.')
                mean = np.mean(self.frame[:, i])
                if np.abs(mean) > 100:
                    mean = f'{np.mean(self.frame[:, i]):.0f}'
                elif np.abs(mean) > 10:
                    mean = f'{np.mean(self.frame[:, i]):.1f}'
                else:
                    mean = f'{np.mean(self.frame[:, i]):.2f}'.rstrip('0').rstrip('.')
                self.graphWidget.plotItem.plot(pen=pen,
                                               name=f'{items_names[i]},std:{std},mean:{mean}'
                                               )
        # self.graphWidget.plotItem.curves[0].setVisible(True)
        for i, curve in enumerate(self.graphWidget.plotItem.curves):
            curve.setVisible(i == 0)
        # for i in range(0, int(self.frame.shape[1] / 2) - 1):
        for i in range(0, self.frame.shape[1] - 1):
            self.graphWidget.plotItem.curves[i].setData(
                self.frame[:, 0], self.frame[:, i + 1], **self.CURVE_PARAMS)
        # self.__logger.error('Тут временный костыль')
        # self.graphWidgetGroupBox.show()
        print('with reading', perf_counter() - t0)
        print('without reading', perf_counter() - t1)

        QtWidgets.QApplication.restoreOverrideCursor()
        self.progress_signal.emit(100)
        self.__logger.info(f'Full time: {perf_counter() - t_0}, size: {self.frame.shape}')
        self.frame = None ###############################################################

# --- ------------------------------------------------------------------------------------
    def change_layout(self, flag):
        if flag:
            self.graphWidgetGroupBox.hide()
            self.graphWidgetGroupBox.setParent(self)
            self.layout().addWidget(self.graphWidgetGroupBox, 2, 0, 5, 5)
            self.graphWidgetGroupBox.show()
        else:
            self.graphWidgetGroupBox.hide()
            self.graphWidgetGroupBox.setParent(None)
            self.layout().removeWidget(self.graphWidgetGroupBox)
            self.graphWidgetGroupBox.show()

    def show_certain(self):
        # i = self.show_spinbox.value()
        # try:
        #     self.graphWidget.plotItem.curves[i].setVisible(True)
        # except IndexError:
        #     return
        # if hasattr(self, 'frame') and not self.frame is None:
        #     self.graphWidget.plotItem.curves[i].setData(
        #         self.frame[:, self.cb1.currentIndex()],
        #         self.frame[:, self.cb2.currentIndex()]
        #     )
        # else:
        #     self.__logger.info(f'No loaded data!')

        try:
            self.singleCurveGraph.plotItem.curves[0].setVisible(True)
        except IndexError:
            print('error')
            return
        print(hasattr(self, 'frame') and not self.frame is None)
        print(self.cb1.currentIndex(), self.cb2.currentIndex())
        # print(self.frame[:, self.cb1.currentIndex()])
        # print(self.frame[:, self.cb2.currentIndex()])
        # if hasattr(self, 'frame') and not self.frame is None:
        if True:
            t = perf_counter()
            if self.cb1.currentIndex() == 0:
                xData = self.graphWidget.plotItem.curves[0].xData
            else:
                xData = self.graphWidget.plotItem.curves[self.cb1.currentIndex() - 1].yData
            if self.cb2.currentIndex() == 0:
                yData = self.graphWidget.plotItem.curves[0].xData
            else:
                yData = self.graphWidget.plotItem.curves[self.cb2.currentIndex() - 1].yData
            # args = np.argsort(xData)
            # xData = xData[args]
            # yData = yData[args]
            # ununique = np.where(np.diff(xData) != 0)[0] + 1
            # ununique = np.insert(ununique, 0, 0)
            # ununique__ = np.copy(ununique)
            # ununique = np.insert(ununique, ununique.size, xData.size)
            # print(ununique)
            # d_unique = np.diff(ununique)
            # print(d_unique)
            # sort_yData = np.ndarray(shape=(len(ununique) - 1))
            # for i in range(ununique.size - 1):
            #     # print(ununique[i],ununique[i+1],d_unique[i])
            #     sort_yData[i] = np.sum(yData[ununique[i]:ununique[i+1]]) / d_unique[i]
            # sort_xData = xData[ununique__]
            # print(len(xData[ununique - 1]))
            # print(len(sort_yData))
            # print(len(ununique))
            # print('t = ', perf_counter() - t)
            sort_xData, sort_yData = DataBase.clear_repeats(xData, yData)
            # print(self.singleCurveGraph.plotItem.curves[0]) #PlotCurveItem PlotDataItem.PlotDataItem
            self.singleCurveGraph.plotItem.curves[0].setData(
                sort_xData, sort_yData, **self.CURVE_PARAMS)
            # self.singleCurveGraph.plotItem.curves[0].xData = sort_xData.view(np.ndarray)
            # self.singleCurveGraph.plotItem.curves[0].yData = sort_yData.view(np.ndarray)
            # self.singleCurveGraph.plotItem.curves[0].update()
            # self.graphWidget2.plotItem.curves[0].setData(
            #     self.frame[:, self.cb1.currentIndex()],
            #     self.frame[:, self.cb2.currentIndex()]
            # )
        else:
            self.__logger.info(f'No loaded data!')
        print(self.singleCurveGraph.plotItem.curves[0].xData)
        print(self.singleCurveGraph.plotItem.curves[0].yData)
        print(self.singleCurveGraph.plotItem.curves[0].isVisible())

        # if self.cb1.currentIndex() > 0:
            # x = self.graphWidget.plotItem.curves[self.cb1.currentIndex() - 1].yData
            
        QtCore.QCoreApplication.processEvents()
        self.graphWidget.autoRange()   

    def shift_visibility(self, n):
        if n > 0:
            flag = False
            for curve in self.graphWidget.plotItem.curves:
                if flag and not curve.isVisible():
                    curve.setVisible(True)
                    flag = False
                elif curve.isVisible():
                    curve.setVisible(False)
                    flag = True
        else:
            flag = None
            for curve in self.graphWidget.plotItem.curves:
                if curve.isVisible():
                    curve.setVisible(False)
                    if not flag is None and not flag.isVisible():
                        flag.setVisible(True)
                flag = curve
        QtCore.QCoreApplication.processEvents()
        self.graphWidget.autoRange()   

    def change_visibility(self, flag):
        t_0 = perf_counter()
        for curve in self.graphWidget.plotItem.curves:
            curve.setVisible(flag)
            if flag:
                QtCore.QCoreApplication.processEvents()
            if perf_counter() - t_0 > 3:
                self.__logger.warning(f'Слишком много точек, остановись...')
                break
    
        self.graphWidget.autoRange()   
        # QtCore.QCoreApplication.processEvents()
        self.__logger.info(f'Full time :{perf_counter() - t_0}')

    def shift(self, n=0):
        t_0 = perf_counter()
        for i, curve in enumerate(self.graphWidget.plotItem.curves):
            curve.setVisible((n + i) % 3 == 0) 
        self.graphWidget.autoRange()   
        QtCore.QCoreApplication.processEvents()
        self.__logger.info(f'Full time :{perf_counter() - t_0}')


# --- ------------------------------------------------------------------------------------

    @QtCore.pyqtSlot(QtGui.QDropEvent)
    def dragEnterEvent(self, event: QtGui.QDropEvent):
        if event.mimeData().hasUrls():
            # print(event.mimeData().)
            # action = QtWidgets.QAction('AAAAA', self)
            # action.triggered.connect(lambda: print(213))
            # event.setDropAction(QtCore.Qt.DropAction(action))
            event.setDropAction(QtCore.Qt.DropAction.CopyAction)
            event.accept()
            # event.acceptProposedAction()

    @QtCore.pyqtSlot(QtGui.QDropEvent)
    def dropEvent(self, event: QtGui.QDropEvent):
        # print(event.mimeData().data())
        if not event.mimeData().hasUrls():
            return
        files_to_plot: list[str] = []
        for url in event.mimeData().urls():
            _, ext = os.path.splitext(url.toLocalFile())
            if ext != '.txt':
                continue
            files_to_plot.append(url.toLocalFile())
        if len(files_to_plot):
            self.process(txt_files=files_to_plot)

    def get_current_setting(self):
        """dict name: 'plot settings'"""
        dict = {
            'mode flag': self.single.isChecked(),
            'in window flag': self.window_cb.isChecked()
            }
        common_dict = DataBase.get('__dict_with_app_settings')
        common_dict['plot settings'] = dict
        DataBase.setParams(__dict_with_app_settings=common_dict)
        return True

    def restore_settings(self, dict: dict):
        """dict name: 'plot settings'"""
        if res := dict.get('mode flag', True):
            self.single.setChecked(res)
            self.switch()
        if res := dict.get('in window flag', True):
            self.window_cb.setChecked(res)
            self.change_layout(self.window_cb.isChecked())
        return True
