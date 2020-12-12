#!/usr/bin/env python3
"""
This file should be used to run PyPLANE from the project folder while testing.
eg. `python3 ./run`

It is also to be used to build the Windows binary
ie. `pyinstaller.exe --onefile --noconsole .\run`
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyPLANE.ui_main_window import MainWindow

print(os.getcwd())

app = QApplication(sys.argv)
app_main_window = MainWindow()
app.setWindowIcon(QIcon("snap/gui/pyplane.png"))
sys.exit(app.exec())
