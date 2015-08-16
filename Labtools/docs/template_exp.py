# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'exp.ui'
#
# Created: Fri Jan  9 15:22:25 2015
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(787, 514)
        MainWindow.setStyleSheet(_fromUtf8(" QPushButton{ background-image: url(:/images/bt_01_off.png);}\n"
" QPushButton:pressed {background-image:url(:/images/bt_01_on.png);}\n"
"QFrame{background-color: rgb(21, 107, 113);}\n"
" QDockWidget::title {\n"
"        background-color: lightgray;\n"
"       padding-left: 10px;\n"
"       padding-top: 4px;\n"
"    }\n"
"border-color: rgb(29, 122, 162);\n"
""))
        MainWindow.setDocumentMode(False)
        MainWindow.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks|QtGui.QMainWindow.AnimatedDocks)
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vertical_splitter = QtGui.QSplitter(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vertical_splitter.sizePolicy().hasHeightForWidth())
        self.vertical_splitter.setSizePolicy(sizePolicy)
        self.vertical_splitter.setOrientation(QtCore.Qt.Vertical)
        self.vertical_splitter.setObjectName(_fromUtf8("vertical_splitter"))
        self.graph_splitter = QtGui.QSplitter(self.vertical_splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graph_splitter.sizePolicy().hasHeightForWidth())
        self.graph_splitter.setSizePolicy(sizePolicy)
        self.graph_splitter.setMinimumSize(QtCore.QSize(10, 10))
        self.graph_splitter.setMaximumSize(QtCore.QSize(0, 0))
        self.graph_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.graph_splitter.setOpaqueResize(True)
        self.graph_splitter.setObjectName(_fromUtf8("graph_splitter"))
        self.output_splitter = QtGui.QSplitter(self.vertical_splitter)
        self.output_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.output_splitter.setObjectName(_fromUtf8("output_splitter"))
        self.output_area_frame = QtGui.QFrame(self.output_splitter)
        self.output_area_frame.setStyleSheet(_fromUtf8("color: rgb(255, 255, 255);"))
        self.output_area_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.output_area_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.output_area_frame.setObjectName(_fromUtf8("output_area_frame"))
        self.output_area = QtGui.QGridLayout(self.output_area_frame)
        self.output_area.setMargin(0)
        self.output_area.setObjectName(_fromUtf8("output_area"))
        self.shell_frame = QtGui.QFrame(self.output_splitter)
        self.shell_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.shell_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.shell_frame.setObjectName(_fromUtf8("shell_frame"))
        self.shell = QtGui.QGridLayout(self.shell_frame)
        self.shell.setMargin(0)
        self.shell.setObjectName(_fromUtf8("shell"))
        self.gridLayout.addWidget(self.vertical_splitter, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 787, 25))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuAdd_Widget = QtGui.QMenu(self.menuBar)
        self.menuAdd_Widget.setObjectName(_fromUtf8("menuAdd_Widget"))
        MainWindow.setMenuBar(self.menuBar)
        self.dockWidget = QtGui.QDockWidget(MainWindow)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.dockWidget.setFont(font)
        self.dockWidget.setStyleSheet(_fromUtf8(""))
        self.dockWidget.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.dockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.vertical_frame = QtGui.QFrame(self.dockWidgetContents)
        self.vertical_frame.setMinimumSize(QtCore.QSize(100, 20))
        self.vertical_frame.setStyleSheet(_fromUtf8("QPushButton{color: rgb(255,255,255);}\n"
"QLabel{color: rgb(255,255,255);}\n"
"color: rgb(0,0,0);\n"
""))
        self.vertical_frame.setObjectName(_fromUtf8("vertical_frame"))
        self.frame_area = QtGui.QVBoxLayout(self.vertical_frame)
        self.frame_area.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.frame_area.setMargin(0)
        self.frame_area.setObjectName(_fromUtf8("frame_area"))
        self.horizontalLayout.addWidget(self.vertical_frame)
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)
        self.actionAdd_Button = QtGui.QAction(MainWindow)
        self.actionAdd_Button.setObjectName(_fromUtf8("actionAdd_Button"))
        self.actionInsert_Console = QtGui.QAction(MainWindow)
        self.actionInsert_Console.setObjectName(_fromUtf8("actionInsert_Console"))
        self.menuAdd_Widget.addAction(self.actionInsert_Console)
        self.menuBar.addAction(self.menuAdd_Widget.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionInsert_Console, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.addConsole)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Experiments", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAdd_Widget.setTitle(QtGui.QApplication.translate("MainWindow", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidget.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Controls", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd_Button.setText(QtGui.QApplication.translate("MainWindow", "Insert Console", None, QtGui.QApplication.UnicodeUTF8))
        self.actionInsert_Console.setText(QtGui.QApplication.translate("MainWindow", "Insert Console", None, QtGui.QApplication.UnicodeUTF8))

