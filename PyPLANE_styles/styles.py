# CSS to generate the styles

default_light = """
QWidget {
  background-color: #cbdce5;
  padding: 0px;
  color:  black;
  selection-background-color: pink;
  selection-color: green;
}

QLineEdit {
  color: black;
  border: 2px solid #2C5E84;
  border-radius: 5px;
  background-color: white;
}

/* The only button in PyPLANE (so far) is the big red plot button */

QPushButton {
  background-color: darkred;
  border: 1px solid grey;
  color: white;
  border-radius: 4px;
  padding: 3px;
  min-width: 80px;
}

QPushButton:hover {
  background-color: red;
  border: 1px solid grey;
  color: white;
  border-radius: 4px;
  padding: 3px;
  min-width: 80px;
}
"""
