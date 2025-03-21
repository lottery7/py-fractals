import glob
import os
from datetime import datetime

import ffmpeg
from OpenGL.GL import *
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import *


class Fractal2D(QOpenGLWidget):
    def save_position(self):
        with open("res/doc/positions.txt", "a") as file:
            text = "; ".join(
                [
                    f'{self.settings["OFFSET"][0]}',
                    f'{self.settings["OFFSET"][1]}',
                    f'{self.settings["ZOOM"]}',
                ]
            )
            file.write(text + "\n")

    def save_video(self):
        self._anim_progress_bar.setVisible(True)
        old_size = self.size()
        if self.settings["HIGH_VIDEO_QUALITY"]:
            self.resize(2560, 1440)

        for i in range(round(self.animation_length * 60 + 60)):
            if self.animation_length * 60 + 30 >= i >= 30:
                self.animate()
            scr = self.grabFramebuffer()
            scr.save(f"res/tmp/image{i:08d}.jpg", "jpg")
            self._anim_progress_bar.setValue(round(i / (self.animation_length + 1) / 60 * 100))

        self.resize(old_size)

        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        try:
            stream = ffmpeg.input("res/tmp/image%08d.jpg", framerate=60)
            stream = ffmpeg.output(stream, f"res/video/animation_{date}.mp4", video_bitrate="20000k")
            ffmpeg.run(stream)
        except Exception:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("ffmpeg error. Try to reinstall ffmpeg.")

        for file in glob.glob("res/tmp/*"):
            os.remove(file)

        self._anim_progress_bar.setValue(0)

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Info")
        dlg.setIcon(QMessageBox.Information)
        dlg.setText(f"Animation is saved.")
        dlg.setDetailedText("PATH: res/video/animation_" + date + ".mp4")
        dlg.setStyleSheet(
            """QLabel{height: 30px; min-height: 30px; max-height: 30px;
                                            width: 300px; min-width:300px; max-width:300px;}"""
        )
        dlg.exec()

        self._anim_progress_bar.setVisible(False)

    def input_position(self):
        text, ok = QInputDialog.getText(self, "Position", "Enter x; y; z:")
        if ok:
            text = text.split(";")
            for i in range(3):
                if not text[i]:
                    continue
                val = float(text[i])
                if i == 0:
                    self.settings["OFFSET"][0] = val
                elif i == 1:
                    self.settings["OFFSET"][1] = val
                else:
                    self.settings["ZOOM"] = val

    def setup_ui(self):
        self.add_button("Object color", lambda: self._color_picker("COLOR"), color="black")
        self.add_button("Screenshot", self.take_screenshot, color="black")
        self.add_button("Save position", self.save_position)
        self.add_button("Input position", self.input_position)
        self.add_check_box("Anti-aliasing", "AA")
        self.add_check_box("High screenshot quality", "HIGH_SCR_QUALITY")

        CheckBox(self, self.anim_panel, "High video quality", "HIGH_VIDEO_QUALITY", None)
        CheckBox(self, self.anim_panel, "Real-time", "ANIMATION", None)
        Button(self, self.anim_panel, "Save animation", self.save_video, "black")

        self._anim_param_end_value.setText("DIE")
        self.anim_panel.addWidget(self._anim_param_end_value)
        self.anim_panel.addWidget(self._anim_progress_bar)

    def take_screenshot(self):
        date = datetime.now().strftime("%Y-%m2d-%d_%H-%M-%S.jpg")
        path = f"res/screenshots/screenshot_{date}"
        self.resize(self.width() + self.width() % 2, self.height() + self.height() % 2)

        old_size = self.size()
        if self.settings["HIGH_SCR_QUALITY"]:
            self.resize(2560, 1440)

        scr = self.grabFramebuffer()
        scr.save(path, "jpg")

        self.resize(old_size)

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Info")
        dlg.setIcon(QMessageBox.Information)
        dlg.setText(f"Screenshot is saved.")
        dlg.setDetailedText("PATH:\n" + path + "\n")
        dlg.setStyleSheet(
            """QLabel{height: 30px; min-height: 30px; max-height: 30px;
                                    width: 300px; min-width:300px; max-width:300px;}"""
        )
        dlg.exec()

    def update_status_bar(self):
        status_list = []
        for key, value in self._status_dict.items():
            form, unpack = value
            val = self.settings[key]
            if unpack:
                status_list.append(form.format(*val))
            else:
                status_list.append(form.format(val))
        self.status = " ".join(status_list)
        self.window.statusBar.showMessage(self.status)
