"""
This is supposed to be a pretty list of things that have been found in the web crawling so far
"""
from PyQt5 import QtCore, QtWidgets, QtGui
from image_utils import resize_to_max, cv_to_qt

class ResultWidget(QtWidgets.QWidget):
    def __init__(self, parent, image, title, url):
        super(ResultWidget, self).__init__(parent)

        # Set up Globals
        self.indent = 0
        self.margins = None  # Is set after initUI creates it's first layout

        # Set up UI Globals
        self.title       = QtWidgets.QLabel(title)
        self.description = QtWidgets.QLabel(url)
        self.icon        = QtWidgets.QLabel()

        self.initUI()
        self.setIcon(image)

    def initUI(self):
        bold = QtGui.QFont()
        bold.setBold(True)
        self.title.setFont(bold)


        midLayout = QtWidgets.QVBoxLayout()
        midLayout.setSpacing(1)
        midLayout.addWidget(self.title)
        midLayout.addWidget(self.description)


        mainHLayout = QtWidgets.QHBoxLayout()
        mainHLayout.addWidget(self.icon)
        mainHLayout.addLayout(midLayout, QtCore.Qt.AlignLeft)

        mainHLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(mainHLayout)
        self.resize(self.sizeHint())
        # self.setSizeHint(self.sizeHint())
        # self.setSize

    def setIcon(self, img_cv):
        img_cv = resize_to_max(img_cv, 32, 32)
        q_img = cv_to_qt(img_cv)
        self.icon.setPixmap(QtGui.QPixmap(q_img))


class ResultsList(QtWidgets.QListWidget):
    MINIMUM_WIDTH  = 300

    def __init__(self, parent):
        super().__init__(parent)

        self.init_UI()

    def init_UI(self):
        # Set up the hintLbl overlay
        self.setMinimumWidth(self.MINIMUM_WIDTH)


    def add_item(self, image, title, url, index=None):
        """

        :param commandType: The command that will be generated
        :param parameters: The parameters that get fed into the command (Only for loading a file)
        :param index: Place the command at a particular index, instead of the end (Only for dropping item into list)
        :return:
        """

        # Create the widget to be placed inside the listWidgetItem
        newWidget = ResultWidget(self, image, title, url)


        # Create the list widget item
        listWidgetItem = QtWidgets.QListWidgetItem(self)
        listWidgetItem.setSizeHint(newWidget.sizeHint())  # Widget will not appear without this line
        self.setItemWidget(listWidgetItem, newWidget)

        # Add list widget to commandList
        self.addItem(listWidgetItem)


        # If an index was specified, move the added widget to that index
        if index is not None:
            '''
                Because PyQt is stupid, I can't simply self.insertItem(index, listWidgetItem). I have to add it, get its
                index, 'self.takeItem' it, then 'insertItem(newIndex, listWidgetItem) it. Whatever, it works, right?
            '''
            lastRow = self.indexFromItem(listWidgetItem).row()
            takenlistWidgetItem = self.takeItem(lastRow)
            self.insertItem(index, takenlistWidgetItem)
