# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'transient.ui'
#
# Created: Tue Jan  6 12:50:15 2015
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(223, 420)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.pushButton = QtGui.QPushButton(Form)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.pushButton)
        self.pushButton_3 = QtGui.QPushButton(Form)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.pushButton_3)
        self.msg = QtGui.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.msg.setFont(font)
        self.msg.setText(_fromUtf8(""))
        self.msg.setObjectName(_fromUtf8("msg"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.SpanningRole, self.msg)
        self.CLabel = QtGui.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.CLabel.setFont(font)
        self.CLabel.setText(_fromUtf8(""))
        self.CLabel.setObjectName(_fromUtf8("CLabel"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.SpanningRole, self.CLabel)
        self.LLabel = QtGui.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.LLabel.setFont(font)
        self.LLabel.setText(_fromUtf8(""))
        self.LLabel.setObjectName(_fromUtf8("LLabel"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.SpanningRole, self.LLabel)
        self.RLabel = QtGui.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.RLabel.setFont(font)
        self.RLabel.setText(_fromUtf8(""))
        self.RLabel.setObjectName(_fromUtf8("RLabel"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.SpanningRole, self.RLabel)
        self.LCLabel = QtGui.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.LCLabel.setFont(font)
        self.LCLabel.setText(_fromUtf8(""))
        self.LCLabel.setObjectName(_fromUtf8("LCLabel"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.SpanningRole, self.LCLabel)
        self.ILabel = QtGui.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.ILabel.setFont(font)
        self.ILabel.setText(_fromUtf8(""))
        self.ILabel.setObjectName(_fromUtf8("ILabel"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.SpanningRole, self.ILabel)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(9, QtGui.QFormLayout.SpanningRole, spacerItem)
        self.pushButton_2 = QtGui.QPushButton(Form)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.formLayout.setWidget(10, QtGui.QFormLayout.SpanningRole, self.pushButton_2)
        self.indicator = QtGui.QLabel(Form)
        self.indicator.setMinimumSize(QtCore.QSize(0, 15))
        self.indicator.setMaximumSize(QtCore.QSize(16777215, 10))
        self.indicator.setObjectName(_fromUtf8("indicator"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.SpanningRole, self.indicator)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.showData)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.run)
        QtCore.QObject.connect(self.pushButton_3, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.fit)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Form", "Toggle OD1", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Form", "Fit selected region", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Form", "Log data to Console", None, QtGui.QApplication.UnicodeUTF8))
        self.indicator.setText(QtGui.QApplication.translate("Form", "Output state", None, QtGui.QApplication.UnicodeUTF8))

