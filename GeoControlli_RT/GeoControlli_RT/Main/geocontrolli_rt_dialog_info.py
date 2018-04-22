# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'geocontrolli_rt_dialog_info.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_InfoDialog(object):
    def setupUi(self, InfoDialog):
        InfoDialog.setObjectName(_fromUtf8("InfoDialog"))
        InfoDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        InfoDialog.resize(381, 281)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("Main/GeoControlli.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        InfoDialog.setWindowIcon(icon)
        InfoDialog.setModal(True)
        self.labVersion = QtGui.QLabel(InfoDialog)
        self.labVersion.setEnabled(True)
        self.labVersion.setGeometry(QtCore.QRect(7, 184, 361, 20))
        self.labVersion.setAlignment(QtCore.Qt.AlignCenter)
        self.labVersion.setObjectName(_fromUtf8("labVersion"))
        self.pbInfoExit = QtGui.QPushButton(InfoDialog)
        self.pbInfoExit.setGeometry(QtCore.QRect(190, 220, 121, 31))
        self.pbInfoExit.setObjectName(_fromUtf8("pbInfoExit"))
        self.labInfoImg = QtGui.QLabel(InfoDialog)
        self.labInfoImg.setGeometry(QtCore.QRect(13, 20, 351, 151))
        self.labInfoImg.setFrameShape(QtGui.QFrame.Box)
        self.labInfoImg.setFrameShadow(QtGui.QFrame.Sunken)
        self.labInfoImg.setText(_fromUtf8(""))
        self.labInfoImg.setPixmap(QtGui.QPixmap(_fromUtf8(":/gcrt_/geocontrolli_rt_info.bmp")))
        self.labInfoImg.setScaledContents(True)
        self.labInfoImg.setObjectName(_fromUtf8("labInfoImg"))
        self.pbInfoManual = QtGui.QPushButton(InfoDialog)
        self.pbInfoManual.setGeometry(QtCore.QRect(60, 220, 121, 31))
        self.pbInfoManual.setObjectName(_fromUtf8("pbInfoManual"))
        self.label_2 = QtGui.QLabel(InfoDialog)
        self.label_2.setEnabled(False)
        self.label_2.setGeometry(QtCore.QRect(10, 260, 361, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(InfoDialog)
        QtCore.QMetaObject.connectSlotsByName(InfoDialog)

    def retranslateUi(self, InfoDialog):
        InfoDialog.setWindowTitle(_translate("InfoDialog", "Informazioni", None))
        self.labVersion.setText(_translate("InfoDialog", " ", None))
        self.pbInfoExit.setToolTip(_translate("InfoDialog", "Esce dal programma", None))
        self.pbInfoExit.setText(_translate("InfoDialog", "Esci", None))
        self.pbInfoManual.setToolTip(_translate("InfoDialog", "Apre il file GeoControlli_RT_GuidaUtente.pdf", None))
        self.pbInfoManual.setText(_translate("InfoDialog", "Apri guida utente", None))
        self.label_2.setText(_translate("InfoDialog", "Sviluppato da Virgilio Cima per Regione Toscana", None))

import geocontrolli_rt_rc
