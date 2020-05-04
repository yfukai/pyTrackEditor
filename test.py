# - * - coding: utf8 - * -

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt test(QMainWindow)'
        self.width = 400
        self.height = 200
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.width, self.height)
        label = QLabel('This is PyQt test.', self)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())