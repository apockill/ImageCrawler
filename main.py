import sys
import paths
from crawler import Crawler
from config import Config
from PyQt5 import QtCore, QtWidgets, QtGui  # All GUI things
from results_gui import ResultsList

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

        # Init UI Globals
        self.scan_btn = QtWidgets.QPushButton("Start Search")
        self.settings_btn = QtWidgets.QPushButton("Settings")
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.results_lst = ResultsList(self)

        # Initialize the UI
        self.init_UI()

        # Create the timer for the scanner
        self.scan_timer = QtCore.QTimer()

    def init_UI(self):
        # Set up buttons
        self.settings_btn.setIcon(QtGui.QIcon(paths.settings))
        self.scan_btn.setIcon(QtGui.QIcon(paths.start_scan))

        self.scan_btn.setToolTip("This will start searching the websites specified in the list of websites to search")
        self.settings_btn.setToolTip("This will open a settings window to configure your scan")

        self.scan_btn.clicked.connect(self.start_scan)
        self.settings_btn.clicked.connect(self.open_settings)

        col2 = QtWidgets.QVBoxLayout()
        col2.addWidget(self.settings_btn)
        col2.addStretch(1)
        col2.addWidget(self.scan_btn)


        col1 = QtWidgets.QVBoxLayout()
        col1.addWidget(self.results_lst)
        col1.addWidget(self.progress_bar)


        row1 = QtWidgets.QHBoxLayout()
        row1.addLayout(col1)
        row1.addLayout(col2)

        self.setLayout(row1)
        self.setWindowTitle('')
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

        self.crawler = Crawler(self.config.websites)

        # Disable the scan button
        self.scan_btn.setDisabled(True)

        # self.results_lst.add_item("www.amazon.com", "some image description")

        # Start crawling in another thread
        self.crawler.start()


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
        descLbl = QtWidgets.QLabel("Customize Your Scan")

        depth_lbl = QtWidgets.QLabel("Scan Depth")
        brwsr_lbl = QtWidgets.QLabel("Maximum Open Browsers")
        timeout_lbl = QtWidgets.QLabel("URL Load Timeout (s)")

        window.depth_txt = QtWidgets.QLineEdit()
        window.brwsr_txt = QtWidgets.QLineEdit()  # Show prints from robot class
        window.timeout_txt = QtWidgets.QLineEdit()  # Show prints from robot class

        # Recover previous settings
        window.depth_txt.setText(str(self.config.search_depth))
        window.brwsr_txt.setText(str(self.config.max_browsers))
        window.timeout_txt.setText(str(self.config.browser_timeout))

        window.content.addWidget(descLbl)
        addRow(depth_lbl, window.depth_txt)
        addRow(brwsr_lbl, window.brwsr_txt)
        addRow(timeout_lbl, window.timeout_txt)

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


        # Make sure QT properly handles the memory after this function ends
        window.close()
        window.deleteLater()

        self.settings_btn.setEnabled(True)

    # Scan Logic
    def analyze_image(self):
        """ This will pull an image that has been found by the crawler and analyze it """
        pass

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
