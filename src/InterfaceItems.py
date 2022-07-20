from PyQt5.QtWidgets import *
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt


class Button(QPushButton):
    def __init__(self, obj, layout, title, func=None, color="black", pos=None, *args):
        super().__init__(*args)
        self.__colors = {
            "black": "background-color: rgb(33, 33, 33)",
            "red": "background-color: rgb(160, 60, 60)",
            "green": "background-color: rgb(60, 160, 60)",
            "blue": "background-color: rgb(60, 60, 160)"
        }

        self.styleSheetTemplate = """
QPushButton {
BGCOLOR;
border-radius: 4px;
padding-left: 7px;
min-width: 150px;
max-width: 150px;
min-height: 25px;
max-height: 25px;
}

QPushButton:hover {
HOVER;
}
QPushButton:pressed {
PRESSED;
}"""

        self.setColor(color)
        self.setText(title)
        self.obj = obj
        self.clicked.connect(func)
        self.clicked.connect(obj.setFocus)
        self.clicked.connect(self.obj.state_changed)
        if pos is None or len(pos) != 2:
            layout.addWidget(self)
        else:
            layout.addWidget(self, *pos)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def setColor(self, color):
        col = self.__colors[color]
        colHover = col.replace("rgb", "rgba").replace(")", ", 60)")
        colPressed = colHover.replace(", 60)", ", 100)")
        styleSheet = self.styleSheetTemplate.replace("BGCOLOR", col).replace("HOVER",
                                                                             colHover).replace("PRESSED", colPressed)
        self.setStyleSheet(styleSheet)

    def on_off(self, key):
        try:
            self.obj.settings[key] = not self.obj.settings[key]
        except KeyError:
            print(f"Add {key} to the settings list.")
            return
        text = self.text()
        if self.obj.settings[key]:
            text = text.replace(": OFF", ": ON")
            self.setText(text)
            self.setColor("green")
        else:
            text = text.replace(": ON", ": OFF")
            self.setText(text)
            self.setColor("red")


class Slider(QSlider):
    def __init__(self, obj, twist, func, layout, scope, startValue, pos=None, *args):
        super().__init__(twist, *args)
        self.obj = obj
        self.valueChanged.connect(func)
        self.valueChanged.connect(lambda value: obj.setFocus())
        self.valueChanged.connect(self.obj.state_changed)
        self.setMinimum(scope[0])
        self.setMaximum(scope[1])
        self.setValue(int(startValue))
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet("""
        QSlider {
            min-width: 150px;
            max-width: 150px;
        }
        """)
        if pos is None or len(pos) != 2:
            layout.addWidget(self)
        else:
            layout.addWidget(self, *pos)


class CheckBox(QCheckBox):
    def __init__(self, obj, layout, title, arg_name, pos):
        super().__init__()
        self.obj = obj
        self.arg_name = arg_name
        self.setText(title)
        self.setChecked(obj.settings[arg_name])
        self.stateChanged.connect(self.change_value)
        self.stateChanged.connect(self.obj.state_changed)
        if pos is None or len(pos) != 2:
            layout.addWidget(self)
        else:
            layout.addWidget(self, *pos)

    def change_value(self):
        self.obj.settings[self.arg_name] = not self.obj.settings[self.arg_name]
