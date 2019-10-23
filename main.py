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
    
        self.setFixedSize(1400, 787.5)
        #self.showFullScreen()
        self.InitWindow()

    def InitWindow(self):

        vbox = QtWidgets.QVBoxLayout()

        hboxInsert = QtWidgets.QHBoxLayout()
        self.numPointsLabel = QtWidgets.QLabel("Unesite broj tačaka:")
        self.numOfPoints = QtWidgets.QTextEdit()
        self.numPointsLabel.setFixedSize( 150, 30 )
        self.numOfPoints.setFixedSize( 80, 30 ) 

        self.numButton = QtWidgets.QPushButton("Potvrdite broj tačaka")
        self.numButton.setFixedSize(150, 50)
        
        hboxInsert.addWidget(self.numPointsLabel)
        hboxInsert.addWidget(self.numOfPoints)
        hboxInsert.addWidget(self.numButton)

        self.numButton.clicked.connect(self.on_click_numPoints)

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
        hboxButton.addWidget(self.naiveButton)
        hboxButton.addWidget(self.DLTButton)
        hboxButton.addWidget(self.DLTNButton)

#        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

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

        #self.lineEdit1 = QtWidgets.QLineEdit(placeholderText="Unesite broj tačaka:")

        self.label1 = QtWidgets.QLabel("Pogledajte u padajući meni! :)")
        #self.label1.setGeometry(QtCore.QRect(0, 0, 700, 700))
        hbox.addWidget(self.label1)

        self.label2 = QtWidgets.QLabel("")
        #self.label2.setGeometry(QtCore.QRect(700, 0, 700, 700))
        hbox.addWidget(self.label2)
        
        #vbox.addWidget(self.lineEdit1)        
        vbox.addLayout(hbox)      
        vbox.addLayout(hboxButton)  

        self.setLayout(vbox)
        self.show()


    def file_open(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                            '.', "Image files (*.jpg *.gif)"
        )

        imagePath = fname[0]
        self.fileName = imagePath
        pixmap = QtGui.QPixmap(imagePath)
        pixmap2 = QtGui.QPixmap("black.jpg")

    
        pixmap_resized = pixmap.scaled(700, 700, QtCore.Qt.KeepAspectRatio)
        pixmap2_resized = pixmap2.scaled(pixmap_resized.width(), pixmap_resized.height())

        self.label1.resize(pixmap_resized.width(), pixmap_resized.height())
        self.label1.setPixmap(QtGui.QPixmap(pixmap_resized))

        self.label2.resize(pixmap_resized.width(), pixmap_resized.height())
        self.label2.setPixmap(QtGui.QPixmap(pixmap2_resized))

        #self.resize(pixmap_resized.width(), pixmap_resized.height())
        self.label1.mousePressEvent = self.getPos

    def getPos(self, event):
        x = event.pos().x()
        y = event.pos().y() 

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
        x = event.pos().x()
        y = event.pos().y() 

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
        self.nPoints = int(self.numOfPoints.toPlainText())
        print("Broj tacaka: " + str(self.nPoints))

    def on_click_naive(self):
        if (len(self.xs) == self.nPoints):

            proj_width = self.label1.width()
            proj_height = self.label1.height()

            img_original = Image.open(self.fileName)
            algorithms.naive(self.xs, self.ys, self.xs_proj, self.ys_proj, proj_width, proj_height, img_original)

            print("zavrsio je naivni!")
            # try:
            #     os.remove("algo.bmp")
            # except: pass

            pixmap = QtGui.QPixmap("out.bmp")
            pixmap_resized = pixmap.scaled(proj_width, proj_height)
            self.label2.setPixmap(QtGui.QPixmap(pixmap_resized))

        else:
            pass  

    # TODO 
    def on_click_dlt(self):
        if (len(self.xs) == self.nPoints):

            proj_width = self.label1.width()
            proj_height = self.label1.height()

            img_original = Image.open(self.fileName)
            algorithms.dlt(self.xs, self.ys, self.xs_proj, self.ys_proj, proj_width, proj_height, img_original)

            print("zavrsio je dlt!")
            
            # try:
            #     os.remove("algo.bmp")
            # except: pass

            pixmap = QtGui.QPixmap("out.bmp")
            pixmap_resized = pixmap.scaled(proj_width, proj_height)
            self.label2.resize(proj_width, proj_height)
            self.label2.setPixmap(QtGui.QPixmap(pixmap_resized))
        else:
            pass  


App = QtWidgets.QApplication(sys.argv)
window = Window()
sys.exit(App.exec())