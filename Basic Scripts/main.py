import sys
from PyQt5.QtWidgets import QApplication
from Scripts.window import App



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())