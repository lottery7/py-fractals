from typing import Literal

from PySide6.QtGui import QColor

_COLORS = {
    "black": QColor(33, 33, 33),
    "blue": QColor(60, 60, 160),
    "green": QColor(60, 160, 60),
    "red": QColor(160, 60, 60),
}

_QSS_COLOR_TEMPLATE_TEMPLATE = """
    {component} {{{{
        background-color: {{bgColor}};
    }}}}

    {component}:hover {{{{
        background-color: {{hoverBgColor}};
    }}}}

    {component}:pressed {{{{
        background-color: {{pressedBgColor}};
    }}}}
    """


def get_color(name: Literal["black", "blue", "green", "red"]) -> QColor:
    return QColor(_COLORS[name])


def get_qss_color_template(component_name: str):
    return _QSS_COLOR_TEMPLATE_TEMPLATE.format(component=component_name)
