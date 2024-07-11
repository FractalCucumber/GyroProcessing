from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QComboBox
import re
from PyQt5.QtWidgets import QAction
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtSerialPort import QSerialPort
from time import sleep


class CustomComboBox(QComboBox):
    def __init__(self,
                 settings: QtCore.QSettings,
                 name: str = 'default',
                 default_items_list=None,
                 editable_flag=True,
                 uint_validator_enable=True,
                 parent=None, **opts):
        super(CustomComboBox, self).__init__(parent, **opts)
        self.name = name
        self.setEditable(True)
        self.lineEdit().setReadOnly(not editable_flag)
        self.lineEdit().setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)
        if uint_validator_enable:
            self.int_validator = QtGui.QIntValidator(bottom=0)
            self.setValidator(self.int_validator)

        self.currentTextChanged.connect(
            lambda value: self.setItemText(self.currentIndex(), value))

        self.settings = settings
        if self.settings.contains(self.name + "_item"):
            for i in range(self.count()):
                self.removeItem(i)
            self.addItems(
                self.settings.value(self.name + "_item"))
        else:
            if not default_items_list:
                return
            self.addItems(default_items_list)
        if self.settings.contains(self.name + "_curr_index"):
            if self.count() >= int(self.settings.value(self.name + "_curr_index")):
                self.setCurrentIndex(
                    int(self.settings.value(self.name + "_curr_index")))

    def get_ind(self):
        if not self.settings.contains(self.name + "_name"):
            return
        index = self.findText(
            self.settings.value(self.name + "_name"))
        if index >= 0:
            self.setCurrentIndex(index)
        elif self.count():
            self.setCurrentIndex(0)

    def save_all(self):
        self.save_value()
        self.save_index()

    def save_value(self):
        if not self.count():
            return
        self.settings.setValue(
            self.name + "_item",
            [self.itemText(i) for i in range(self.count())])

    def save_index(self):
        if not self.count():
            return
        self.settings.setValue(
            self.name + "_curr_index", self.currentIndex())

    def save_current_text(self):
        if not self.count():
            return
        self.settings.setValue(
            self.name + "_name", self.currentText())

# ----------------------------------------------------------------------------------------
#
##########################################################################################
#
# ----------------------------------------------------------------------------------------


class CustomBaudRateComboBox(CustomComboBox):
    def __init__(self,
                 settings: QtCore.QSettings,
                 settings_name: str = 'Default',
                 default_items_list = [''],
                 editable_flag=True,
                 uint_validator_enable=True,
                 logger=None):
        CustomComboBox.__init__(self,
            settings, settings_name, default_items_list,
            editable_flag, uint_validator_enable)
        self.logger = logger
        self.get_available_com()
        self.get_ind()
        self.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenu)
        # self.update_com_list_action = QAction("Update COM list", self)
        self.find_port_with_data_action = QAction("Найти COM с данными", self)
        self.find_port_with_data_action.setShortcut("Ctrl+F")
        self.find_port_with_data_action.triggered.connect(self.find_port_with_data)
        self.update_com_list_action = QAction("Обновить COM", self)
        self.update_com_list_action.setShortcut("Ctrl+U")
        self.update_com_list_action.triggered.connect(self.get_available_com)
        
    @QtCore.pyqtSlot()
    def __contextMenu(self):
        _normal_menu = self.lineEdit().createStandardContextMenu()
        # self._normalMenu = QtWidgets.QMenu()
        # self._normalMenu = self.combo_box_name.layoutDirection().createStandardContextMenu()
        _normal_menu.addSeparator()
        _normal_menu.addAction(self.update_com_list_action)
        _normal_menu.addAction(self.find_port_with_data_action)
        _normal_menu.exec(QtGui.QCursor.pos())
        _normal_menu.deleteLater()

    # def disconnect():
    #     def disconnect_decorator(func):
    #         def _wrapper(*args, **kwargs):
    #             # print(args[0], " | ", kwargs, '\n')
    #             # print("sender ", args[0].sender())
    #             # print("find_port_with_data ", func)
    #             # args[0].sender().triggered.disconnect(func)
    #             func(*args, **kwargs)
    #             # args[0].sender().triggered.connect(func)
    #         return _wrapper
    #     return disconnect_decorator

    # @disconnect()
    @QtCore.pyqtSlot()
    def find_port_with_data(self):  # сделать так, чтобы уже выбранный порт не сбрасывался
        self.find_port_with_data_action.triggered.disconnect(self.find_port_with_data)
        from PyQt5.QtWidgets import QMessageBox, QApplication
        serial_port = QSerialPort(dataBits=QSerialPort.DataBits.Data8,
                                       stopBits=QSerialPort.StopBits.OneStop,
                                       parity=QSerialPort.Parity.NoParity)
        serial_port.setBaudRate(115200)
        port_names = [ports.portName() for ports in QSerialPortInfo.availablePorts()]
        if not len(port_names):
            if self.logger:
                self.logger.warning('No COM ports available')
            return
        # QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        QApplication.setOverrideCursor(QtCore.Qt.CursorShape.BusyCursor)
        port_names = sorted(port_names, key=self.natural_keys)
        self.clear()
        self.addItems(port_names)
        if self.logger:
            self.logger.info('Check COM ports...')
        flag = False
        for i, name in enumerate(port_names):
            serial_port.setPortName(name)
            if not serial_port.open(QtCore.QIODevice.OpenModeFlag.ReadWrite):
                port_names[i] += ": can't open"
                continue
            serial_port.clear()
            sleep(0.1)
            QtCore.QCoreApplication.processEvents()
            if serial_port.bytesAvailable():
                port_names[i] += f": receive data!"
                # port_names[i] += f": receive data! ({serial_port.bytesAvailable()} bytes in 100 ms)"
                self.setCurrentIndex(i)
                flag = True
                if self.logger:
                    self.logger.info(f'Receive data from {name}!')
            else:
                port_names[i] += ": no data"
            serial_port.close()
        if not flag:
            if self.logger:
                self.logger.warning(f'No ports with data!')
        text = "Search results:\n\n" + '\n'.join(port_names)
        QApplication.restoreOverrideCursor()
        QMessageBox.information(self, "Results", text)
        self.find_port_with_data_action.triggered.connect(self.find_port_with_data)

    @QtCore.pyqtSlot()
    def get_available_com(self):  # сделать так, чтобы уже выбранный порт не сбрасывался
        """Append available COM ports names to combo box widget."""
        port_names = [ports.portName() 
               for ports in QSerialPortInfo.availablePorts()]
        if not len(port_names):
            if self.logger:
                self.logger.warning('No COM ports available')
            return False
        self.clear()
        self.addItems(sorted(port_names, key=self.natural_keys))
        if self.logger:
            self.logger.info('Update available COM port list')
        return True

    @staticmethod
    def natural_keys(text: str):
        """Sort string with numbers."""
        def atoi(text: str):
            return int(text) if text.isdigit() else text
        return [atoi(c) for c in re.split(r'(\d+)', text)]
   
