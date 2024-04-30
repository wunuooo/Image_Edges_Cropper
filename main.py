from PyQt5.QtWidgets import QApplication
from sys import exit, argv
from GUI_window import MainWindow


if __name__ == '__main__':

    app = QApplication(argv)
    window = MainWindow()
    window.show()
    exit(app.exec_())