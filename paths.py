import os
import sys

resourcesLoc = "Resources"
icons_dir = "Icons\\"


def resourcePath(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

icon_dir = resourcePath("Icons")

settings = os.path.join(icon_dir, "settings.png")
start_scan = os.path.join(icon_dir, "start_scan.png")
add_template = os.path.join(icon_dir, "add_template.png")