# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created: Fri May  8 12:48:59 2015
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
        Form.resize(239, 492)
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
        self.formLayout.setWidget(3, QtGui.QFormLayout.SpanningRole, self.pushButton)
        self.pushButton_6 = QtGui.QPushButton(Form)
        self.pushButton_6.setObjectName(_fromUtf8("pushButton_6"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.SpanningRole, self.pushButton_6)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(6, QtGui.QFormLayout.SpanningRole, spacerItem)
        self.pushButton_2 = QtGui.QPushButton(Form)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.SpanningRole, self.pushButton_2)
        self.pushButton_3 = QtGui.QPushButton(Form)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.SpanningRole, self.pushButton_3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(9, QtGui.QFormLayout.SpanningRole, spacerItem1)
        self.progress = QtGui.QProgressBar(Form)
        self.progress.setProperty("value", 0)
        self.progress.setObjectName(_fromUtf8("progress"))
        self.formLayout.setWidget(10, QtGui.QFormLayout.SpanningRole, self.progress)
        self.startFreq = QtGui.QSpinBox(Form)
        self.startFreq.setMinimum(50)
        self.startFreq.setMaximum(100000)
        self.startFreq.setProperty("value", 150)
        self.startFreq.setObjectName(_fromUtf8("startFreq"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.startFreq)
        self.stopFreq = QtGui.QSpinBox(Form)
        self.stopFreq.setMinimum(60)
        self.stopFreq.setMaximum(100000)
        self.stopFreq.setProperty("value", 1500)
        self.stopFreq.setObjectName(_fromUtf8("stopFreq"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.stopFreq)
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.msg = QtGui.QLabel(Form)
        self.msg.setText(_fromUtf8(""))
        self.msg.setObjectName(_fromUtf8("msg"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.SpanningRole, self.msg)
        self.stepFreq = QtGui.QDoubleSpinBox(Form)
        self.stepFreq.setProperty("value", 1.0)
        self.stepFreq.setObjectName(_fromUtf8("stepFreq"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.stepFreq)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.startSweep)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.showData)
        QtCore.QObject.connect(self.pushButton_3, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.clearData)
        QtCore.QObject.connect(self.pushButton_6, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.stopSweep)
        QtCore.QObject.connect(self.startFreq, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), Form.setStartFreq)
        QtCore.QObject.connect(self.stopFreq, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), Form.setStopFreq)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.pushButton.setText(_translate("Form", "Start Frequency Sweep", None))
        self.pushButton_6.setText(_translate("Form", "Stop Frequency Sweep", None))
        self.pushButton_2.setText(_translate("Form", "Display Data", None))
        self.pushButton_3.setText(_translate("Form", "Clear", None))
        self.label.setText(_translate("Form", "Start Freq", None))
        self.label_2.setText(_translate("Form", "Stop Freq", None))
        self.label_3.setText(_translate("Form", "Step Size", None))

