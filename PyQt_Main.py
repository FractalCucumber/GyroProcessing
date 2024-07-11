# cSpell:includeRegExp #.*
# cSpell:includeRegExp /(["]{3}|[']{3})[^\1]*?\1/g

# pyinstaller PyQt_ApplicationOnefolder.spec 
# C:\Users\zinkevichav\AppData\Roaming\Code\User\settings.json - настройки проверки орфографии
# C:/Users/al-zi/AppData/Local/Programs/Python/Python310/python.exe d:/Work/Gyro2023_Git/PyQt_Main.py GYRO_NUMBER=3 AMP_LOG10_FLAG=0 FILE_LOG_FLAG=0
# C:/Users/zinkevichav/AppData/Local/Programs/Python/Python36/python.exe d:/GyroVibroTest/PyQt_Main.py settings=new_config.ini
# import qdarkstyle

# def enable_dark_mode(app, state=True):
#     """Enable or disable dark mode."""
#     if state:
#         app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
#     else:
#         app.setStyleSheet(qdarkstyle.load_stylesheet(palette=qdarkstyle.LightPalette))
#         # self.setStyleSheet(self.default_style_sheet)

if __name__ == "__main__":
    # from time import time, perf_counter
    from time import perf_counter
    t0 = perf_counter()
    from PyQt5.QtWinExtras import QtWin
    appid = 'GyroProcessing'
    QtWin.setCurrentProcessExplicitAppUserModelID(appid)
    # нужно для того, чтобы иконку приложения можно было менять.
    # иначе, если запускать через ярлык, то ее смена не будет работать
    from PyQt5 import QtWidgets, QtGui #, QtCore
    import sys
    from os import path
    # from PyQt_Functions import get_res_path
    t_1 = perf_counter() - t0
    def get_res_path(relative_path: str):   
        """Get absolute path to resource, works with PyInstaller."""
        base_path = getattr(
            sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
        return path.join(base_path, relative_path)
    app = QtWidgets.QApplication(sys.argv)
    # app.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)

    # enable_dark_mode(app, False)
    # app.setStyleSheet(
        # qdarkstyle.load_stylesheet(palette=qdarkstyle.DarkPalette))
        # qdarkstyle.load_stylesheet(palette=qdarkstyle.LightPalette))
    splash = QtWidgets.QSplashScreen(
        QtGui.QPixmap(get_res_path('res/load_icon.png')))
    t_2 = perf_counter() - t0
    splash.show()
    # app.processEvents()
    t1 = perf_counter() - t0
    # Test = True
    # Test = False
    # if Test:
        # from PyQt_ApplicationClassTest import AppWindowTest as AppWindow
    # else:
    from PyQt_AppClass import AppWindow
    t2 = perf_counter() - t0
    window = AppWindow(args=sys.argv)
    window.logger.debug(f"sys.argv: {sys.argv}")
    window.logger.debug(f"pre import time: {t_1:.4f} sec")
    window.logger.debug(f"pre import time 2: {t_2:.4} sec")
    window.logger.debug(f"+ QSplashScreen load time: {t1:.4} sec")
    window.logger.debug(f"+ import time: {t2:.4} sec")
    window.logger.debug(f"total load time: {perf_counter() - t0:.4f} sec")
    splash.finish(window)
    # app.restoreOverrideCursor()
    sys.exit(app.exec())

