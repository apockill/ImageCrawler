import sys
from PyQt5 import QtCore, QtWidgets, QtGui  # All GUI things


class MainWindow(QtWidgets.QDialog):


    def __init__(self):
        super().__init__()

        # Init UI Globals
        self.scan_btn = QtWidgets.QPushButton("Start Search")
        self.progress_bar = QtWidgets.QProgressBar(self)

        # Initialize the UI
        self.init_UI()



    def init_UI(self):
        # Set up progress bar
        # self.progress_bar.setGeometry(200, 80, 250, 200)

        # Set up buttons
        self.scan_btn.setToolTip("This will start searching the websites specified in the list of websites to search")

        self.scan_btn.clicked.connect(self.start_scan)

        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(self.progress_bar)
        row1.addWidget(self.scan_btn)

        column1 = QtWidgets.QVBoxLayout()
        column1.addLayout(row1)

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
        self.scan_btn.setDisabled(True)


    # QT Events
    def closeEvent(self, event):
        pass




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
