import cv2


def open_camera(camera_index: int = 0, frame_width: int = 640, frame_height: int = 480):
    capture = cv2.VideoCapture(camera_index)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    return capture
