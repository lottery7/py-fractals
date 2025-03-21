from datetime import datetime

from PySide6.QtWidgets import QMessageBox

from frontend.components import ColoredButton, NamedCheckBox
from frontend.constants import get_color
from util import use_setter

from .fractal_abc import FractalABC


class ScreenshotableFractal(FractalABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._high_screenshot_quality = False

    @property
    def high_screenshot_quality(self) -> bool:
        return self._high_screenshot_quality

    @high_screenshot_quality.setter
    def high_screenshot_quality(self, new_value: bool) -> None:
        self._high_screenshot_quality = new_value

    def fractal_controls(self):
        return [
            NamedCheckBox(
                name="High Screenshot Quality",
                initial=self.high_screenshot_quality,
                handlers=[lambda value: use_setter(self, "high_screenshot_quality", value)],
            ),
            ColoredButton(
                name="Screenshot",
                color=get_color("blue"),
                handlers=[self._take_screenshot],
            ),
        ]

    def _take_screenshot(self) -> str:
        date = datetime.now().strftime("%m-%d-%Y_%H-%M-%S.jpg")
        path = f"res/screenshots/{date}"
        old_size = self.size()

        if self.high_screenshot_quality:
            self.resize(2560, 1440)
        else:
            self.resize(self.width() + self.width() % 2, self.height() + self.height() % 2)

        scr = self.grabFramebuffer()
        scr.save(path, "jpg")

        self.resize(old_size)

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Info")
        dlg.setIcon(QMessageBox.Information)
        dlg.setText("Screenshot Saved")
        dlg.setDetailedText(f"Path: {path}")
        dlg.setStyleSheet(
            """QLabel {
                min-height: 30px; 
                max-height: 30px;
                min-width: 300px; 
                max-width: 300px;
            }"""
        )
        dlg.exec()

        return path
