from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QFileDialog
from PyQt5.QtWidgets import QMainWindow


class App(QMainWindow,QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Transfer files with congestion control'
        self.left = 150
        self.top = 150
        self.width = 640 * 2
        self.height = int(480 * 1.3)

        self.initUI()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(400, 500)
        self.textbox.resize(600, 40)

        # Buttons
        button = QPushButton('Choose', self)
        button.setToolTip('This is an example button')
        button.move(1000, 500)
        button.clicked.connect(self.openFileNameDialog)

        # Create widget -- not yet implemented
        #label = QLabel(self)
        #pixmap = QPixmap('logo_ac_iasi.jpg')
        #pixmap.
        #label.setPixmap(pixmap)
        #self.resize(pixmap.width(), pixmap.height())

        self.show()