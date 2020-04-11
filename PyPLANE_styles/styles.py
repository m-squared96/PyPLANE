# CSS to generate the styles

default_light = """
QWidget {
  background-color: #cbdce5;
  padding: 0px;
  color: #2C5E84;
  selection-background-color: #187388;
  selection-color: #FAEDD2;
}

QLineEdit {
  border: 2px solid #2C5E84;
  border-radius: 5px;
  background-color: white;
}

/* Multiple stages of buttons */

QPushButton {
  background-color: darkred;
  border: 2px solid #2C5E84;
  color: white;
  border-radius: 4px;
  padding: 3px;
  min-width: 80px;
}

QPushButton:hover {
  background-color: red;
}

QPushButton:pressed {
  background-color: #2C5E84;
}

/* Menu bar (mostly fixes) */

QMenuBar {
  padding: 2px; 
}

QMenuBar::item {
  padding: 5px;
}

QMenuBar::item:selected {
  border: 2px solid #2C5E84;
}

QMenuBar::item:pressed {
  border: 2px solid #cbdce5;
  color: #cbdce5;
  background-color: #2C5E84;
}

"""
