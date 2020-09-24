from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import algorithms
from PIL import Image

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.title = "Računanje projektivnog preslikavanja i otklanjanje distorzije"
        self.top = 50
        self.left = 50
        self.width = 1200
        self.height = 675

        self.xs = []
        self.ys = []

        self.xs_proj = []
        self.ys_proj = []

        self.fileName = ""
        self.nPoints = 0
        
        self.pixmap = QtGui.QPixmap()
        self.painter1 = QtGui.QPainter()
        self.pixmap2 = QtGui.QPixmap()
        self.painter2 = QtGui.QPainter()
        
        self.setFixedSize(1200, 787.5)
        self.InitWindow()
        self.show()

    def InitWindow(self):

        vbox = QtWidgets.QVBoxLayout()
    
        hboxInsert = QtWidgets.QHBoxLayout()
        hboxInsert.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        hboxInsert.setSpacing(10)
        hboxInsert.setContentsMargins(0, 0, 0, 0)

        self.imageAdd = QtWidgets.QPushButton("Dodajte sliku")
        self.imageAdd.setFixedSize(150, 50)
        self.numOfPoints = QtWidgets.QLineEdit()
        self.numOfPoints.setPlaceholderText("#tačaka")
        self.numOfPoints.setFixedSize( 60, 40 ) 
        self.numButton = QtWidgets.QPushButton("Potvrdi")
        self.numButton.setFixedSize(100, 50)
        
        self.numButton.clicked.connect(self.on_click_numPoints)
        self.imageAdd.clicked.connect(self.file_open)
        
        hboxInsert.addWidget(self.numOfPoints)
        hboxInsert.addWidget(self.numButton)
        hboxInsert.addWidget(self.imageAdd)
        
        vbox.addLayout(hboxInsert)

        hboxButton = QtWidgets.QHBoxLayout()
        self.naiveButton = QtWidgets.QPushButton("Naivni")
        self.naiveButton.setFixedSize(200, 60)
        self.naiveButton.clicked.connect(self.on_click_naive)
        self.DLTButton = QtWidgets.QPushButton("DLT")
        self.DLTButton.clicked.connect(self.on_click_dlt)
        self.DLTButton.setFixedSize(200, 60)
        self.DLTNButton = QtWidgets.QPushButton("DLT Normalizovan")
        self.DLTNButton.setFixedSize(200, 60)
        self.DLTNButton.clicked.connect(self.on_click_dltN)

        hboxButton.addWidget(self.naiveButton)
        hboxButton.addWidget(self.DLTButton)
        hboxButton.addWidget(self.DLTNButton)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(50, 20, 50, 20)
        menu_bar = QtWidgets.QMenuBar()
        vbox.addWidget(menu_bar)

        hbox.setAlignment(QtCore.Qt.AlignCenter)

        openFile = QtWidgets.QAction("&Open Image", self)
        openFile.setShortcut("Crtl+O")
        openFile.setStatusTip("Open Image")
        openFile.triggered.connect(self.file_open)

        fileMenu = menu_bar.addMenu('&File')
        fileMenu.addAction(openFile)

        self.label1 = QtWidgets.QLabel("Pogledajte u padajući meni! :)")
        hbox.addWidget(self.label1)

        self.label2 = QtWidgets.QLabel("")
        hbox.addWidget(self.label2)
        
        vbox.addLayout(hbox)      
        vbox.addLayout(hboxButton)  

        self.setLayout(vbox)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.show()

    def file_open(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                            '.', "Image files (*.jpg *.gif *.png)"
        )

        imagePath = fname[0]
        self.fileName = imagePath
        
        self.pixmap = QtGui.QPixmap(imagePath)
        self.pixmap2 = QtGui.QPixmap("black.jpg")

        self.pixmap = self.pixmap.scaled(500, 700, 
                                    QtCore.Qt.KeepAspectRatio,
                                    QtCore.Qt.FastTransformation)

        self.pixmap2 = self.pixmap2.scaled(self.pixmap.width(), self.pixmap.height())

        self.label1.resize(self.pixmap.width(), self.pixmap.height())
        self.label1.setScaledContents( True )
        self.painter1 = QtGui.QPainter(self.pixmap)
        self.painter1.setBrush(QtGui.QBrush(QtCore.Qt.red))
        self.label1.setPixmap(self.pixmap)

        self.label2.resize(self.pixmap.width(), self.pixmap.height())
        self.label2.setScaledContents( True )
        self.painter2 = QtGui.QPainter(self.pixmap2)
        self.painter2.setBrush(QtGui.QBrush(QtCore.Qt.green))
        self.label2.setPixmap(self.pixmap2)

        self.label1.mousePressEvent = self.getPos

    def getPos(self, event):
        if(self.nPoints == 0):
            return
        
        x = event.pos().x()
        y = event.pos().y()

        self.painter1.drawEllipse(x-5, y-5, 10, 10)
        self.label1.setPixmap(self.pixmap)

        self.xs.append(x)
        self.ys.append(y)

        if(len(self.xs) < (self.nPoints + 1) and len(self.xs) != self.nPoints):
            QtWidgets.QMessageBox.about(self, "Koordinate originala", 
            "Označili ste tačku: (" + str(x)  + ", " + str(y) + ")")
            
        elif(len(self.xs) == self.nPoints):
            QtWidgets.QMessageBox.about(self, "Koordinate originala", 
            "Označili ste tačku: (" + str(x)  + ", " + str(y) + ")" + "\n" +
             "Pređite na projektivne tačke.")
            self.label1.mousePressEvent = {}
            self.label2.mousePressEvent = self.getPos2

    def getPos2(self, event):
        if(self.nPoints == 0):
            return
        
        x = event.pos().x()
        y = event.pos().y() 

        self.painter2.drawEllipse(x-5, y-5, 10, 10)
        self.label2.setPixmap(self.pixmap2)

        self.xs_proj.append(x)
        self.ys_proj.append(y)
        
        if(len(self.xs_proj) < (self.nPoints + 1) and len(self.xs_proj) != self.nPoints):
            QtWidgets.QMessageBox.about(self, "Koordinate projekcije", 
            "Označili ste tačku: (" + str(x)  + ", " + str(y) + ")")
            
        elif(len(self.xs_proj) == self.nPoints):
            QtWidgets.QMessageBox.about(self, "Koordinate originala", 
            "Označili ste tačku: (" + str(x)  + ", " + str(y) + ")" + "\n" +
             "KRAJ KLIKTANJA.")
            self.label2.mousePressEvent = {}


    def on_click_numPoints(self):
        self.numOfPoints.setReadOnly(True)
        self.nPoints = int(self.numOfPoints.text())
        print("Broj tacaka: " + str(self.nPoints))

    def on_click_naive(self):
        if (len(self.xs) == self.nPoints):

            proj_width = self.label1.width()
            proj_height = self.label1.height()

            img_original = Image.open(self.fileName)
            algorithms.naive(self.xs, self.ys, self.xs_proj, self.ys_proj, proj_width, proj_height, img_original)

            print("Zavrsio je Naivni!")

            pixmap = QtGui.QPixmap("out.bmp")
            pixmap = pixmap.scaled(600, 800, 
                                QtCore.Qt.KeepAspectRatio,
                                QtCore.Qt.FastTransformation)

            self.label2.resize(proj_width, proj_height)
            self.label2.setPixmap(QtGui.QPixmap(pixmap))

        else:
            pass  

    def on_click_dlt(self):
        if (len(self.xs) == self.nPoints):

            proj_width = self.label1.width()
            proj_height = self.label1.height()

            img_original = Image.open(self.fileName)
            algorithms.dlt(self.xs, self.ys, self.xs_proj, self.ys_proj, proj_width, proj_height, img_original)

            print("Zavrsio je DLT!")

            pixmap = QtGui.QPixmap("out.bmp")
            pixmap_resized = pixmap.scaled(600, 800, 
                                        QtCore.Qt.KeepAspectRatio,
                                        QtCore.Qt.FastTransformation)
            self.label2.resize(proj_width, proj_height)
            self.label2.setPixmap(QtGui.QPixmap(pixmap_resized))
        else:
            pass 

    def on_click_dltN(self):
        if (len(self.xs) == self.nPoints):

            proj_width = self.label1.width()
            proj_height = self.label1.height()

            img_original = Image.open(self.fileName)
            algorithms.dltN(self.xs, self.ys, self.xs_proj, self.ys_proj, proj_width, proj_height, img_original)

            print("Zavrsio je DLT Normalizovani!")

            pixmap = QtGui.QPixmap("out.bmp")
            pixmap_resized = pixmap.scaled(600, 600, 
                                        QtCore.Qt.KeepAspectRatio,
                                        QtCore.Qt.FastTransformation)
            self.label2.resize(proj_width, proj_height)
            self.label2.setPixmap(QtGui.QPixmap(pixmap_resized))
        else:
            pass 

App = QtWidgets.QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
