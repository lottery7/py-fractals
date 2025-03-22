import os
from datetime import datetime
from math import ceil

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QFileDialog

from frontend.components import ColoredButton, NamedSpinBox
from frontend.constants import get_color
from util import create_video_from_qimages, use_setter

from .fractal_abc import FractalABC


class AnimatedFractal(FractalABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._anim_params: dict
        self._anim_duration: float = 1.0

    @property
    def animation_duration(self) -> float:
        return self._anim_duration

    @animation_duration.setter
    def animation_duration(self, new_value: float) -> None:
        self._anim_duration = new_value

    def animation_controls(self):
        return [
            ColoredButton(
                name="Record Video",
                color=get_color("green"),
                handlers=[self._record_animation],
            ),
            ColoredButton(
                name="Show Start State",
                color=get_color("blue"),
                handlers=[self._show_start_animation_state],
            ),
            ColoredButton(
                name="Show End State",
                color=get_color("blue"),
                handlers=[self._show_end_animation_state],
            ),
            NamedSpinBox(
                name="Duration (Seconds)",
                scope=(1, 1_000_000),
                step=0.1,
                initial=1,
                handlers=[lambda value: use_setter(self, "animation_duration", value)],
            ),
            # NamedCheckBox(
            #     name="Show In Realtime",
            #     initial=False,
            #     handlers=[self._run_motion],
            # ),
        ]

    def _step_params(self) -> QImage:
        steps = self.animation_duration * 60
        for param, config in self._anim_params.items():
            if not config["use"]:
                continue
            old_value = getattr(self, param)
            diff = config["fspeed"](config["start"], config["end"], steps)
            new_value = config["fstep"](old_value, diff)
            use_setter(self, param, new_value)

        return self.grabFramebuffer()

    def _record_animation(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "Choose folder")
        self._show_start_animation_state()

        num_frames = ceil(self.animation_duration * 60)
        frames = [self.grabFramebuffer()] + [self._step_params() for _ in range(num_frames)]
        date = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        create_video_from_qimages(
            qimages=frames,
            output_file=os.path.join(folder_path, f"{date}.mp4"),
            fps=60,
        )

    def _show_start_animation_state(self) -> None:
        for param, config in self._anim_params.items():
            if not config["use"]:
                continue
            use_setter(self, param, config["start"])

    def _show_end_animation_state(self) -> None:
        for param, config in self._anim_params.items():
            if not config["use"]:
                continue
            use_setter(self, param, config["end"])
