from PyQt5 import QtGui
import cv2

def resize_to_max(img, max_width, max_height):
    """
    Resize the image, keep aspect ratio, and resize it so that either the width or the height match the max_width
    or the max_height

    :param max_width: desired width, if the image is wider than it is tall
    :param max_height: desired height, if the image is wider than it is tall
    :return:
    """
    cur_h, cur_w, _ = img.shape

    if cur_w > cur_h:
        scale_factor = max_width / cur_w
        new_w = int(cur_w * scale_factor)
        new_h = int(cur_h * scale_factor)
    else:
        scale_factor = max_height / cur_h
        new_w = int(cur_w * scale_factor)
        new_h = int(cur_h * scale_factor)

    return cv2.resize(img, (new_w, new_h))


def cv_to_qt(img_cv):
    height, width, channel = img_cv.shape
    bytes_per_line = 3 * width
    q_img = QtGui.QImage(img_cv.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
    return q_img