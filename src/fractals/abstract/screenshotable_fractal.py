import os
from datetime import datetime

from PySide6.QtWidgets import QFileDialog

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

    def _take_screenshot(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "Choose folder")
        date = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        path = os.path.join(folder_path, f"{date}.jpg")

        old_size = self.size()

        if self.high_screenshot_quality:
            self.resize(2560, 1440)
        else:
            self.resize(self.width() + self.width() % 2, self.height() + self.height() % 2)

        scr = self.grabFramebuffer()
        scr.save(path, "jpg")

        self.resize(old_size)
