#!/usr/bin/env python3
"""
This is used to execute PyPLANE from the snap package
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyPLANE.ui_main_window import MainWindow

app = QApplication(sys.argv)
app_main_window = MainWindow()
app.setWindowIcon(QIcon("/snap/pyplane/current/meta/gui/pyplane.png"))
sys.exit(app.exec())
