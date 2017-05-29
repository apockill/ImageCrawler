import sys
from crawler import Crawler
from config import Config
from PyQt5 import QtCore, QtWidgets, QtGui  # All GUI things
from results_gui import ResultsList

"""
TODO: Add settings
When "start scan" is pressed, self.crawler is constructed with the settings
Settings button is disabled

Initialization of crawler must catch FILENOTFOUNDERROR in case the chromedriver.exe is not in the same directory

The first time you start scan, check to make sure there is > 1 websites in the website list
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

    def init_UI(self):
        # Set up buttons

        self.scan_btn.setToolTip("This will start searching the websites specified in the list of websites to search")
        self.scan_btn.clicked.connect(self.start_scan)

        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(self.results_lst)

        row2 = QtWidgets.QHBoxLayout()
        row2.addWidget(self.progress_bar)
        row2.addWidget(self.scan_btn)

        column1 = QtWidgets.QVBoxLayout()
        column1.addLayout(row1)
        column1.addLayout(row2)

        self.setLayout(column1)
        self.setWindowTitle('')
        self.show()


    # Controls Events
    def start_scan(self):
        """
        Throws error message if no websites are on the list

        Disables button while scan is running
        :return:
        """

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

    # QT Events
    def closeEvent(self, event):
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
