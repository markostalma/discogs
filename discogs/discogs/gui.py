import math
import sys
import threading

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import QTimer, SLOT, Qt
from PySide2.QtGui import QPalette, QPainter, QBrush, QColor, QPen
from PySide2.QtWidgets import QAction, QMessageBox, QWidget
from pywin.scintilla.find import FindDialog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.first_widget = FirstWidget(self)
        self.setCentralWidget(self.first_widget)

        menuBar = self.menuBar()
        aboutMenu = menuBar.addMenu('&About')
        aboutMenu.addAction('About Program')
        #aboutMenu.triggered[QAction].connect(self.aboutProgramMenuClicked)
        aboutMenu.addAction('About Author')
        #aboutMenu.triggered[QAction].connect(self.aboutAuthorMenuClicked)
        helpMenu = menuBar.addMenu('&Help')
        helpMenu.addAction('Quick Help')
        exitMenu = menuBar.addMenu('&Exit')
        exitMenu.addAction("Click to Exit")
        exitMenu.triggered[QAction].connect(self.exitMenuClicked)

    def aboutProgramMenuClicked(self):
        print('About Program')

    def aboutAuthorMenuClicked(self):
        print('About Author')

    def exitMenuClicked(self):
        exit(1)

class FirstWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(FirstWidget, self).__init__(parent)

        self.parent = parent

        # Label
        self.comboLabel = QtWidgets.QLabel("Choose Algortihm!")
        self.comboLabel.setFont(QtGui.QFont("Titilium", 14))
        self.comboLabel.setAlignment(QtCore.Qt.AlignCenter)

        # Combo Box
        self.comboListItems = ["Choose Algortihm!", 'K - Means', 'Other Algorithm']
        self.comboList = QtWidgets.QComboBox()
        self.comboList.addItems(self.comboListItems)

        # Button
        self.btn = QtWidgets.QPushButton("Choose and go")
        self.btn.clicked.connect(self.goToNextPage)

        # Set Layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.comboLabel)
        self.layout.addWidget(self.comboList)
        self.layout.addWidget(self.btn)
        self.setLayout(self.layout)

    # Go to Next Page after Choosing a content from a list
    def goToNextPage(self):
        if self.comboList.currentIndex() == 1:
            self.second_widget = SecondWidget(self.parent, 1)
            self.parent.setCentralWidget(self.second_widget)
            self.hide()
        elif self.comboList.currentIndex() == 2:
            self.second_widget = SecondWidget(self.parent, 2)
            self.parent.setCentralWidget(self.second_widget)
            self.hide()
        else:
            print('Nisi izabrao!')


class SecondWidget(QtWidgets.QWidget):
    def __init__(self, parent, type):
        super(SecondWidget, self).__init__(parent)

        self.type = type
        self.parent = parent

        # Set Layout
        self.layout = QtWidgets.QVBoxLayout()
        self.overlay = Overlay(self)
        self.overlay.hide()

        if type == 1:
            # Label
            self.comboLabel = QtWidgets.QLabel("Choose Cluster Number!")
            self.comboLabel.setFont(QtGui.QFont("Titilium", 14))
            self.comboLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.comboLabel.show()

            # Combo Box for entries
            self.comboListItems = ['Genre', 'Styles', 'Publish Year']
            self.comboListEntries = QtWidgets.QComboBox()
            self.comboListEntries.addItems(self.comboListItems)
            # self.comboListEntries.show()

            # Combo Box for number of clusters
            self.comboListItems = ["1", "2", "3", "4", "5"]
            self.comboListClusters = QtWidgets.QComboBox()
            self.comboListClusters.addItems(self.comboListItems)
            # self.comboListClusters.show()

            self.layout.addWidget(self.comboLabel)
            self.layout.addWidget(self.comboListEntries)
            self.layout.addWidget(self.comboListClusters)
        elif type == 2:
            # Label
            self.comboLabel = QtWidgets.QLabel("Other option")
            self.comboLabel.setFont(QtGui.QFont("Titilium", 14))
            self.comboLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.comboLabel.show()
            self.layout.addWidget(self.comboLabel)
        else:
            print('Izvrši proveru mačko!')

        # Button
        self.btn = QtWidgets.QPushButton("Choose and go")
        self.btn.clicked.connect(self.goToNextPage)

        self.layout.addWidget(self.btn)
        self.setLayout(self.layout)


    def do_work(self, func):
        print('Nit')
        func()
        self.overlay.hide()
        self.third_widget = ThirdWidget(self.parent)
        self.parent.setCentralWidget(self.third_widget)
        self.hide()


    def cluster(self):
        print('CLUSTER')


    def other(self):
        print('OTHER')



    # Go to Next Page after Choosing a content from a list
    def goToNextPage(self):
        self.overlay.show()

        if self.type == 1:
            t = threading.Thread(target=self.do_work, args=(self.cluster,))
            t.start()
        else:
            t = threading.Thread(target=self.do_work, args=(self.other,))
            t.start()


class ThirdWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ThirdWidget, self).__init__(parent)

        # Label
        self.comboLabel = QtWidgets.QLabel("Vizualization!")
        self.comboLabel.setFont(QtGui.QFont("Titilium", 14))
        self.comboLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.comboLabel.show()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.comboLabel)
        self.setLayout(self.layout)


class Overlay(QWidget):
     def __init__(self, parent = None):

         QWidget.__init__(self, parent)
         palette = QPalette(self.palette())
         palette.setColor(palette.Background, Qt.transparent)
         self.setPalette(palette)

     def paintEvent(self, event):

         painter = QPainter()
         painter.begin(self)
         painter.setRenderHint(QPainter.Antialiasing)
         painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
         painter.setPen(QPen(Qt.NoPen))

         for i in range(6):
             if (self.counter / 5) % 6 == i:
                 painter.setBrush(QBrush(QColor(127 + (self.counter % 5)*32, 127, 127)))
             else:
                 painter.setBrush(QBrush(QColor(127, 127, 127)))
             painter.drawEllipse(
                 self.width()/2 + 15 * math.cos(2 * math.pi * i / 6.0) - 10,
                 self.height()/2 + 15 * math.sin(2 * math.pi * i / 6.0) - 10,
                 20, 20)

         painter.end()

     def showEvent(self, event):

         self.timer = self.startTimer(50)
         self.counter = 0

     def timerEvent(self, event):

         self.counter += 1
         self.update()
         if self.counter == 60:
            self.killTimer(self.timer)
            self.hide()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = MainWindow()
    widget.setWindowTitle("My App")
    widget.resize(300, 150)
    widget.show()

    sys.exit(app.exec_())



