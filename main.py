from crawler import Crawler
from config import Config
from PyQt5 import QtCore, QtWidgets, QtGui  # All GUI things
from results_gui import ResultsList
from compare_image import CompareImage
import sys
import paths
import cv2


"""
TODO
When "start scan" is pressed, self.crawler is constructed with the settings

Initialization of crawler must catch FILENOTFOUNDERROR in case the chromedriver.exe is not in the same directory

Settings:
    Maximum amount of browser instances
    Maximum depth of search
    Timeout for a URL before giving up and trying a new one
"""


class MainWindow(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        self.config = Config()
        self.crawler = None  # Initialized in self.start_scan
        self.comparer = CompareImage()

        # Init UI Globals
        self.scan_btn = QtWidgets.QPushButton("Start Search")
        self.settings_btn = QtWidgets.QPushButton("Settings")
        self.template_btn = QtWidgets.QPushButton("Template")
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.scan_cnt_lbl = QtWidgets.QLabel("")
        self.results_lst = ResultsList(self)

        # Create the timer for the scanner
        self.scan_timer = QtCore.QTimer()
        self.scan_check_time = 100  # How often to check for images in self.crawler
        self.scanned_count = 0  # How many images have been scanned

        # Initialize the UI
        self.init_UI()

    def init_UI(self):
        self.progress_bar.setFixedWidth(350)


        # Set up buttons
        self.settings_btn.setIcon(QtGui.QIcon(paths.settings))
        self.scan_btn.setIcon(QtGui.QIcon(paths.start_scan))
        self.template_btn.setIcon(QtGui.QIcon(paths.add_template))

        self.scan_btn.setToolTip("This will start searching the websites specified in the list of websites to search")
        self.settings_btn.setToolTip("This will open a settings window to configure your scan")
        self.template_btn.setToolTip("This will add an image to search for in the images throughout the scan")

        self.scan_btn.clicked.connect(self.start_scan)
        self.settings_btn.clicked.connect(self.open_settings)
        self.template_btn.clicked.connect(self.add_template)

        col2 = QtWidgets.QVBoxLayout()
        col2.addWidget(self.settings_btn)
        col2.addWidget(self.template_btn)
        col2.addStretch(1)
        col2.addWidget(self.scan_btn)

        col1row1 = QtWidgets.QHBoxLayout()
        col1row1.addWidget(self.progress_bar)
        col1row1.addWidget(self.scan_cnt_lbl)

        col1 = QtWidgets.QVBoxLayout()
        col1.addWidget(self.results_lst)
        col1.addLayout(col1row1)


        row1 = QtWidgets.QHBoxLayout()
        row1.addLayout(col1)
        row1.addLayout(col2)

        self.setLayout(row1)
        self.setWindowTitle('Image Crawler')
        self.show()


    # Controls Events
    def start_scan(self):
        """
        Throws error message if no websites are on the list

        Disables button while scan is running
        :return:
        """

        # If no websites exist in the list
        if len(self.config.websites) == 0:
            QtWidgets.QMessageBox.question(self, 'Can Not Continue',
                                           "You have not specified any URL's to scan. Try adding some!",
                                           QtWidgets.QMessageBox.Ok)
            return

        # If no templates have been added to be tracked
        if len(self.comparer.get_template()) == 0:
            QtWidgets.QMessageBox.question(self, 'Can Not Continue',
                                           "You have not added any template images for the scanner to search for. "
                                           "Try adding some!",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.crawler = Crawler(self.config.websites,
                               self.config.search_depth,
                               self.config.max_browsers,
                               self.config.browser_timeout)

        # Disable the scan button
        self.scan_btn.setDisabled(True)
        self.settings_btn.setDisabled(True)
        self.template_btn.setDisabled(True)

        # Start crawling in another thread
        self.crawler.start()

        # Start analyzing in a while so the browsers have time to open
        self.scan_timer.singleShot(1000, self.analyze_image)

    def open_settings(self):
        self.settings_btn.setDisabled(True)

        window = QtWidgets.QDialog()

        def addRow(left, right):
            right.setFixedWidth(100)
            row = QtWidgets.QHBoxLayout()
            row.addStretch(1)
            row.addWidget(left)
            row.addWidget(right)
            window.content.addLayout(row)

        # Create the apply/cancel buttons, connect them, and format them
        window.okBtn = QtWidgets.QPushButton('Ok')
        window.okBtn.setMaximumWidth(100)
        window.okBtn.clicked.connect(window.accept)

        # Create a content box for the command to fill out parameters and GUI elements
        window.content = QtWidgets.QVBoxLayout()
        window.content.setContentsMargins(20, 10, 20, 10)

        # Now that the window is 'dressed', add "Cancel" and "Apply" buttons
        buttonRow = QtWidgets.QHBoxLayout()
        buttonRow.addStretch(1)
        buttonRow.addWidget(window.okBtn)

        # Create the main vertical layout, add everything to it
        window.mainVLayout = QtWidgets.QVBoxLayout()
        window.mainVLayout.addLayout(window.content)
        window.mainVLayout.addStretch(1)

        # Set the main layout and general window parameters
        window.setLayout(window.mainVLayout)
        window.setWindowTitle("Scan Settings")
        window.setWindowIcon(QtGui.QIcon(paths.settings))

        # Dress the base window (this is where the child actually puts the content into the widget)
        desc_lbl = QtWidgets.QLabel("Customize Your Scan")

        depth_lbl = QtWidgets.QLabel("Scan Depth")
        brwsr_lbl = QtWidgets.QLabel("Maximum Open Browsers")
        timeout_lbl = QtWidgets.QLabel("URL Load Timeout (s)")
        ratio_lbl = QtWidgets.QLabel("Min Percent Match")

        window.depth_txt = QtWidgets.QLineEdit()
        window.brwsr_txt = QtWidgets.QLineEdit()  # Show prints from robot class
        window.timeout_txt = QtWidgets.QLineEdit()  # Show prints from robot class
        window.ratio_sldr = QtWidgets.QSlider()

        # Any setup that's necessary
        window.ratio_sldr.setRange(0, 95)
        window.ratio_sldr.setOrientation(QtCore.Qt.Horizontal)

        # Recover previous settings
        window.depth_txt.setText(str(self.config.search_depth))
        window.brwsr_txt.setText(str(self.config.max_browsers))
        window.timeout_txt.setText(str(self.config.browser_timeout))
        window.ratio_sldr.setValue(self.config.min_match_percent)

        window.content.addWidget(desc_lbl)
        addRow(depth_lbl, window.depth_txt)
        addRow(brwsr_lbl, window.brwsr_txt)
        addRow(timeout_lbl, window.timeout_txt)
        addRow(ratio_lbl, window.ratio_sldr)

        window.mainVLayout.addLayout(buttonRow)  # Add button after, so hints appear above buttons

        # Run the info window and prevent other windows from being clicked while open:
        accepted = window.exec_()

        if accepted:
            try: self.config.search_depth = int(window.depth_txt.text())
            except ValueError: pass

            try: self.config.max_browsers = int(window.brwsr_txt.text())
            except ValueError: pass

            try: self.config.browser_timeout = int(window.timeout_txt.text())
            except ValueError: pass

            self.config.min_match_percent = window.ratio_sldr.value()

        # Make sure QT properly handles the memory after this function ends
        window.close()
        window.deleteLater()

        self.settings_btn.setEnabled(True)

    def add_template(self):
        """ This happens when the Template button is pressed. It adds an image to the tracker to search for """

        img_file = QtWidgets.QFileDialog.getOpenFileName(self,
                                                    'Add Template Image',  # Window title
                                                    './',  # Directory
                                                    '*.png')[0]  # File type
        # If the user pressed cancel
        if img_file is None: return

        # Add the image to the comparer
        img = cv2.imread(img_file)
        self.comparer.add_template(img)


    # Scan Logic
    def analyze_image(self):
        """ This will pull an image that has been found by the crawler and analyze it """
        timer = lambda: self.scan_timer.singleShot(self.scan_check_time, self.analyze_image)

        url, img = self.crawler.get_image()

        # If no image is in the queue, ignore
        if img is None:
            timer()
            return


        if self.comparer.is_match(img, self.config.min_match_percent / 100.0):
            print("GOT MATCH!", self.scanned_count)
            cv2.imwrite("OUTPUT/" + str(self.scanned_count) + '.png', img)
            cv2.waitKey(1)
            self.add_match(img, "Image " + str(self.scanned_count), url)

        # Finish up and set the timer again
        self.scanned_count += 1
        self.scan_cnt_lbl.setText("Tested: " + str(self.scanned_count))
        timer()

    def add_match(self, image, id, url):
        # TODO(Alex): Add something to a file log here
        self.results_lst.add_item(image, id, url)


    # QT Events
    def closeEvent(self, event):
        # If there is an ongoing crawling session, close it
        if self.crawler is not None:
            self.crawler.close()


if __name__ == '__main__':
    # Install a global exception hook to catch pyQt errors that fall through (for debugging)
    sys.__excepthook = sys.excepthook
    sys._excepthook  = sys.excepthook
    def exception_hook(exctype, value, traceback):
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook   = exception_hook


    # Create the Application base
    app = QtWidgets.QApplication(sys.argv)

    # Set Application Font
    font = QtGui.QFont()
    font.setFamily("Verdana")
    font.setPixelSize(12)
    app.setFont(font)

    # Actually start the program
    mainWindow = MainWindow()
    sys.exit(app.exec_())
