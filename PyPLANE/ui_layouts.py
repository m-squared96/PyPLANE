from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QLabel,
)

class EquationEntryLayout(QHBoxLayout):
    def __init__(self, dep_var, equation_rhs):
        QHBoxLayout.__init__(self)
        self.dep_var = dep_var
        self.eqn_rhs_line_edit = QLineEdit(equation_rhs)
        self.addWidget(QLabel(dep_var + "' ="))
        self.addWidget(self.eqn_rhs_line_edit)

    def text(self):
        return self.eqn_rhs_line_edit.text()

    def set_text(self, text):
        self.eqn_rhs_line_edit.setText(text)

    def clear(self):
        self.eqn_rhs_line_edit.clear()


class ParameterEntryLayout(QHBoxLayout):
    def __init__(self, param_name="", param_val=""):
        QHBoxLayout.__init__(self)
        self.param_name_line_edit = QLineEdit(param_name)
        self.param_val_line_edit = QLineEdit(str(param_val))

        self.addWidget(self.param_name_line_edit)
        self.addWidget(QLabel("="))
        self.addWidget(self.param_val_line_edit)

    def param_name_text(self):
        return self.param_name_line_edit.text()

    def param_val_text(self):
        return self.param_val_line_edit.text()

    def set_param_name_text(self, name):
        self.param_name_line_edit.setText(name)

    def set_param_val_text(self, val):
        self.param_val_line_edit.setText(str(val))

    def set_name_val_text(self, name, val):
        self.set_param_name_text(name)
        self.set_param_val_text(str(val))

    def clear(self):
        self.param_name_line_edit.clear()
        self.param_val_line_edit.clear()


class AxisLimitEntryLayout(QHBoxLayout):
    def __init__(self, var_name, var_min_val, var_max_val):
        QHBoxLayout.__init__(self)
        self.var_name = var_name
        self.min_val_line_edit = QLineEdit(str(var_min_val))
        self.max_val_line_edit = QLineEdit(str(var_max_val))

        self.addWidget(QLabel(f"Max {var_name} ="))
        self.addWidget(self.max_val_line_edit)
        self.addWidget(QLabel(f"Min {var_name} ="))
        self.addWidget(self.min_val_line_edit)

    def max_val_text(self):
        return self.max_val_line_edit.text()

    def min_val_text(self):
        return self.min_val_line_edit.text()

    def set_min_val_text(self, val):
        self.min_val_line_edit.setText(str(val))

    def set_max_val_text(self, val):
        self.max_val_line_edit.setText(str(val))

    def set_min_max_text(self, min_val, max_val):
        self.set_min_val_text(min_val)
        self.set_max_val_text(max_val)

    def clear(self):
        self.min_val_line_edit.clear()
        self.max_val_line_edit.clear()

