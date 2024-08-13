from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import os

from app import MainWindow

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'k4g.beckySuite.products'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

basedir = os.path.dirname(__file__)


if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(os.path.join(basedir, 'calendar_icon.ico')))
    window = MainWindow()
    window.show()
    app.exec()
