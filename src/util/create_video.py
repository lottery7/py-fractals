import cv2
import numpy as np
from PySide6.QtGui import QImage


def create_video_from_qimages(qimages: list[QImage], output_file: str, fps: int = 60):
    """Creates video from list[QImage] and saved it in mp4 format."""

    assert output_file.endswith(".mp4")

    if not qimages:
        print("Empty list[QImage]")
        return

    height, width, channel = (
        qimages[0].height(),
        qimages[0].width(),
        4 if qimages[0].hasAlphaChannel() else 3,
    )

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    for qimage in qimages:
        buffer = qimage.constBits().tobytes()
        img = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, channel)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

        video_writer.write(img)

    video_writer.release()
