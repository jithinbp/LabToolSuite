# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stream.ui'
#
# Created: Sun Jun 14 23:42:30 2015
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(276, 420)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.cmdlist = QtGui.QComboBox(Form)
        self.cmdlist.setMinimumSize(QtCore.QSize(250, 0))
        self.cmdlist.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);"))
        self.cmdlist.setEditable(True)
        self.cmdlist.setObjectName(_fromUtf8("cmdlist"))
        self.cmdlist.addItem(_fromUtf8(""))
        self.cmdlist.addItem(_fromUtf8(""))
        self.cmdlist.addItem(_fromUtf8(""))
        self.cmdlist.addItem(_fromUtf8(""))
        self.cmdlist.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.cmdlist)
        self.pushButton = QtGui.QPushButton(Form)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.stream)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.cmdlist.setItemText(0, _translate("Form", "get_average_voltage(\'CH5\')", None))
        self.cmdlist.setItemText(1, _translate("Form", "get_freq(\'ID1\')", None))
        self.cmdlist.setItemText(2, _translate("Form", "get_high_freq(\'ID1\')", None))
        self.cmdlist.setItemText(3, _translate("Form", "DutyCycle(\'ID1\')[1]", None))
        self.cmdlist.setItemText(4, _translate("Form", "MeasureInterval(\'ID1\',\'ID2\',\'rising\',\'rising\')", None))
        self.pushButton.setText(_translate("Form", "Monitor", None))

