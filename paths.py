import os
import sys

resources_loc = "Resources"
icons_dir = os.path.join(resources_loc, "Icons\\")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

icon_dir = resource_path(icons_dir)

settings = os.path.join(icon_dir, "settings.png")
start_scan = os.path.join(icon_dir, "start_scan.png")
add_template = os.path.join(icon_dir, "add_template.png")
websites = os.path.join(icon_dir, "websites.png")

driver = None
if 'PHANTOMJS_LOCATION' in os.environ:
    driver = os.environ['PHANTOMJS_LOCATION']
else:
    driver = os.path.join(resource_path(resources_loc), "phantomjs.exe")
