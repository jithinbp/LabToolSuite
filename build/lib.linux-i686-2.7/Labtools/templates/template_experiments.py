# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'template_experiments.ui'
#
# Created: Fri May  8 13:50:29 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(237, 512)
        MainWindow.setStyleSheet(_fromUtf8(" QPushButton{ background-image: url(:/images/bt_01_off.png);\n"
"color: rgb(255, 255, 255);}\n"
" QPushButton:pressed {background-image:url(:/images/bt_01_on.png);}\n"
"QFrame,QListWidget{background-color: rgb(21, 107, 113);}\n"
"\n"
"QLabel,QRadioButton,QCheckBox {color: rgb(255, 255, 255);}\n"
"QLabel,QRadioButton,QCheckBox{background-color: rgba(0,0,0, 0);color: rgb(0,0,0);}\n"
"QComboBox{background-color: rgba(255,255,255, 100);color: rgb(0,0,0);}\n"
"\n"
"border-color: rgb(29, 122, 162);\n"
"\n"
""))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setStyleSheet(_fromUtf8("background-color: rgb(21, 107, 113);"))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.filenames = QtGui.QListWidget(self.centralwidget)
        self.filenames.setObjectName(_fromUtf8("filenames"))
        self.verticalLayout.addWidget(self.filenames)
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 237, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.run_exp)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.pushButton.setText(_translate("MainWindow", "RUN Experiment", None))

