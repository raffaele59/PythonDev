'''
Created on 22/feb/2018

@author: utente
'''

from PyQt4 import QtGui #, uic
from Tkinter import Tk

from geocontrolli_rt_dialog_descr_sql import Ui_dlgDescrAndSql


class ClsDlgDescrCtrl(QtGui.QDialog, Ui_dlgDescrAndSql):
    '''
    classdocs
    '''

    def __init__(self, testo_descriz, testo_query):
        '''
        Constructor
        '''
        QtGui.QDialog.__init__(self)
        Ui_dlgDescrAndSql.__init__(self)
        self.setupUi(self)
        self.pbCopyDescr.clicked.connect(self.copia_descriz)
        self.pbCopyQuery.clicked.connect(self.copia_query)
        self.pbCopyBoth.clicked.connect(self.copia_entrambe)
        self.pbEsciDscAndSql.clicked.connect(self.chiudi_dialog)
        
        self.testo_descriz=testo_descriz;
        self.testo_query=testo_query;
        
        self.tedDescriz.clear()
        self.tedDescriz.append(testo_descriz)
        self.tedQuerySql.clear()
        self.tedQuerySql.append(testo_query)

    def copia_descriz(self):
        """
        Copy descr. into clipboard
        """
        the_tk=Tk()
        the_tk.withdraw()
        the_tk.clipboard_clear()
        the_tk.clipboard_append(self.testo_descriz)
        the_tk.update()
        the_tk.destroy()
        
        self.tedDescriz.selectAll()
        self.labInfoDone.setText('Copiata descriz. negli appunti')

    def copia_query(self):
        """
        Copy query sql into clipboard
        """
        the_tk=Tk()
        the_tk.withdraw()
        the_tk.clipboard_clear()
        the_tk.clipboard_append(self.testo_query)
        the_tk.update()
        the_tk.destroy()
        
        self.tedQuerySql.selectAll()
        self.labInfoDone.setText('Copiata query sql negli appunti')

    def copia_entrambe(self):
        """
        Copy descr. and query sql into clipboard
        """
        the_tk=Tk()
        the_tk.withdraw()
        the_tk.clipboard_clear()
        the_tk.clipboard_append(self.testo_descriz)
        the_tk.clipboard_append('\n\n-----\n\n')
        the_tk.clipboard_append(self.testo_query)
        the_tk.update()
        the_tk.destroy()
        
        self.tedDescriz.selectAll()
        self.tedQuerySql.selectAll()
        
        self.labInfoDone.setText('Copiate descriz. e query negli appunti')

    def chiudi_dialog(self):
        """
        Exit dialog
        """
        self.close()
