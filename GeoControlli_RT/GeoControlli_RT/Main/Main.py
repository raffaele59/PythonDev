# coding=utf-8
'''
Created on 23/giu/2017

@author: Raffaele&Virgilio Factory
'''
from os.path import dirname, abspath, isfile, normpath
from os import startfile #subprocess
import datetime
from ClsDbService import ClsDbService
from ClsDataToPdf import ClsDataToPdf
from ClsModDocToPdf import ClsModDocToPdf
from ClsSessione import  ClsSessione
from PyQt4 import QtGui #, uic
#import PyQt4.QtCore
from PyQt4.QtGui import QFileDialog, QMessageBox, QInputDialog, QStandardItemModel, QTreeWidgetItem, QColor, QTableWidgetItem # , QGraphicsView, QAction, QMenu, qApp, QKeySequence, QShortcut, QStandardItem
#from PyQt4.QtCore import *
from PyQt4.QtCore import Qt, QString #, QVariant
from _winreg import CreateKey, HKEY_CURRENT_USER, REG_SZ, SetValue, OpenKey, EnumValue, CloseKey
from Tkinter import Tk
from collections import OrderedDict
#from reportlab.pdfgen import canvas

#import sys
#import inspect
#import __main__

#qt_main_dlg = "geocontrolli_rt_dialog_base.ui" # Enter file here.
#Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_main_dlg) 
from geocontrolli_rt_dialog_base import Ui_MainWindow
from geocontrolli_rt_dialog_info import Ui_InfoDialog

from ClsDlgDescrCtrl import ClsDlgDescrCtrl

STR_VERS='Beta - marzo 2018'

class InfoDialog(QtGui.QDialog, Ui_InfoDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        Ui_InfoDialog.__init__(self)
        self.setupUi(self)
        #self.setModal(True)
        #self.pbInfoExit.clicked.connect(self.info_exit)
        #self.pbInfoManual.clicked.connect(self.info_open_manual)
        self.labVersion.setText('Versione '+STR_VERS)
        
    #def info_exit(self):
    #    QMessageBox.information(self,"Info","info_exit",QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton) 
        
    #def info_open_manual(self):
    #    QMessageBox.information(self,"Info","info_open_manual",QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton) 

class GeoControlli_RT(QtGui.QMainWindow, Ui_MainWindow): #
    def __init__(self, parent=None):
        #initialize ui
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.trwControls.setContextMenuPolicy(Qt.CustomContextMenu)
        self.trwControls.customContextMenuRequested.connect(self.on_context_menu)
        self.tabWidget.setCurrentIndex(0)
        self.popMenu = QtGui.QMenu(self)
        self.popMenu.addAction('&Copia comando SQL', self.copy_sql_cmd) # , Qt.CTRL + Qt.Key_S) # , QKeySequence('Ctrl+W')
        self.popMenu.addAction('Copia &descrizione controllo', self.copy_doc_cmd) # , Qt.CTRL + Qt.Key_S) # , QKeySequence('Ctrl+W')
        self.popMenu.addAction('&Informazioni sul controllo', self.apri_info_ctrl)
        self.pbTestSpatial.hide()
        self.tbvSessions.hide()
        #self.pbInfo.hide()
        self.setWindowIcon(QtGui.QIcon("GeoControlli.ico"))
        
        self.infoDlg=InfoDialog()
        self.infoUi = Ui_InfoDialog()
        self.infoUi.setupUi(self.infoDlg)
        self.infoUi.pbInfoExit.clicked.connect(self.info_dialog_exit)
        self.infoUi.pbInfoManual.clicked.connect(self.info_dialog_open_manual)

        #classes
        self.db_service= ClsDbService()

        #initialize variables
        self.cur_codctrl=""
        self.dict_controls=OrderedDict() # = {}
        self.lst_dati_sess=[]
        self.err_msg=""
        self.db_config_name=""
        self.db_deliv_name=""
        self.db_log_name=""
       
        #registry
        self.registry_root_key=HKEY_CURRENT_USER
        self.registry_key_name="Software\GeoControlli_RT" # poi creare chiave dentro Software con due passi invece di uno - nome programma come costante?
        [self.db_config_name, self.db_deliv_name, self.db_log_name]=self.registry_to_names()
        
        #config. db
        self.leDbConfig.setText(self.db_config_name)
        self.pbOpenDbConfig.clicked.connect(self.select_config_name)
        self.leDbConfig.textChanged.connect(self.db_filename_changed)
        
        #delivery db
        self.leDbDelivery.setText(self.db_deliv_name)
        self.pbOpenDbDelivery.clicked.connect(self.select_delivery_name)
        self.leDbDelivery.textChanged.connect(self.db_filename_changed)
        
        #log db
        self.leDbLog.setText(self.db_log_name)
        self.leDbLog.textChanged.connect(self.db_filename_changed)
        self.pbOpenDbLog.clicked.connect(self.select_log_name)
        
        #sessions and errors output
        self.pbReportSessione.clicked.connect(self.report_sessione)
        self.pbOutTables.clicked.connect(self.create_out_err_tbls)
        self.pbEmptyLogBox.clicked.connect(self.empty_log_out_box)
        self.tbwSessions.itemSelectionChanged.connect(self.enable_session_buttons)
        self.pbOutTables.setEnabled(False)
        self.pbReportSessione.setEnabled(False)
        self.cbOkResultsOut.setEnabled(False)
        self.cbDescrizOut.setEnabled(False)
        self.def_rpt_name=''
        self.def_docmod_name=''

        #save/load checks
        self.pbSaveChkCtrl.clicked.connect(self.save_checks_ctrl)
        self.pbLoadChkCtrl.clicked.connect(self.load_checks_ctrl)
        
        #connections and executions
        self.pbConnectDb.clicked.connect(self.connect_databases)
        self.pbExecuteControls.clicked.connect(self.execute_controls)
        self.pbTestSpatial.clicked.connect(self.test_spquery)
        if (self.leDbConfig.text()== "" or self.leDbDelivery.text()=="" or self.leDbLog.text()=="") : self.pbConnectDb.setEnabled(False)
        
        #contexts
        self.cbContext.currentIndexChanged.connect(self.context_changed)
        
        #tools (temp)
        self.pbCreateEmptyDbLog.clicked.connect(self.create_empty_db_log)
        self.pbCreateModDoc.clicked.connect(self.create_model_docum)
        self.pbInfo.clicked.connect(self.info_dialog_show)
         
        #exit
        self.pbExit.clicked.connect(self.close) # self.exit_from_program non chiama closeEvent
        
        # commenti

        #self.setFixedSize(self.width(),self.height())
        # create tree view context menu
        #self.trwControls.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.popMenu.addAction(QtGui.QAction('Copia comando SQL', self))
        #self.popMenu.addAction(QtGui.QAction('Verifica controllo', self))
        #self.popMenu.addSeparator()
        #self.popMenu.addAction(QtGui.QAction('Altro ... ', self))  

        #self.actionCpSqlCmd = QAction(('&Copia comando SQL'), self)
        ##self.actionCpSqlCmd.setShortcut(QKeySequence('Ctrl+W'))
        ##self.connect(self.actionCpSqlCmd,SIGNAL("triggered()"),self.copy_sql_cmd)
        #self.actionCpSqlCmd.triggered.connect(self.copy_sql_cmd)
        #self.popMenu.addAction(self.actionCpSqlCmd)
        
        #self.keyCpSqlCmd=QShortcut(QKeySequence('Ctrl+W'),self.trwControls) # self.popMenu
        #self.keyCpSqlCmd.activated.connect(self.copy_sql_cmd)

        # add menu to the tree view      
        # verificare se si riesce a connettere direttamente il menu contestuale
        # all'albero, e non usare la cur_codctrl "globale"
        #connect(ui->treeView, SIGNAL(customContextMenuRequested(const QPoint &)), this, SLOT(onCustomContextMenu(const QPoint &)));
        
        
        #self.vista_graf = QGraphicsView()
        
#        print sys.argv[0]
#        print'ok1'
#        print __main__.__file__
#        print'ok2'

    # funzioni
        
    def select_config_name(self):
        path_name=""
        if (self.leDbConfig.text()!="") : path_name=dirname(abspath(self.leDbConfig.text()))
        file_name=QFileDialog.getOpenFileName(self, "Selezionare il db di configurazione",path_name, "*.sqlite")
        if (file_name != "") : self.leDbConfig.setText(file_name)
#         self.pbConnectDb.setEnabled(True)
#         if (self.leDbConfig.text()== "" or self.leDbDelivery.text()=="" or self.leDbLog.text()=="") : self.pbConnectDb.setEnabled(False)
        
    def select_delivery_name(self):
        path_name=""
        if (self.leDbDelivery.text()!="") : path_name=dirname(abspath(self.leDbDelivery.text()))
        file_name=QFileDialog.getOpenFileName(self, "Selezionare il db dei dati mda controllare",path_name, "Spatialite db (*.sqlite *.db);;Tutti i file (*.*)")
        if (file_name != "") : self.leDbDelivery.setText(file_name)
#         self.pbConnectDb.setEnabled(True)
#         if (self.leDbConfig.text()== "" or self.leDbDelivery.text()=="" or self.leDbLog.text()=="") : self.pbConnectDb.setEnabled(False)
        
    def select_log_name(self):
        path_name=""
        if (self.leDbLog.text()!="") : path_name=dirname(abspath(self.leDbLog.text()))
        file_name=QFileDialog.getOpenFileName(self, "Selezionare il database di log (output)",path_name, "Spatialite db (*.sqlite *.db);;Tutti i file (*.*)")
        if (file_name != "") : self.leDbLog.setText(file_name)
#         self.pbConnectDb.setEnabled(True)
#         if (self.leDbConfig.text()== "" or self.leDbDelivery.text()=="" or self.leDbLog.text()=="") : self.pbConnectDb.setEnabled(False)

    def db_filename_changed(self):
        is_connect_ok=True
        
        cur_deliv_name=str(self.leDbDelivery.text())
        is_file_ok=False
        if cur_deliv_name.strip()!="" and cur_deliv_name is not None:
            if isfile(cur_deliv_name): is_file_ok=True
        if is_file_ok:
            label_color='color: rgb(0,0,0);'
        else:
            label_color='color: rgb(255,0,0);'
            is_connect_ok=False
        self.laDbDelivery.setStyleSheet(label_color)
        
        cur_log_name=str(self.leDbLog.text())
        is_file_ok=False
        if cur_log_name.strip()!="" and cur_log_name is not None:
            if isfile(cur_log_name): is_file_ok=True
        if is_file_ok:
            label_color='color: rgb(0,0,0);'
        else:
            label_color='color: rgb(255,0,0);'
            is_connect_ok=False
        self.laDbLog.setStyleSheet(label_color)
        
        cur_config_name=str(self.leDbConfig.text())
        is_file_ok=False
        if cur_config_name.strip()!="" and cur_config_name is not None:
            if isfile(cur_config_name): is_file_ok=True
        if is_file_ok:
            label_color='color: rgb(0,0,0);'
        else:
            label_color='color: rgb(255,0,0);'
            is_connect_ok=False
        self.laDbConfig.setStyleSheet(label_color)

        if (self.leDbConfig.text()== "" or self.leDbDelivery.text()=="" or self.leDbLog.text()=="") : is_connect_ok=False
        
        self.pbConnectDb.setEnabled(is_connect_ok)
        self.pbExecuteControls.setEnabled(False)
        
    def connect_databases(self):
        try:
            self.db_config_name=str(self.leDbConfig.text()).strip()
            self.db_deliv_name=str(self.leDbDelivery.text()).strip()
            self.db_log_name=str(self.leDbLog.text()).strip()

            # temporary
            self.db_service.db_connect(self.db_config_name, self.db_deliv_name, self.db_log_name)
            if self.db_service.db_status!=0 :
                QMessageBox.critical(self, "Errore", "Errore nell'apertura del database: {}".format(self.db_service.err_msg), 
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
                return
            # lst_controls=self.db_service.get_lst_controls() 
            # sourcename=str(self.leDbDelivery.text())
            
            #QMessageBox.information(self,"Connessione database","Connessione avvenuta",QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            self.out_message("Connessione ai database avvenuta")
            
            self.pbSaveChkCtrl.setEnabled(True)
            self.pbLoadChkCtrl.setEnabled(True)
            #self.pbTestSpatial.setEnabled(True) 

            prev_context=''
            prev_deliver=''
            prev_operator=''
            prev_note=''
            
            prev_info=self.db_service.get_last_sess_info()
            if len(prev_info)>0:
                #id_sess=prev_info['ID_SESS']
                prev_context=prev_info['COD_CTS']
                prev_deliver=prev_info['CONSEGNA']
                prev_operator=prev_info['OPERATORE']
                prev_note=prev_info['NOTE']
            
            cur_deliver=str(self.leDelivName.text())
            if len(cur_deliver)<1:
                cur_deliver=prev_deliver
                self.leDelivName.setText(cur_deliver)
            
            cur_operator=str(self.leOperator.text())
            if len(cur_operator)<1:
                cur_operator=prev_operator
                self.leOperator.setText(cur_operator)
            
            cur_note=str(self.leNote.text())
            if len(cur_note)<1:
                cur_note=prev_note
                self.leNote.setText(cur_note)
            
            lst_contexts=self.db_service.get_lst_contexts()
            self.cbContext.clear()
            idxSel=0
            conta_cicli=0
            for context in lst_contexts:
                self.cbContext.addItem(context[0]+" - "+context[1],context[0])
                if context[0]==prev_context: idxSel=conta_cicli
                conta_cicli=conta_cicli+1
            self.cbContext.setCurrentIndex(idxSel)
            
            self.context_changed()
        
            self.pbExecuteControls.setEnabled(True)
            
            db_versions=self.db_service.get_versions()
            if db_versions:
                self.labSqliteVers.setText('Sqlite3 version: '+db_versions[0])
                self.labSpatialiteVers.setText('Spatialite version: '+db_versions[1])

        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore nella connessione del database: {}".format(e.message), 
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
#             msg_box = QMessageBox()
#             msg_box.setText("Error opening databases: {}".format(e.message))
#             msg_box.setIcon(QMessageBox.Critical)
#             msg_box.addButton(QMessageBox.Ok)
#             ret = msg_box.exec_()  

    def crea_rep_sessione(self, id_sessione, rpt_name):
        try:
            sess=self.db_service.load_session(id_sessione)
            if self.db_service.db_status!=0:
                QMessageBox.critical(self, "Errore", "Errore in recupero dati sessione: {}".format(self.db_service.err_msg), QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
                return
            lst_dict_sql=self.db_service.create_report_list(id_sessione)
            
            lst_num_ctrl=self.db_service.conta_ctrl_sessione(id_sessione)   #[num_ctrl_totali,num_ctrl_eseguiti]

            lst_intest=[]
            lst_intest.append({'TESTO' : u'CONTROLLI DI QUALITÀ ' + sess.cod_cts, 'STILE' : 'Title', 'INDENT_MM' : 0, 'BELOW_MM' : 10}) #A\'
            lst_intest.append({'TESTO' : 'Data creazione report: ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M'), 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 0}) #str(datetime.datetime.now())
            
            lst_rif_dati=[]
            lst_rif_dati.append({'TESTO' : 'Dati sottoposti a controllo:', 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 0})
            lst_rif_dati.append({'TESTO' : sess.path_dat, 'STILE' : 'Bullet', 'INDENT_MM' : 5, 'BELOW_MM' : 0})
            lst_rif_dati.append({'TESTO' : 'DB configurazione:', 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 0})
            lst_rif_dati.append({'TESTO' : sess.path_cfg, 'STILE' : 'Bullet', 'INDENT_MM' : 5, 'BELOW_MM' : 0})
            lst_rif_dati.append({'TESTO' : 'DB Log risultati:', 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 0})
            lst_rif_dati.append({'TESTO' : sess.path_log, 'STILE' : 'Bullet', 'INDENT_MM' : 5, 'BELOW_MM' : 0})

            lst_info_sess=[]
            lst_info_sess.append({'TESTO' : 'Consegna:', 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 0})
            lst_info_sess.append({'TESTO' : sess.consegna, 'STILE' : 'Bullet', 'INDENT_MM' : 5, 'BELOW_MM' : 0})
            lst_info_sess.append({'TESTO' : 'Operatore:', 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 0})
            lst_info_sess.append({'TESTO' : sess.operatore, 'STILE' : 'Bullet', 'INDENT_MM' : 5, 'BELOW_MM' : 0})
            lst_info_sess.append({'TESTO' : 'Note:', 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 0})
            lst_info_sess.append({'TESTO' : sess.note, 'STILE' : 'Bullet', 'INDENT_MM' : 5, 'BELOW_MM' : 0})
            lst_info_sess.append({'TESTO' : 'N. sessione:', 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 0})
            lst_info_sess.append({'TESTO' : str(id_sessione), 'STILE' : 'Bullet', 'INDENT_MM' : 5, 'BELOW_MM' : 0})
            
            if self.db_service.db_status!=0:
                QMessageBox.critical(self, "Errore", "Errore in caricamento controlli sessione: {}".format(self.db_service.err_msg), QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
                return
            # fields=tuple(zip(lst_dict_sql[0].keys(), lst_dict_sql[0].keys()))
            fields=tuple(zip(("DES_GRP", "COD_CTRL", "DES_CTRL","ESITO_CTRL"),("Gruppo", "Codice","Descrizione","Esito")))
            #logo_rt='logoRT.jpg' # .gif
            #doc = ClsDataToPdf(lst_intest,fields, lst_dict_sql, title=sess.cod_cts + ': Controlli sessione ' + str(sess.id_sessione),logo=logo_rt)
            logo_e_intestaz=self.get_logo_e_intestaz()
            doc = ClsDataToPdf(lst_intest, lst_rif_dati, lst_info_sess, fields, lst_dict_sql, lst_num_ctrl, out_if_ok=self.cbOkResultsOut.isChecked(), descr_out=self.cbDescrizOut.isChecked(), logo=logo_e_intestaz[0], intestaz=logo_e_intestaz[1]) #logo=logo_rt
            doc.export(rpt_name)            

        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore in creazione report controlli sessione: {}".format(e.message), QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            
    def get_logo_e_intestaz(self):
        file_path=dirname(self.db_config_name)+'/'
        file_logo=file_path+'GeoControlli_RT_logo_utente.jpg'
        file_intestaz=file_path+'GeoControlli_RT_intestaz_utente.txt'
        if not isfile(file_logo): file_logo=None
        if not isfile(file_intestaz): file_intestaz=None
        return [file_logo,file_intestaz]

    def test_spquery(self):
#             c = canvas.Canvas("hello.pdf")
#             c.drawString(100,750,"Welcome to Reportlab!")
#             c.save()

#         try:
#             area=self.db_service.test_spatial_fun()
#             if self.db_service.db_status!=0 :
#                 QMessageBox.critical(self, "Data base error", "Error executing spatial query: {}".format(self.db_service.err_msg), 
#                                      QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
#                 return
#             QMessageBox.information(self,"Test query","Spatial query execution completed",QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
#             self.txtbResults.append(str(area))
#             
#         except Exception as e:
#             QMessageBox.critical(self, "Error", "Error in executing spatial query test: {}".format(e.message), 
#                                      QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)

        dummy=0
        
    def context_changed(self):
        self.load_controls()
        self.load_dati_sess()
        
    def load_controls(self):
        try:
            cod_cts=str(self.cbContext.itemData(self.cbContext.currentIndex()).toString())
            #cod_descr_cts=str(self.cbContext.currentText()) #"CTR45"
            #idxSpc=cod_descr_cts.find(" ")
            #if idxSpc<1:
            #    QMessageBox.critical(self, "Errore", "Errore nella lettura del contesto", 
            #                         QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            #    return
            #cod_cts=cod_descr_cts[0:idxSpc]
            
            self.dict_controls.clear();
            self.db_service.fill_dict_controls(cod_cts,self.dict_controls)
            if self.db_service.db_status!=0 :
                QMessageBox.critical(self, "Errore", "Errore nella lettura dei controlli dal database: {}".format(self.db_service.err_msg), 
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
                return
            self.build_sql_query(self.dict_controls)
            self.build_descr_mod(self.dict_controls)
            self.build_descr_ctrl(self.dict_controls)
#             dict_controls=self.db_service.get_dict_controls()
#             if self.db_service.db_status!=0 :
#                 QMessageBox.critical(self, "Data base error", "Error reading controls from database: {}".format(self.db_service.err_msg), 
#                                      QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
#                 return
            view_model = QStandardItemModel()
            view_model.setColumnCount(3)
            header_names = []
            header_names.append("Nome")
            header_names.append("Descrizione")
            header_names.append("Sql statement")
            view_model.setHorizontalHeaderLabels(header_names)   

            # Tree view perspective
            # populate the tree view
            self.trwControls.clear()
            parent_cts=QTreeWidgetItem(self.trwControls)
            parent_cts.setText(0,cod_cts)
            parent_cts.setFlags(parent_cts.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            prev_cat=""
            prev_grp=""
            for ctrl in self.dict_controls.values():
                if  ctrl['COD_CAT'].upper() != prev_cat.upper() :
                    parent_cat=QTreeWidgetItem(parent_cts)
                    parent_cat.setText(0,ctrl['DESCR_CAT'])
                    parent_cat.setFlags(parent_cat.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                    parent_cat.setCheckState(0,Qt.Checked)
                    prev_cat=ctrl['COD_CAT'].upper()                    
                if ctrl['COD_GRP'].upper() != prev_grp.upper() :
                    parent_grp=QTreeWidgetItem(parent_cat)
                    parent_grp.setText(0,ctrl['DESCR_GRP'])
                    parent_grp.setFlags(parent_grp.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                    parent_grp.setCheckState(0,Qt.Checked)
                    prev_grp=ctrl['COD_GRP'].upper()
                child=QTreeWidgetItem(parent_grp)
                child.setText(0,ctrl['COD_CTRL'])
                child.setToolTip(0,ctrl['DESCR_CTRL'])
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setCheckState(0,Qt.Checked)
            
            #QMessageBox.information(self,"Caricamento controlli","Caricamento completato",QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            self.out_message("Caricamento controlli completato")
            
            self.pbExecuteControls.setEnabled(True)
            
            #self.trwControls.expandAll()  
            invis_root = self.trwControls.invisibleRootItem()
            
            count_1 = invis_root.childCount()
            for i_1 in range(count_1):
                item_1 = invis_root.child(i_1)
                item_1.setExpanded(True)
            
                count_2 = item_1.childCount()
                for i_2 in range(count_2):
                    item_2 = item_1.child(i_2)
                    item_2.setExpanded(True)
       
        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore nel caricamento dei controlli: {}".format(e.message), 
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
    def execute_controls(self):
        try:            
            col_diff=50
            #col_verde=QColor(100,255,100)
            col_sfondo=self.trwControls.palette().color(QtGui.QPalette.Background)
            #col_sfondo=self.trwControls.background(0).color()
            val_r_sfd=col_sfondo.red()
            val_g_sfd=col_sfondo.green()
            val_b_sfd=col_sfondo.blue()
            if (val_r_sfd>col_diff): val_r_evi=val_r_sfd-col_diff
            else: val_r_evi=val_r_sfd+col_diff
            if (val_g_sfd>col_diff): val_g_evi=val_g_sfd-col_diff
            else: val_g_evi=val_g_sfd+col_diff
            if (val_b_sfd>col_diff): val_b_evi=val_b_sfd-col_diff
            else: val_b_evi=val_b_sfd+col_diff
            col_evid=QColor(val_r_evi,val_g_evi,val_b_evi)
            
            self.trwControls.setAutoFillBackground(True)
            
            # Apertura sessione di controllo
            #cod_cts=str(self.cbContext.currentText()) #"CTR45"
            cod_cts=str(self.cbContext.itemData(self.cbContext.currentIndex()).toString())
            #cod_descr_cts=str(self.cbContext.currentText()) #"CTR45"
            #idxSpc=cod_descr_cts.find(" ")
            #if idxSpc<1:
            #    QMessageBox.critical(self, "Errore", "Errore nella lettura del contesto", 
            #                         QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            #    return
            #cod_cts=cod_descr_cts[0:idxSpc]
            consegna=str(self.leDelivName.text()) #"consegna"
            operatore=str(self.leOperator.text()) #"OP01"
            note=str(self.leNote.text()) #"test"
            data_inizio=datetime.datetime.now()
            sess=ClsSessione(cod_cts, consegna, data_inizio, self.db_deliv_name,self.db_config_name, self.db_log_name, 
                             operatore, note)
            self.db_service.open_session(sess)
            if self.db_service.db_status!=0 :
                QMessageBox.critical(self, "Errore", "Errore in apertura sessione di controllo: {}".format(self.db_service.err_msg), 
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
                return

            self.out_message("Esecuzione controlli in corso")
            
            ultima_riga_vuota=False
            
            #self.trwControls.  readonly  e poi select
            invis_root = self.trwControls.invisibleRootItem()
            
            count_1 = invis_root.childCount()
            for i_1 in range(count_1):
                item_1 = invis_root.child(i_1)
                item_1.setBackgroundColor(0,col_evid)
            
                count_2 = item_1.childCount()
                for i_2 in range(count_2):
                    item_2 = item_1.child(i_2)
                    item_2.setBackgroundColor(0,col_evid)

                    is_checked=item_2.checkState(0)
                    if (is_checked):
                        self.txtbResults.append('')
                        self.txtbResults.append(item_2.text(0))
                        #self.txtbResults.append('')
                        ultima_riga_vuota=False
                
                    count_3 = item_2.childCount()
                    for i_3 in range(count_3):
                        item_3 = item_2.child(i_3)
                        item_3.setBackgroundColor(0,col_evid)

                        is_checked=item_3.checkState(0)
                        if (is_checked):
                            self.txtbResults.append('')
                            self.txtbResults.append('  '+item_3.text(0))
                            self.txtbResults.append('')
                            ultima_riga_vuota=True
                        
                        count_4=item_3.childCount()
                        for i_4 in range(count_4):
                            item_4 = item_3.child(i_4)
                            
                            #indice_cor=self.trwControls.indexFromItems(item_4)
                            #self.trwControls.selectionModel().setCurrentIndex(indice_cor)
                            item_4.setBackgroundColor(0,col_evid)

                            #self.trwControls.update() # per repaint(), ma non funziona!
                            #self.trwControls.hide()
                            #self.trwControls.show()
                            #self.vista_graf.repaint()
                            #self.vista_graf.update()
                            
                            self.tabWidget.repaint()
                            #self.tabWidget.update()
                                                
                            is_checked=item_4.checkState(0)
                            if (is_checked):
                                #self.txtbResults.append(item_4.text(0))
                                #self.txtbResults.append('')
                                cod_ctrl=str(item_4.text(0))
                                #sql_cmd=self.dict_controls[cod_ctrl]["SQL_MOD"]
                                
                                data_inizio=datetime.datetime.now()
                                id_esecuz=self.db_service.open_exec(sess, self.dict_controls[cod_ctrl], data_inizio)   
                                num_err=self.db_service.exec_ctrl(sess, id_esecuz, self.dict_controls[cod_ctrl])   
                                data_fine=datetime.datetime.now()
                                db_stato=self.db_service.db_status
                                db_err_msg=self.db_service.err_msg
                                self.db_service.close_exec(id_esecuz, data_fine,num_err,self.db_service.db_status, self.db_service.err_msg)
                                max_err=self.dict_controls[cod_ctrl]['MAX_ERR']
                                #self.txtbResults.append(sql_cmd)
                                #self.txtbResults.append('')
                                if db_stato!=0:
                                    self.txtbResults.setTextColor(QColor('red'))
                                    out_msg='    '+'errore in '+cod_ctrl+': '+db_err_msg #': stato = '+str(db_stato)+', msg = '
                                    if not ultima_riga_vuota: self.txtbResults.append('')
                                    self.txtbResults.append(out_msg)
                                    self.txtbResults.setTextColor(QColor('black'))
                                    self.txtbResults.append('')
                                    ultima_riga_vuota=True
                                else:
                                    if num_err>0: self.txtbResults.setTextColor(QColor('red'))
                                    out_msg='    '+cod_ctrl+': errori='+str(num_err)
                                    if num_err>=max_err: out_msg+=(' - ATTENZIONE: raggiunto il limite di '+str(max_err))
                                    self.txtbResults.append(out_msg)
                                    self.txtbResults.setTextColor(QColor('black'))
                                    ultima_riga_vuota=False

                                #QMessageBox.information(self,"Esecuzione Controlli","Test",QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)   

            data_fine=datetime.datetime.now()
            self.db_service.close_session(sess,data_fine)
            
            count_1 = invis_root.childCount()
            for i_1 in range(count_1):
                item_1 = invis_root.child(i_1)
                item_1.setBackgroundColor(0,col_sfondo)
            
                count_2 = item_1.childCount()
                for i_2 in range(count_2):
                    item_2 = item_1.child(i_2)
                    item_2.setBackgroundColor(0,col_sfondo)
                
                    count_3 = item_2.childCount()
                    for i_3 in range(count_3):
                        item_3 = item_2.child(i_3)
                        item_3.setBackgroundColor(0,col_sfondo)
                        
                        count_4=item_3.childCount()
                        for i_4 in range(count_4):
                            item_4 = item_3.child(i_4)
                            item_4.setBackgroundColor(0,col_sfondo)
                     
            #QMessageBox.information(self,"Esecuzione Controlli","Esecuzione completata",QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            self.out_message("Esecuzione controlli completata")
            
            self.pbExecuteControls.setEnabled(True)   

            self.load_dati_sess()
       
        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore nell'esecuzione dei controlli: {}".format(e.message), 
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            
    def build_sql_query(self, dict_controls):
        try:
            for ctrl in dict_controls.values():
                cmd_sql=ctrl['SQL_MOD'].strip()
                if cmd_sql[-1]==';':
                    cmd_sql=cmd_sql[:-1]
                if cmd_sql.lower().find('limit ')<0:
                    cmd_sql+='\n limit '
                    cmd_sql+=str(ctrl["MAX_ERR"])
                ctrl['SQL_MOD']=cmd_sql
                    
                if ctrl["LAYER"]!=None: 
                    if len(ctrl["LAYER"])>0 :
                        cmd_sql=self.subs_var_signs(ctrl,'SQL_MOD',"LAYER")
                        ctrl['SQL_MOD']=cmd_sql
                if ctrl["GEOM"]!=None: 
                    if len(ctrl["GEOM"])>0 :
                        cmd_sql=self.subs_var_signs(ctrl,'SQL_MOD',"GEOM")
                        ctrl['SQL_MOD']=cmd_sql
                if ctrl["ATTR"]!=None:
                    if len(ctrl["ATTR"])>0 :
                        cmd_sql=self.subs_var_signs(ctrl,'SQL_MOD',"ATTR")
                        ctrl['SQL_MOD']=cmd_sql
                if ctrl["VALORI"]!=None: 
                    if len(ctrl["VALORI"])>0 :
                        cmd_sql=self.subs_var_signs(ctrl,'SQL_MOD',"VALORI")
                        ctrl['SQL_MOD']=cmd_sql
#                 if ctrl["GEOMETRY"]==None: continue 
#                 if len(ctrl["GEOMETRY"])>0 :
#                     cmd_sql=self.subs_var_signs(ctrl,"GEOMETRY")
#                     ctrl['SQL_MOD']=cmd_sql

                # toppa per controlli su attributi di tabelle senza geom.
                if ctrl["GEOM"]==None:
                    cmd_sql=ctrl['SQL_MOD']
                    for i in range(1,10):
                        da_sost="lay" + str(i) +".$GEOM" + str(i) + "$"
                        cmd_sql=cmd_sql.replace(da_sost,'NULL')
                    ctrl['SQL_MOD']=cmd_sql

#                     layers=ctrl["LAYER"].split(";")
#                     i=0 
#                     for  layer in layers:
#                         i=i+1
#                         var="$LAYER" + str(i)
#                         cmd_sql=cmd_sql.replace(var, layer.strip())
                   
#                 if ctrl["TIPO_CTRL"]==1:
#                     ctrl["CMD_SQL"]=ctrl['CMD_SQL']
#                 elif ctrl["SQL_INS"]==2:
#                     cmd_sql=ctrl['CONDIZ'] 
#                     cmd_sql.replace("$LAYER", ctrl["LAYER"])
#                     cmd_sql.replace("$LAYER2", ctrl["LAYER_2"])
#                     cmd_sql.replace("$ATTR", ctrl["ATTR"])
#                     cmd_sql.replace("$ATTR2", ctrl["ATTR_2"])
#                     ctrl["CMD_SQL"]=cmd_sql
                  
#                 for key in ctrl:                     
#                     QMessageBox.Information(self,key,ctrl[key],QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)

#            self.txtbResults.append(cmd_sql)
#            self.txtbResults.append('')
        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore nella composizione del comando SQL: {}".format(e.message), QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton)
            
    def build_descr_mod(self, dict_controls):
        try:
            for ctrl in dict_controls.values():
                dsc_mod=ctrl['DESCR_MOD'] 
                if ctrl["LAYER"]!=None: 
                    if len(ctrl["LAYER"])>0 :
                        dsc_mod=self.subs_var_signs(ctrl,'DESCR_MOD',"LAYER")
                        ctrl['DESCR_MOD']=dsc_mod
                if ctrl["GEOM"]!=None: 
                    if len(ctrl["GEOM"])>0 :
                        dsc_mod=self.subs_var_signs(ctrl,'DESCR_MOD',"GEOM")
                        ctrl['DESCR_MOD']=dsc_mod
                if ctrl["ATTR"]!=None:
                    if len(ctrl["ATTR"])>0 :
                        dsc_mod=self.subs_var_signs(ctrl,'DESCR_MOD',"ATTR")
                        ctrl['DESCR_MOD']=dsc_mod
                if ctrl["VALORI"]!=None: 
                    if len(ctrl["VALORI"])>0 :
                        dsc_mod=self.subs_var_signs(ctrl,'DESCR_MOD',"VALORI")
                        ctrl['DESCR_MOD']=dsc_mod
        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore nella composizione della descriz. del modello: {}".format(e.message), QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton)
            
    def build_descr_ctrl(self, dict_controls):
        try:
            for ctrl in dict_controls.values():
                dsc_ctrl=ctrl['DESCR_CTRL'] 
                if ctrl["LAYER"]!=None: 
                    if len(ctrl["LAYER"])>0 :
                        dsc_ctrl=self.subs_var_signs(ctrl,'DESCR_CTRL',"LAYER")
                        ctrl['DESCR_CTRL']=dsc_ctrl
                if ctrl["GEOM"]!=None: 
                    if len(ctrl["GEOM"])>0 :
                        dsc_ctrl=self.subs_var_signs(ctrl,'DESCR_CTRL',"GEOM")
                        ctrl['DESCR_CTRL']=dsc_ctrl
                if ctrl["ATTR"]!=None:
                    if len(ctrl["ATTR"])>0 :
                        dsc_ctrl=self.subs_var_signs(ctrl,'DESCR_CTRL',"ATTR")
                        ctrl['DESCR_CTRL']=dsc_ctrl
                if ctrl["VALORI"]!=None: 
                    if len(ctrl["VALORI"])>0 :
                        dsc_ctrl=self.subs_var_signs(ctrl,'DESCR_CTRL',"VALORI")
                        ctrl['DESCR_CTRL']=dsc_ctrl
        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore nella composizione della descriz. del controllo: {}".format(e.message), QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton)
    
    def subs_var_signs(self, ctrl, campo_sost, var_sign):
        try:

            #cmd_sql=ctrl['SQL_MOD'] 
            str_modif=ctrl[campo_sost] 
            lst_params=ctrl[var_sign].split(";")
            i=0 
            for param in lst_params:
                i=i+1
                variab="$" + var_sign + str(i) + "$"
                str_modif=str_modif.replace(variab, param.strip())
            return str_modif
        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore nella sostituzione delle variabili {} nella stringa: {} ({})".format(var_sign, str_modif, e.message), QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton)
            
    def save_checks_ctrl(self):
        try:
            text, ok = QInputDialog.getText(self, 'Scelta controlli', 'Nome configurazione scelta controlli:')        
            if len(str(text))>0 and ok:
                sigla_sav=str(text)           
            else:
                return None
            cod_cts=str(self.cbContext.itemData(self.cbContext.currentIndex()).toString())
            invis_root = self.trwControls.invisibleRootItem()
            count_1 = invis_root.childCount()
            lchecked_ctrl=[]
            for i_1 in range(count_1):
                item_1 = invis_root.child(i_1)            
                count_2 = item_1.childCount()
                for i_2 in range(count_2):
                    item_2 = item_1.child(i_2)                
                    count_3 = item_2.childCount()
                    for i_3 in range(count_3):
                        item_3 = item_2.child(i_3)                        
                        count_4=item_3.childCount()
                        for i_4 in range(count_4):
                            item_4 = item_3.child(i_4)                                                                            
                            is_checked=item_4.checkState(0)
                            if (is_checked):
                                lchecked_ctrl.append(str(item_4.text(0)))
            self.db_service.insert_lst_chk(sigla_sav, cod_cts, lchecked_ctrl)                   
        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore in salvataggio scelta controlli: {}".format(e.message), 
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            
    def load_checks_ctrl(self):
        try:
            cod_cts=str(self.cbContext.itemData(self.cbContext.currentIndex()).toString())
            lst_sigla_chk=self.db_service.get_lst_sigla_chk(cod_cts)
            sigla, ok = QInputDialog.getItem(self, "Scelta controlli", "Lista scelte salvate", lst_sigla_chk, 0, False)
            if ok and sigla:
                ssigla=str(sigla)
            else:
                return None                     

            lst_chk_ctrl = self.db_service.get_lst_chk_ctrl(cod_cts, ssigla)
            
            invis_root = self.trwControls.invisibleRootItem()
            count_1 = invis_root.childCount()
            for i_1 in range(count_1):
                item_1 = invis_root.child(i_1)            
                count_2 = item_1.childCount()
                for i_2 in range(count_2):
                    item_2 = item_1.child(i_2)                
                    count_3 = item_2.childCount()
                    for i_3 in range(count_3):
                        item_3 = item_2.child(i_3)                        
                        count_4=item_3.childCount()
                        for i_4 in range(count_4):
                            item_4 = item_3.child(i_4)    
                            cod_ctrl=str(item_4.text(0))
                            if (cod_ctrl in lst_chk_ctrl):
                                item_4.setCheckState(0,Qt.Checked)
                            else:
                                item_4.setCheckState(0,Qt.Unchecked)
                                                                                                    

        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore in caricamento scelta controlli da eseguire: {}".format(e.message), 
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
    def load_dati_sess(self):
        try:
            #self.tbwSessions.clear()
            cod_cts=str(self.cbContext.itemData(self.cbContext.currentIndex()).toString())
            
            header_names=(QString("Sessione;Consegna;Inizio;Fine;Note;Tot;Eseg;Ok;Non ok;Num err").split(";"))

            self.tbwSessions.setHorizontalHeaderLabels(header_names)
            self.tbwSessions.setColumnCount(10)
            
            #larg_tot=0.0
            #for idx_col in range(0,8):
            #    larg_tot=larg_tot+self.tbwSessions.columnWidth(idx_col)
            
            larg_tot=self.tbwSessions.viewport().size().width()
            #for idx_col in range(0,8):
            #    self.tbwSessions.setColumnWidth(idx_col,int(larg_tot/10.0))
            self.tbwSessions.setColumnWidth(0,int(larg_tot*0.09))
            self.tbwSessions.setColumnWidth(1,int(larg_tot*0.14))
            self.tbwSessions.setColumnWidth(2,int(larg_tot*0.15))
            self.tbwSessions.setColumnWidth(3,int(larg_tot*0.15))
            self.tbwSessions.setColumnWidth(4,int(larg_tot*0.14))
            self.tbwSessions.setColumnWidth(5,int(larg_tot*0.06))
            self.tbwSessions.setColumnWidth(6,int(larg_tot*0.06))
            self.tbwSessions.setColumnWidth(7,int(larg_tot*0.06))
            self.tbwSessions.setColumnWidth(8,int(larg_tot*0.06))
            self.tbwSessions.setColumnWidth(9,int(larg_tot*0.07))
            
            self.lst_dati_sess=self.db_service.get_lst_dati_sess(cod_cts)
            if self.db_service.db_status!=0 :
                QMessageBox.critical(self, "Errore", "Errore in lettura riepilogo sessioni dal database: {}".format(self.db_service.err_msg), 
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
                return
            if len(self.lst_dati_sess)<1: return

            self.tbwSessions.setRowCount(len(self.lst_dati_sess))
            
            m=0
            for sess in self.lst_dati_sess:
                #newitem=QTableWidgetItem(sess['SID_SESSIONE'], sess['CONSEGNA'],sess['DATA_INIZIO'],sess['DATA_FINE'],sess['NOTE'])
                self.tbwSessions.setItem(m,0,QTableWidgetItem(sess['SID_SESSIONE']))
                self.tbwSessions.setItem(m,1,QTableWidgetItem(sess['CONSEGNA']))
                self.tbwSessions.setItem(m,2,QTableWidgetItem(sess['DATA_INIZIO']))
                self.tbwSessions.setItem(m,3,QTableWidgetItem(sess['DATA_FINE']))
                self.tbwSessions.setItem(m,4,QTableWidgetItem(sess['NOTE']))
                self.tbwSessions.setItem(m,5,QTableWidgetItem(str(sess['CTRL_TOT'])))
                self.tbwSessions.setItem(m,6,QTableWidgetItem(str(sess['CTRL_ESE'])))
                self.tbwSessions.setItem(m,7,QTableWidgetItem(str(sess['CTRL_OK'])))
                self.tbwSessions.setItem(m,8,QTableWidgetItem(str(sess['CTRL_KO'])))
                self.tbwSessions.setItem(m,9,QTableWidgetItem(str(sess['NUM_ERR'])))
                #self.tbwSessions.setRowHeight(m,20)
                m=m+1

            #header = self.tbwSessions.horizontalHeader()
            #header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
            
            self.tbwSessions.resizeRowsToContents()
            
            self.enable_session_buttons()
            
            #self.tbwSessions.update()
            #self.tbwSessions.repaint()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore nel caricamento del riepilogo sessioni: {}".format(e.message), QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
                                    
    def registry_to_names(self):
        try:
            reg_config_name=""
            reg_deliv_name=""
            reg_log_name=""
            parent_key=CreateKey(self.registry_root_key, self.registry_key_name)
            cfg_key=CreateKey(parent_key, "configName")
            dlv_key=CreateKey(parent_key, "deliveryName")
            log_key=CreateKey(parent_key, "logName")
            try:
                reg_config_name=EnumValue(cfg_key,0)[1]
            except Exception as e:
                self.err_msg=e.message
                reg_config_name=""
            try:
                reg_deliv_name=EnumValue(dlv_key,0)[1]
            except Exception as e:
                self.err_msg=e.message
                reg_deliv_name=""
            try:
                reg_log_name=EnumValue(log_key,0)[1]
            except Exception as e:
                self.err_msg=e.message
                reg_log_name=""
            CloseKey(cfg_key)
            CloseKey(dlv_key)
            CloseKey(log_key)
            CloseKey(parent_key)
            #verifica esistenza file
            if not isfile(reg_config_name): reg_config_name=""
            if not isfile(reg_deliv_name): reg_deliv_name=""
            if not isfile(reg_log_name): reg_log_name=""
            #restituzione lista nomi file
            return [reg_config_name,reg_deliv_name,reg_log_name]
        except Exception as e:
            self.err_msg=e.message
            return["","",""]

    def names_to_registry(self): #, db_config_name, db_deliv_name, db_log_name
        key=OpenKey(self.registry_root_key, self.registry_key_name)
        SetValue(key, "configName", REG_SZ, self.db_config_name)
        SetValue(key, "deliveryName", REG_SZ, self.db_deliv_name)
        SetValue(key, "logName", REG_SZ, self.db_log_name)
        CloseKey(key)

    def on_context_menu(self, click_point):
        # show context menu
        #self.popMenu.exec_(self.trwControls.mapToGlobal(click_point))        
        # show context menu (only on leaves)
        if (self.trwControls.itemAt(click_point).childCount()==0):
            self.cur_codctrl=self.trwControls.itemAt(click_point).text(0)
            self.popMenu.exec_(self.trwControls.mapToGlobal(click_point))     
        
    def create_out_err_tbls(self):
        self.txtbOutMsgs.append('----------')
#         prev_info=self.db_service.get_last_sess_info()
#         if len(prev_info)<1:
#             self.txtbOutMsgs.append('*** informazioni di sessione non trovate')
#             return
#         id_sess=prev_info['ID_SESS']

        indexes = self.tbwSessions.selectionModel().selectedRows()
#         for index in sorted(indexes):
#             print('Row %d is selected' % index.row())
            
        if not indexes:
            QtGui.QMessageBox.about(self, "Crea tabelle geometriche","Selezionare una sessione")
            return
        else:
            srow=indexes[0].row()
             
        id_sess=int(self.tbwSessions.item(srow,0).text())

        if id_sess<1:
            self.txtbOutMsgs.append('*** informazioni di sessione non trovate')
            return
        lst_tbls=self.db_service.get_lst_gtype_epsg_log(id_sess)
        if not lst_tbls:
            self.txtbOutMsgs.append('Errori non presenti, nessuna tabella creata')
            id_sess=0
            return
        for lst in lst_tbls:
            self.db_service.generate_log_table(self.db_log_name,id_sess,lst['GTYPE'],lst['EPSG'])
            out_msg='Generata tabella geom. errori: sessione='+str(id_sess)+', geom='+lst['GTYPE']+', epsg='+str(lst['EPSG'])
            self.txtbOutMsgs.append(out_msg)
        id_sess=0

    def report_sessione(self):  
        cod_cts=str(self.cbContext.itemData(self.cbContext.currentIndex()).toString())
        indexes = self.tbwSessions.selectionModel().selectedRows()
#         for index in sorted(indexes):
#             print('Row %d is selected' % index.row())
            
        if not indexes:
            QtGui.QMessageBox.about(self, "Crea report sessione","Selezionare una sessione")
            return
        else:
            srow=indexes[0].row()
             
        sid_sess=str(self.tbwSessions.item(srow,0).text()).strip()
        # *cerca negli headers l'indice della colonna inizio (data inizio)
        col_inizio = 0
        while col_inizio < self.tbwSessions.columnCount():
            if str(self.tbwSessions.horizontalHeaderItem(col_inizio).text()).lower() == 'inizio':
                inizio_sess=str(self.tbwSessions.item(srow,col_inizio).text())
                break
            col_inizio += 1
            
#         for sess in self.lst_dati_sess:
#             if str(sess['ID_SESSIONE']) == sid_sess:
#                 data_inizio = sess['DATA_INIZIO']
        if self.def_rpt_name: def_path=dirname(self.def_rpt_name)+'/'
        elif self.db_deliv_name: def_path=dirname(self.db_deliv_name)+'/'
        else: def_path=''
        self.def_rpt_name=def_path  + cod_cts + "_sess_" + sid_sess + "_" + inizio_sess[:10] + ".pdf"
        self.def_rpt_name=normpath(self.def_rpt_name) 
        rpt_name = QtGui.QFileDialog.getSaveFileName(self, "Crea report sessione",QString(self.def_rpt_name), "Report pdf (*.pdf);;All Files (*)")        
        if not rpt_name:
            return         
#         QtGui.QMessageBox.information(self, "Chiama stampa","Stampa su file \"%s\"" % rpt_name)
        self.def_rpt_name=str(rpt_name)
        self.crea_rep_sessione(int(sid_sess), str(rpt_name))
        
        self.txtbOutMsgs.append('----------')
        out_msg='Creato report: '+rpt_name
        self.txtbOutMsgs.append(out_msg)

    def enable_session_buttons(self):  
        indexes = self.tbwSessions.selectionModel().selectedRows()
            
        if indexes:
            num_err=0
            srow=indexes[0].row()
            col_numerr = 0
            while col_numerr < self.tbwSessions.columnCount():
                if str(self.tbwSessions.horizontalHeaderItem(col_numerr).text()).lower() == 'num err':
                    num_err=int(str(self.tbwSessions.item(srow,col_numerr).text()))
                    break
                col_numerr += 1
            self.pbOutTables.setEnabled(num_err>0)
            self.pbReportSessione.setEnabled(True)
            self.cbOkResultsOut.setEnabled(True)
            self.cbDescrizOut.setEnabled(True)
        else:
            self.pbOutTables.setEnabled(False)
            self.pbReportSessione.setEnabled(False)
            self.cbOkResultsOut.setEnabled(False)
            self.cbDescrizOut.setEnabled(False)
                  
    def closeEvent(self,close_event):    
#         result = QtGui.QMessageBox.question(self,
#                    "Uscita...",
#                    "Sicuro di voler uscire ?",
#                    QtGui.QMessageBox.Yes| QtGui.QMessageBox.No)
#     
#         if result == QtGui.QMessageBox.Yes:
#             #self.names_to_registry(str(self.leDbConfig.text()),str(self.leDbDelivery.text()),str(self.leDbLog.text()) )
#             self.names_to_registry()
#             self.db_service.db_close()
#             close_event.accept()
#         else:
#             close_event.ignore()
             
        self.names_to_registry()
        self.db_service.db_close()
        close_event.accept()

    def copy_sql_cmd(self):
        #QtGui.QMessageBox.question(self,"Test", "You clicked on copy SQL",QtGui.QMessageBox.Yes)
        #QtGui.QMessageBox.question(self,"Test",self.cur_codctrl,QtGui.QMessageBox.Yes)
        the_tk=Tk()
        the_tk.withdraw()
        the_tk.clipboard_clear()
        #the_tk.clipboard_append('You clicked on copy SQL')
        #the_tk.clipboard_append(self.cur_codctrl)
        the_tk.clipboard_append(self.dict_controls[str(self.cur_codctrl)]['SQL_MOD'])
                        
        the_tk.update()
        the_tk.destroy()
        
        set_tblndx=set([])
        sql_query=self.dict_controls[str(self.cur_codctrl)]['SQL_MOD']
        set_tblndx=self.get_set_tblndx(sql_query) 
                       
    def get_set_tblndx(self,sql_query):
        import re
        set_tblndx = set([])
        sqlf1=sql_query.lower()
        sqlf1=re.sub(r"[\n\t\s]*","",sqlf1)
        sqlf2="select rowid from SpatialIndex where f_table_name = '".lower()
        sqlf2=re.sub(r"[\n\t\s]*","",sqlf2)
#         print [(sqlf1[a.end():a.end()+sqlf1[a.end():].find("'")]) for a in list(re.finditer(sqlf2, sqlf1))]
        [set_tblndx.add(sqlf1[a.end():a.end()+sqlf1[a.end():].find("'")]) for a in list(re.finditer(sqlf2, sqlf1))]
        return set_tblndx 
        
    def copy_doc_cmd(self):
        #QtGui.QMessageBox.question(self,"Test", "You clicked on copy SQL",QtGui.QMessageBox.Yes)
        #QtGui.QMessageBox.question(self,"Test",self.cur_codctrl,QtGui.QMessageBox.Yes)
        the_tk=Tk()
        the_tk.withdraw()
        the_tk.clipboard_clear()
        #the_tk.clipboard_append('You clicked on copy SQL')
        #the_tk.clipboard_append(self.cur_codctrl)
        the_tk.clipboard_append(self.dict_controls[str(self.cur_codctrl)]['DESCR_MOD'])
        the_tk.update()
        the_tk.destroy()

    def apri_info_ctrl(self):
        testo_descriz=str(self.dict_controls[str(self.cur_codctrl)]['DESCR_MOD'])
        testo_query=str(self.dict_controls[str(self.cur_codctrl)]['SQL_MOD'])
        dlgDescrCtrl=ClsDlgDescrCtrl(testo_descriz,testo_query)
        dlgDescrCtrl.exec_()
                
    def empty_log_out_box(self):        
        self.txtbResults.clear()
        
    def out_message(self,out_msg):
        self.txtbOutMsgs.append('----------')
        self.txtbOutMsgs.append(out_msg)
        #self.txtbOutMsgs.append('')
        
    def create_empty_db_log(self):        
        dflt_name=""
        if (self.leDbLog.text()!="") : dflt_name=dirname(abspath(self.leDbLog.text()))+'/'
        dflt_name=dflt_name+'db_diagn_vuoto.sqlite'
        file_name=str(QFileDialog.getSaveFileName(self, "Db di diagnostica da creare",dflt_name, "Sqlite db (*.sqlite);;All Files (*)"))
        if not file_name or file_name == "": return
        msg_out=self.db_service.crea_db_diagn_vuoto(file_name)
        if msg_out!='ok':
            QtGui.QMessageBox.warning(self, "Crea DB diagnostica",msg_out)
        else:
            msg_out='Creato il file: \n'
            msg_out+=file_name
            QtGui.QMessageBox.information(self, "Crea DB diagnostica",msg_out)
        
    def create_model_docum(self):
        try:
            lst_doc_mod=self.db_service.create_doc_mod_list()
            if self.db_service.db_status!=0:
                QMessageBox.critical(self, "Errore", "Errore in caricamento docum. modelli: {}".format(self.db_service.err_msg), QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
                return

            if self.def_docmod_name: def_path=dirname(self.def_docmod_name)+'/'
            elif self.db_config_name: def_path=dirname(self.db_config_name)+'/'
            else: def_path=''
            self.def_docmod_name=def_path  + "Documentazione_modelli_GcRT.pdf"
            self.def_docmod_name=normpath(self.def_docmod_name) 
            docmod_name = QtGui.QFileDialog.getSaveFileName(self, "Crea decum. modelli",QString(self.def_docmod_name), "Docum. modelli pdf (*.pdf);;All Files (*)")        
            if not docmod_name:
                return         
#             QtGui.QMessageBox.information(self, "Chiama stampa","Stampa su file \"%s\"" % rpt_name)
            self.def_docmod_name=str(docmod_name)
            
            lst_intest=[]
            lst_intest.append({'TESTO' : 'GeoControlli_RT' , 'STILE' : 'Title', 'INDENT_MM' : 0, 'BELOW_MM' : 10})
            lst_intest.append({'TESTO' : 'DOCUMENTAZIONE DEI MODELLI' , 'STILE' : 'Title', 'INDENT_MM' : 0, 'BELOW_MM' : 10})
            lst_intest.append({'TESTO' : 'Descrizione dei modelli contenuti nel db di congurazione:' , 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 1})
            lst_intest.append({'TESTO' : self.db_config_name , 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 6})
            lst_intest.append({'TESTO' : 'Data: ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M'), 'STILE' : 'Heading4', 'INDENT_MM' : 0, 'BELOW_MM' : 0}) #str(datetime.datetime.now())
            
            doc = ClsModDocToPdf(lst_intest, lst_doc_mod)
            doc.export(str(docmod_name))    
       
            self.txtbOutMsgs.append('----------')
            out_msg='Creato file docum. modelli: '+docmod_name
            self.txtbOutMsgs.append(out_msg)

        except Exception as e:
            QMessageBox.critical(self, "Errore", "Errore in creazione docum. modelli: {}".format(e.message), QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
        
    #def exit_from_program(self):
    #    sys.exit()
    
    def info_dialog_show(self):
        self.infoDlg.exec_()
        #str_out=self.db_service.test_db_query()  
        #QMessageBox.information(self, "Testo", str_out, QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)

    def info_dialog_exit(self):
        self.infoDlg.close()
        
    def info_dialog_open_manual(self):
        self.infoDlg.close()

        if self.db_config_name: manual_path=dirname(self.db_config_name)+'/'
        else:
            manual_path=''
            QMessageBox.critical(self, "Percorso non trovato", "Occorre la connessione al DB di configurazione ", QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            return;
        manual_file=manual_path  + "GeoControlli_RT_GuidaUtente.pdf"
        manual_file=str(normpath(manual_file))
        
        if not isfile(manual_file):
            QMessageBox.critical(self, "File non trovato", "Non trovato file di descrizione:  \n"+manual_file, QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            return;
        
        #subprocess.Popen(manual_file, shell=True)
        startfile(manual_file)
        
        
if __name__ == '__main__':
    import sys
 
    app = QtGui.QApplication(sys.argv)
    window = GeoControlli_RT()
    window.show()

    sys.exit(app.exec_())
