# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'geocontrolli_rt_dialog_descr_sql.ui'
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

class Ui_dlgDescrAndSql(object):
    def setupUi(self, dlgDescrAndSql):
        dlgDescrAndSql.setObjectName(_fromUtf8("dlgDescrAndSql"))
        dlgDescrAndSql.setWindowModality(QtCore.Qt.ApplicationModal)
        dlgDescrAndSql.resize(433, 539)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("Main/GeoControlli.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dlgDescrAndSql.setWindowIcon(icon)
        dlgDescrAndSql.setModal(True)
        self.tedDescriz = QtGui.QTextEdit(dlgDescrAndSql)
        self.tedDescriz.setGeometry(QtCore.QRect(10, 30, 411, 191))
        self.tedDescriz.setObjectName(_fromUtf8("tedDescriz"))
        self.tedQuerySql = QtGui.QTextEdit(dlgDescrAndSql)
        self.tedQuerySql.setGeometry(QtCore.QRect(10, 270, 411, 191))
        self.tedQuerySql.setObjectName(_fromUtf8("tedQuerySql"))
        self.label = QtGui.QLabel(dlgDescrAndSql)
        self.label.setGeometry(QtCore.QRect(20, 10, 81, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(dlgDescrAndSql)
        self.label_2.setGeometry(QtCore.QRect(20, 250, 81, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.pbCopyDescr = QtGui.QPushButton(dlgDescrAndSql)
        self.pbCopyDescr.setGeometry(QtCore.QRect(310, 230, 110, 23))
        self.pbCopyDescr.setObjectName(_fromUtf8("pbCopyDescr"))
        self.pbCopyQuery = QtGui.QPushButton(dlgDescrAndSql)
        self.pbCopyQuery.setGeometry(QtCore.QRect(310, 470, 110, 23))
        self.pbCopyQuery.setObjectName(_fromUtf8("pbCopyQuery"))
        self.pbCopyBoth = QtGui.QPushButton(dlgDescrAndSql)
        self.pbCopyBoth.setGeometry(QtCore.QRect(110, 500, 101, 31))
        self.pbCopyBoth.setObjectName(_fromUtf8("pbCopyBoth"))
        self.pbEsciDscAndSql = QtGui.QPushButton(dlgDescrAndSql)
        self.pbEsciDscAndSql.setGeometry(QtCore.QRect(210, 500, 101, 31))
        self.pbEsciDscAndSql.setObjectName(_fromUtf8("pbEsciDscAndSql"))
        self.labInfoDone = QtGui.QLabel(dlgDescrAndSql)
        self.labInfoDone.setGeometry(QtCore.QRect(20, 470, 161, 21))
        self.labInfoDone.setText(_fromUtf8(""))
        self.labInfoDone.setObjectName(_fromUtf8("labInfoDone"))

        self.retranslateUi(dlgDescrAndSql)
        QtCore.QMetaObject.connectSlotsByName(dlgDescrAndSql)

    def retranslateUi(self, dlgDescrAndSql):
        dlgDescrAndSql.setWindowTitle(_translate("dlgDescrAndSql", "Descrizione e Query SQL", None))
        self.label.setText(_translate("dlgDescrAndSql", "Descrizione:", None))
        self.label_2.setText(_translate("dlgDescrAndSql", "Query SQL:", None))
        self.pbCopyDescr.setText(_translate("dlgDescrAndSql", "Copia descrizione", None))
        self.pbCopyQuery.setText(_translate("dlgDescrAndSql", "Copia query SQL", None))
        self.pbCopyBoth.setText(_translate("dlgDescrAndSql", "Copia entrambe", None))
        self.pbEsciDscAndSql.setText(_translate("dlgDescrAndSql", "Esci", None))

