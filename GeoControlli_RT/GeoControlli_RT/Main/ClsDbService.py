'''
Created on 15/gen/2017

@author: Virgilio Cima
'''
#from pyspatialite import dbapi2 as sldb
import sqlite3
import itertools
from ClsSessione import  ClsSessione
#import datetime

#from collections import OrderedDict

class ClsDbService(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.db_status=0 
        self.err_msg=""
        self.is_connected=False
        #self.cnnConfig=None
        #self.cnnDelivery=None
        self.db_conn=None
        
    def db_connect(self, db_config_name, db_deliv_name, db_log_name):
        try:
            self.db_status=0
            self.err_msg=""
            #butta_via='<A> '
            # self.cnnConfig=sldb.Connection(db_config_name)
            # self.cnnConfig.enable_load_extension(True)
            self.db_conn = sqlite3.connect(db_deliv_name)
            #butta_via='<B> '
            
            if not self.test_r_tree():
                self.db_status=1
                self.err_msg='Manca il supporto R*Tree nella libreria sqlite3.dll'
                return
           
            sql_test='drop table if exists test_poi_butta_via'
            self.db_conn.execute(sql_test)
            
            if (db_deliv_name.upper()!=db_config_name.upper()):
                self.db_conn.execute("ATTACH DATABASE '" + db_config_name + "' AS r")
            #butta_via='<C> '
            if (db_log_name.upper()!=db_config_name.upper() and db_log_name.upper()!=db_deliv_name.upper()):
                self.db_conn.execute("ATTACH DATABASE '" + db_log_name + "' AS l")
            
            #butta_via='<D> '
            self.db_conn.enable_load_extension(True)
            # db_conn.execute("SELECT load_extension('C:\Spatialite_4_3a\ctestlib2')")
#             db_cursor = self.db_conn.cursor()
#             result_set=db_cursor.execute("select sqlite_version()")
#             for row in result_set:
#                 pippo=row[0]
                
            #self.db_conn.execute("SELECT load_extension('C:/Spatialite/ctestlib2')")
            #self.db_conn.execute("SELECT load_extension('C:/Spatialite/mod_spatialite')")
            #self.db_conn.execute("SELECT load_extension('C:/Spatialite_4_3/all_extensions/mod_geocontrolli_rt')")
            #butta_via='<E> '
            self.db_conn.execute("SELECT load_extension('mod_spatialite')")
            #butta_via='<F> '
            self.db_conn.execute("SELECT load_extension('mod_geocontrolli_rt')")
            #butta_via='<G> '
            self.is_connected=True
            
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message #butta_via+
        finally:  
            return self.db_status
        
    def fill_dict_controls(self,cod_cts,dict_controls):
        try:
            #dict_controls=OrderedDict() # = {}  
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            result_set=db_cursor.execute('SELECT A.COD_CTS, T.DESCR_CTS, K.COD_CAT, K.DESCR_CAT, A.COD_GRP, G.DESCR_GRP, C.COD_CTRL, C.DESCR_CTRL, C.COD_MOD, M.SQL_MOD, M.RISULT_ALFA, M.RISULT_GEOM, ' + 
                                         'C.V_LAYER, C.V_GEOM, C.V_FILTRI, C.V_ATTR, C.V_VALORI, C.MAX_ERR, M.DESCR_MOD ' + 
                                         'FROM r.CONTROLLI C, r.MODELLI M, r.ALBERO_CTRL A, r.GRUPPI G, r.CONTESTI T, CATEG K WHERE A.COD_CTS=? AND ' +
                                         'C.COD_MOD=M.COD_MOD AND C.COD_CTRL=A.COD_CTRL AND A.COD_GRP=G.COD_GRP AND A.COD_CTS=T.COD_CTS  AND K.COD_CAT=G.COD_CAT ' + 
                                         'ORDER BY T.ORD_CTS, K.ORD_CAT, G.ORD_GRP, C.ORD_CTRL',[cod_cts])
            for row in result_set:
                dict_controls[row[6]]={'COD_CTS':row[0], 'DESCR_CTS':row[1], 'COD_CAT':row[2], 'DESCR_CAT':row[3],'COD_GRP':row[4],'DESCR_GRP':row[5], 'COD_CTRL':row[6], 'DESCR_CTRL':row[7], 
                                       'COD_MOD':row[8],'SQL_MOD':row[9],'RISULT_ALFA':row[10], 'RISULT_GEOM':row[11], 'LAYER':row[12], 'GEOM':row[13],
                                       'FILTER':row[14], 'ATTR':row[15], 'VALORI':row[16], 'MAX_ERR':row[17], 'DESCR_MOD':row[18]}
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            #dict_controls = {}
        finally:  
            return # dict_controls
        
    def open_session(self, sess):
        try:
            self.db_status=0            
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            db_cursor.execute("SELECT COALESCE(MAX(ID_SESSIONE),0) ID_SESSIONE FROM SESSIONI")
            sess.id_sessione=db_cursor.fetchone()[0]+1
            
            sql_insert="INSERT INTO SESSIONI (ID_SESSIONE, COD_CTS, CONSEGNA, DATA_INIZIO, PATH_DAT, PATH_CFG, PATH_LOG, OPERATORE, NOTE) "
            sql_insert += " VALUES(?,?,?,?,?,?,?,?,?)"
            self.db_conn.execute(sql_insert,[sess.id_sessione, sess.cod_cts, sess.consegna, sess.data_inizio, sess.path_dat, sess.path_cfg, sess.path_log, sess.operatore, sess.note])
            self.db_conn.commit()
#             db_cursor = self.db_conn.cursor()
#             db_cursor.execute("select seq from sqlite_sequence where name='SESSIONI'")
#             sess.id_sessione=db_cursor.fetchone()[0]
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            sess.id_sessione=0
        finally:  
            return sess.id_sessione
        
    def exec_ctrl(self, sess, id_esecuz, ctrl):
        try:
            self.db_status=0
            self.err_msg=""
            num_err=0            
            # preparo esecuzione con inserimento in ERR_LOG
            if  (str(ctrl["RISULT_GEOM"] or '').strip() and ctrl["RISULT_GEOM"]) :
                sql_insert="INSERT INTO ERR_LOG (ID_ESECUZ, ALFA_ERR, GEOM_ERR) "
                sql_insert +="SELECT ?," + ctrl["RISULT_ALFA"] + "," + ctrl["RISULT_GEOM"] + " FROM ("
            else:
                sql_insert="INSERT INTO ERR_LOG (ID_ESECUZ, ALFA_ERR) "
                sql_insert +="SELECT ?," + ctrl["RISULT_ALFA"]  + " FROM ("
            sql_insert += ctrl["SQL_MOD"].replace(";","") + ")"
            curs=self.db_conn.execute(sql_insert,[id_esecuz])
            num_err=0
            if curs!=None:
                num_err=curs.rowcount
            self.db_conn.commit() 
            
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
        finally:    
            return num_err  
         
    def open_exec(self, sess, ctrl, data_inizio):
        try:
            self.db_status=0
            self.err_msg=""
            id_esecuz=0
            db_cursor = self.db_conn.cursor()
            db_cursor.execute("SELECT COALESCE(MAX(ID_ESECUZ),0) ID_ESECUZ FROM ESECUZ")
            id_esecuz=db_cursor.fetchone()[0]+1
            stato=-1
            sql_insert="INSERT INTO ESECUZ (ID_ESECUZ, COD_CTRL, DESCR_CTRL,DATA_INIZIO,  ID_SESSIONE, QUERY_SQL, STATO) VALUES( ?,?,?,?,?,?,?)"
            self.db_conn.execute(sql_insert,[id_esecuz,ctrl['COD_CTRL'] ,ctrl['DESCR_CTRL'], data_inizio, sess.id_sessione, ctrl['SQL_MOD'], stato])
            
            self.db_conn.commit()
            
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
        finally:    
            return id_esecuz

    def close_exec(self, id_esecuz, data_fine, num_err, stato, err_msg):
        try:
            self.db_status=0
            self.err_msg=""
            sql_update="UPDATE ESECUZ SET  DATA_FINE=?, NUM_ERR=?, STATO=?, MSG_ERR=? WHERE ID_ESECUZ=?"
            self.db_conn.execute(sql_update,[data_fine, num_err, stato, err_msg, id_esecuz])
            
            self.db_conn.commit()
            
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
        finally:    
            return         

    def close_session(self, sess, data_fine):
        try:
            self.db_status=0
            self.err_msg=""
            sql_update="UPDATE SESSIONI SET  DATA_FINE=?  WHERE ID_SESSIONE=?"
            self.db_conn.execute(sql_update,[data_fine, sess.id_sessione])
            
            self.db_conn.commit()
            
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
        finally:    
            return         
 
    def get_last_sess_info(self):
        try:
            prev_info = {}  
            self.db_status=0
            self.err_msg=""
            id_sess=0
            db_cursor = self.db_conn.cursor()
            db_cursor.execute("SELECT COALESCE(MAX(ID_SESSIONE),0) ID_SESSIONE FROM SESSIONI")
            id_sess=db_cursor.fetchone()[0] # attenzione! fetchone si svuota appena usato: non mettere in watch!
            if id_sess<1: return prev_info
            db_cursor.execute("SELECT COD_CTS, CONSEGNA, OPERATORE, NOTE FROM SESSIONI WHERE ID_SESSIONE=?",[id_sess])
            temp_tuple=db_cursor.fetchone()
            prev_info['ID_SESS']=id_sess 
            prev_info['COD_CTS']=temp_tuple[0] 
            prev_info['CONSEGNA']=temp_tuple[1] 
            prev_info['OPERATORE']=temp_tuple[2] 
            prev_info['NOTE']=temp_tuple[3] 
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            prev_info = []
        finally:  
            return prev_info

    def get_lst_contexts(self):
        try:
            lst_contexts = []  
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            result_set=db_cursor.execute(
                'SELECT COD_CTS, DESCR_CTS from CONTESTI order by ORD_CTS')
            for row in result_set:
                lst_contexts.append([row[0],row[1]])
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            lst_contexts = []
        finally:  
            return lst_contexts
        
    def get_lst_dati_sess(self,cod_cts):
        try:
            lst_dati_sess = []  
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            #sqlcmd="select substr('          '||cast(B.ID_SESSIONE as text),-10,10) SID_SESSIONE, IFNULL(B.CONSEGNA,'--') CONSEGNA, "
            #sqlcmd+="IFNULL(strftime('%Y-%m-%d %H:%M:%S',B.DATA_INIZIO),'00-00-00') DATA_INIZIO, IFNULL(strftime('%Y-%m-%d %H:%M:%S',B.DATA_FINE),'00-00-00')  DATA_FINE, IFNULL(B.NOTE,'--'), "
            #sqlcmd+= "COUNT(COD_CTRL) CTRL_TOT, SUM(CASE WHEN NUM_ERR=0 THEN 1 ELSE 0 END) AS CTRL_OK, "
            #sqlcmd+="SUM(CASE WHEN NUM_ERR=0 THEN 0 ELSE 1 END) AS CTRL_KO, SUM(NUM_ERR) AS NUM_ERR FROM " 
            #sqlcmd+="(select S.ID_SESSIONE, E.COD_CTRL, SUM(CASE  WHEN ALFA_ERR IS NULL THEN 0 ELSE 1 END) NUM_ERR " 
            #sqlcmd+="from SESSIONI S INNER JOIN ESECUZ E ON E.ID_SESSIONE=S.ID_SESSIONE "
            #sqlcmd+= "LEFT OUTER JOIN ERR_LOG L ON  E.ID_ESECUZ=L.ID_ESECUZ GROUP BY S.ID_SESSIONE, E.COD_CTRL "
            #sqlcmd+=") A, SESSIONI B WHERE A.ID_SESSIONE=B.ID_SESSIONE AND COD_CTS=? " 
            #sqlcmd+="GROUP BY SID_SESSIONE, B.CONSEGNA, B.DATA_INIZIO, B.DATA_FINE, NOTE ORDER BY B.ID_SESSIONE DESC" 
            sqlcmd="select substr('          '||cast(B.ID_SESSIONE as text),-10,10) SID_SESSIONE, IFNULL(B.CONSEGNA,'--') CONSEGNA, "
            sqlcmd+="IFNULL(strftime('%Y-%m-%d %H:%M:%S',B.DATA_INIZIO),'00-00-00') DATA_INIZIO, IFNULL(strftime('%Y-%m-%d %H:%M:%S',B.DATA_FINE),'00-00-00')  DATA_FINE, IFNULL(B.NOTE,'--'), "
            sqlcmd+="COUNT(COD_CTRL) CTRL_TOT, SUM(CASE WHEN STATO_ES=0 THEN 1 ELSE 0 END) AS CTRL_ESE, SUM(CASE WHEN (NUM_ERR=0 AND STATO_ES=0) THEN 1 ELSE 0 END) AS CTRL_OK, "
            sqlcmd+="SUM(CASE WHEN (NUM_ERR<>0 AND STATO_ES=0) THEN 1 ELSE 0 END) AS CTRL_KO, SUM(NUM_ERR) AS NUM_ERR FROM " 
            sqlcmd+="(select S.ID_SESSIONE, E.COD_CTRL, SUM(CASE  WHEN ALFA_ERR IS NULL THEN 0 ELSE 1 END) NUM_ERR, E.STATO STATO_ES " 
            sqlcmd+="from SESSIONI S INNER JOIN ESECUZ E ON E.ID_SESSIONE=S.ID_SESSIONE "
            sqlcmd+= "LEFT OUTER JOIN ERR_LOG L ON  E.ID_ESECUZ=L.ID_ESECUZ GROUP BY S.ID_SESSIONE, E.COD_CTRL "
            sqlcmd+=") A, SESSIONI B WHERE A.ID_SESSIONE=B.ID_SESSIONE AND COD_CTS=? " 
            sqlcmd+="GROUP BY SID_SESSIONE, B.CONSEGNA, B.DATA_INIZIO, B.DATA_FINE, NOTE ORDER BY B.ID_SESSIONE DESC" 
            result_set=db_cursor.execute(sqlcmd,[cod_cts])
            for row in result_set:
                lst_dati_sess.append({'SID_SESSIONE':row[0], 'CONSEGNA':row[1], 'DATA_INIZIO':row[2], 'DATA_FINE':row[3] , 'NOTE':row[4],
                'CTRL_TOT':row[5], 'CTRL_ESE':row[6], 'CTRL_OK':row[7], 'CTRL_KO':row[8], 'NUM_ERR':row[9]})
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            lst_dati_sess = []
        finally:  
            return lst_dati_sess
        
#     def get_lst_gtype_log(self,id_sessione):
# #         1 = POINT
# #         2 = LINESTRING
# #         3 = POLYGON
# #         4 = MULTIPOINT
# #         5 = MULTILINESTRING
# #         6 = MULTIPOLYGON
# #         7 = GEOMETRYCOLLECTION
# #         1001 = POINT Z
# #         1002 = LINESTRING Z
# #         1003 = POLYGON Z
# #         1004 = MULTIPOINT Z
# #         1005 = MULTILINESTRING Z
# #         1006 = MULTIPOLYGON Z
# #         1007 = GEOMETRYCOLLECTION Z
#         try:
#             lst_gtype_log = []  
#             self.db_status=0
#             self.err_msg=""
#             db_cursor = self.db_conn.cursor()
#             result_set=db_cursor.execute(
#                 'SELECT st_geometrytype(geom_err) gtype from err_log WHERE id_sessione=? and GEOM_ERR is not null group by gtype',[id_sessione])
#             for row in result_set:
#                 lst_gtype_log.append(row[0])
#         except Exception as e:
#             self.db_status=1
#             self.err_msg=e.message
#             lst_gtype_log = []
#         finally:  
#             return lst_gtype_log
# 
#     def get_lst_epsg_log(self,id_sessione):
#         try:
#             lst_epsg_log = []  
#             self.db_status=0
#             self.err_msg=""
#             db_cursor = self.db_conn.cursor()
#             result_set=db_cursor.execute(
#                 'SELECT st_srid(geom_err) epsg from err_log WHERE id_sessione=? and GEOM_ERR is not null group by epsg',[id_sessione])
#             for row in result_set:
#                 lst_epsg_log.append(row[0])
#         except Exception as e:
#             self.db_status=1
#             self.err_msg=e.message
#             lst_epsg_log = []
#         finally:  
#             return lst_epsg_log

    def get_lst_gtype_epsg_log(self,id_sessione):
#         1 = POINT
#         2 = LINESTRING
#         3 = POLYGON
#         4 = MULTIPOINT
#         5 = MULTILINESTRING
#         6 = MULTIPOLYGON
#         7 = GEOMETRYCOLLECTION
#         1001 = POINT Z
#         1002 = LINESTRING Z
#         1003 = POLYGON Z
#         1004 = MULTIPOINT Z
#         1005 = MULTILINESTRING Z
#         1006 = MULTIPOLYGON Z
#         1007 = GEOMETRYCOLLECTION Z
        try:
            lst_gtype_epsg_log = []  
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            result_set=db_cursor.execute(
                'SELECT upper(st_geometrytype(GEOM_ERR)) GTYPE, st_srid(GEOM_ERR) EPSG from err_log er JOIN esecuz es ON er.id_esecuz=es.id_esecuz WHERE es.id_sessione=? and GEOM_ERR is not null group by GTYPE, EPSG order by GTYPE, EPSG',
                [id_sessione])
            for row in result_set:
                lst_gtype_epsg_log.append({'GTYPE':row[0], 'EPSG':row[1]})
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            lst_gtype_epsg_log = []
        finally:  
            return lst_gtype_epsg_log
        
    def generate_log_table(self, db_log_name, id_sessione, gtype, epsg):
        try:
            self.db_status=0
            self.err_msg=""
            
            self.db_conn.execute("DETACH DATABASE l")
            
            log_conn = sqlite3.connect(db_log_name)
            log_conn.enable_load_extension(True)
            #log_conn.execute("SELECT load_extension('C:/Spatialite/mod_spatialite')")
            log_conn.execute("SELECT load_extension('mod_spatialite')")
            
            # un po' rozzo ... da discutere
            if gtype.find(" Z")>=0:
                geo_type=gtype[0:gtype.find(" Z")]
                geo_dim='XYZ'
            elif gtype.find(" M")>=0:
                geo_type=gtype[0:gtype.find(" M")]
                geo_dim='XYM'
            else:
                geo_type=gtype
                geo_dim='XY'
            # anche nel nome della tabella si possono adottare convenzioni per semplificare   
            tname="ERR_SESS_" + str(id_sessione) + "_" + geo_type + "_" + str(epsg) + "_" + geo_dim
            tname=tname.replace(' ','_')

            sql_delete="SELECT DropGeoTable('" + tname + "')"
            #sql_delete="DROP TABLE IF EXISTS ERR_LOG " + tname
            log_conn.execute(sql_delete)

            sql_create="CREATE TABLE " + tname + "("
            sql_create+="ID_ERR INTEGER PRIMARY KEY, "
            sql_create+="ID_ESECUZ INTEGER, "
            sql_create+="COD_CTRL TEXT, "
            sql_create+="DESCR_CTRL TEXT, "
            sql_create+="ALFA_ERR TEXT, "
            sql_create+="GEOM_ERR GEOMETRY) "
            log_conn.execute(sql_create)
            
            sql_register="SELECT RecoverGeometryColumn('" + tname + "', 'GEOM_ERR'," + str(epsg) + ",'" + geo_type +"', '" + geo_dim + "')"
            log_conn.execute(sql_register)
            
#             sql_insert="INSERT INTO " + tname + " (ID_ERR, ID_ESECUZ, ALFA_ERR, GEOM_ERR)"
#             sql_insert += " SELECT er.ID_ERR, er.ID_ESECUZ, er.ALFA_ERR, er.GEOM_ERR FROM ERR_LOG er" 
#             sql_insert += " INNER JOIN esecuz es ON er.id_esecuz=es.id_esecuz"
#             sql_insert += " WHERE es.id_sessione=? and st_geometrytype(er.GEOM_ERR)=? and st_srid(er.GEOM_ERR)=?"
#             log_conn.execute(sql_insert,[id_sessione,gtype,epsg])
            
            sql_insert="INSERT INTO " + tname + " (ID_ERR, ID_ESECUZ, COD_CTRL, DESCR_CTRL, ALFA_ERR, GEOM_ERR)"
            sql_insert += " SELECT er.ID_ERR, er.ID_ESECUZ, es.COD_CTRL, es.DESCR_CTRL, er.ALFA_ERR, er.GEOM_ERR FROM ERR_LOG er" 
            sql_insert += " INNER JOIN esecuz es ON er.id_esecuz=es.id_esecuz"
            sql_insert += " WHERE es.id_sessione=? and st_geometrytype(er.GEOM_ERR)=? and st_srid(er.GEOM_ERR)=?"
            log_conn.execute(sql_insert,[id_sessione,gtype,epsg])
            
            #sql_index="SELECT createspatialindex('" + tname + "', 'GEOM_ERR')"
            #log_conn.execute(sql_index)
            
            log_conn.commit()

        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
        finally:
            log_conn.close()
            self.db_conn.execute("ATTACH DATABASE '" + db_log_name + "' AS l")
            return 
        
    def test_spatial_fun(self):
        try:
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            # result_set=db_cursor.execute('select MAX(ST_AREA(geometry)) from referenceparcel')
            # result_set=db_cursor.execute('select length(mygeomtotvtx(geometry, length(geometry))) from landscapefeature')
            result_set=db_cursor.execute('select RT_ID, GEOMETRY FROM RT_0101_A LIMIT 10')
            sql_insert="INSERT INTO ERR_LOG (ID_ESECUZ, ALFA_ERR, GEOM_ERR) VALUES(?, ?, ?)"
            for row in result_set:
                rpid=row[0]
                geom=row[1]
                self.db_conn.execute(sql_insert,[1, rpid, sqlite3.Binary(geom)])
            self.db_conn.commit()
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            area=0
        finally:  
            return area

    def insert_lst_chk(self, sigla, cod_cts, lchecked_ctrl):
        try:
            self.db_status=0            
            self.err_msg=""
            sql_delete="DELETE FROM SCELTA_CTRL WHERE SIGLA_SCELTA=? AND COD_CTS=?"
            self.db_conn.execute(sql_delete,[sigla, cod_cts])
            
            sql_insert="INSERT INTO SCELTA_CTRL(SIGLA_SCELTA,COD_CTS,COD_CTRL) VALUES (?,?,?)"
            for cod_ctrl in lchecked_ctrl:
                self.db_conn.execute(sql_insert,[sigla, cod_cts, cod_ctrl])
            self.db_conn.commit()
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
        finally:  
            return   
        
    def get_lst_sigla_chk(self,cod_cts):
        try:
            lst_sigla_chk = []  
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            sqlcmd="SELECT SIGLA_SCELTA FROM SCELTA_CTRL WHERE COD_CTS=? GROUP BY SIGLA_SCELTA ORDER BY SIGLA_SCELTA;" 
            result_set=db_cursor.execute(sqlcmd,[cod_cts])
            for row in result_set:
                lst_sigla_chk.append(row[0])
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            lst_sigla_chk = []
        finally:  
            return lst_sigla_chk 

    def get_lst_chk_ctrl(self,cod_cts, sigla_scelta):
        try:
            lst_chk_ctrl = []  
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            sqlcmd="SELECT COD_CTRL  FROM SCELTA_CTRL WHERE COD_CTS=? AND SIGLA_SCELTA=?" 
            result_set=db_cursor.execute(sqlcmd,[cod_cts, sigla_scelta])
            for row in result_set:
                lst_chk_ctrl.append(row[0])
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            lst_chk_ctrl  = []
        finally:  
            return lst_chk_ctrl 
        
    def exec_sql_to_list(self,sql_cmd):
        try:
            lst_dict_sql= []  
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            db_cursor.execute(sql_cmd)
            desc = db_cursor.description
            column_names = [col[0] for col in desc]
            lst_dict_sql = [dict(itertools.izip(column_names, row))  for row in db_cursor.fetchall()]
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            lst_dict_sql= []
        finally:
            return lst_dict_sql

    def create_report_list(self,id_sessione):
        try:
            sql_cmd="SELECT ca.DESCR_CAT DES_CAT, gr.DESCR_GRP DES_GRP, co.COD_CTRL COD_CTRL, es.DESCR_CTRL DES_CTRL, mo.DESCR_MOD DES_MOD, "
            sql_cmd+="CASE WHEN er.ALFA_ERR IS NULL THEN 'ok' ELSE er.ALFA_ERR END ESITO_CTRL, "
            sql_cmd+="es.STATO DB_STATO, es.MSG_ERR DB_MSG_ERR, co.COD_MOD COD_MOD, es.NUM_ERR, co.MAX_ERR MAX_ERR "
            sql_cmd+="FROM ESECUZ es "
            sql_cmd+="LEFT OUTER JOIN ERR_LOG er ON es.ID_ESECUZ=er.ID_ESECUZ "
            sql_cmd+="INNER JOIN ALBERO_CTRL al ON es.COD_CTRL=al.COD_CTRL "
            sql_cmd+="INNER JOIN CONTROLLI co ON co.COD_CTRL=es.COD_CTRL "
            sql_cmd+="INNER JOIN GRUPPI gr ON gr.COD_GRP=al.COD_GRP "
            sql_cmd+="INNER JOIN CATEG ca ON gr.COD_CAT=ca.COD_CAT "
            sql_cmd+="INNER JOIN MODELLI mo ON mo.COD_MOD=co.COD_MOD "
            sql_cmd+="WHERE es.ID_SESSIONE=? "
            sql_cmd+="ORDER BY ca.ORD_CAT, gr.ORD_GRP, co.ORD_CTRL"
            lst_dict_sql= []  
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            db_cursor.execute(sql_cmd, [id_sessione])
            desc = db_cursor.description
            column_names = [col[0] for col in desc]
            lst_dict_sql = [dict(itertools.izip(column_names, row))  for row in db_cursor.fetchall()]
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            lst_dict_sql= []
        finally:  
            return lst_dict_sql      

    def conta_ctrl_sessione(self,id_sessione):
        try:
            sql_cmd="SELECT Count(*) NUM_CTRL_TOT FROM ESECUZ es WHERE es.ID_SESSIONE=? " # ha senso il COALESCE con Count(*)?
            num_ctrl_totali=0  
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            db_cursor.execute(sql_cmd, [id_sessione])
            num_ctrl_totali=db_cursor.fetchone()[0]
            
            sql_cmd="SELECT Count(*) NUM_CTRL_ESE FROM ESECUZ es WHERE es.ID_SESSIONE=? AND es.STATO=0"
            num_ctrl_eseguiti=0  
            self.db_status=0
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            db_cursor.execute(sql_cmd, [id_sessione])
            num_ctrl_eseguiti=db_cursor.fetchone()[0]
            
            lst_num_ctrl=[num_ctrl_totali,num_ctrl_eseguiti]
            
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            lst_num_ctrl= [0,0]
        finally:  
            return lst_num_ctrl      
           
    def load_session(self, id_sessione):
        try:
            self.db_status=0            
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            sql_cmd="SELECT ID_SESSIONE, COD_CTS, CONSEGNA, DATA_INIZIO, PATH_DAT, PATH_CFG, PATH_LOG, OPERATORE, NOTE FROM SESSIONI WHERE ID_SESSIONE=?"
            db_cursor.execute(sql_cmd,[id_sessione])
#             db_cursor.execute(sql_cmd)
            sess=None
            for row in db_cursor.fetchall():
                sess=ClsSessione(row[1], row[2], row[3], row[4],row[5], row[6], row[7], row[8])
                sess.id_sessione=row[0]
            
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
#             sess = None
        finally:  
            return sess                                        

    def crea_db_diagn_vuoto(self,nome_file_db):
        msg_out='Errore: errore generico'
        try:
            db_diagn = sqlite3.connect(nome_file_db)
            #db_cursor = db_diagn.cursor()
            db_diagn.enable_load_extension(True)
            db_diagn.execute("SELECT load_extension('mod_spatialite')")
            db_diagn.execute("SELECT InitSpatialMetadata()")

            sql_cmd= "DROP TABLE IF EXISTS SESSIONI;"
            db_diagn.execute(sql_cmd)

            sql_cmd= "CREATE TABLE SESSIONI"
            sql_cmd+="("
            sql_cmd+="ID_SESSIONE INTEGER PRIMARY KEY, /* identificativo univoco */"
            sql_cmd+="COD_CTS TEXT, /* codice del contesto */"
            sql_cmd+="CONSEGNA TEXT, /* annotazione (libera) sulla consegna (lotto ecc.) */"
            sql_cmd+="DATA_INIZIO DATE, /* istante di apertura della sessione */"
            sql_cmd+="DATA_FINE DATE, /* istante di chiusura della sessione */"
            sql_cmd+="PATH_DAT TEXT, /* percorso del file spatialite col db dei dati da controllare */"
            sql_cmd+="PATH_CFG TEXT, /* percorso del file spatialite col db di configurazione (questo stesso)  */"
            sql_cmd+="PATH_LOG TEXT, /* percorso del file spatialite col db del log di output  */"
            sql_cmd+="OPERATORE TEXT, /* annotazione (libera) sull'operatore che ha lanciato i controlli */"
            sql_cmd+="NOTE TEXT /* eventuali note */"
            sql_cmd+=");"
            db_diagn.execute(sql_cmd)

            sql_cmd= "DROP TABLE IF EXISTS ESECUZ;"
            db_diagn.execute(sql_cmd)

            sql_cmd= "CREATE TABLE ESECUZ"
            sql_cmd+="("
            sql_cmd+="ID_ESECUZ INTEGER PRIMARY KEY, /* identificativo univoco */"
            sql_cmd+="COD_CTRL TEXT, /* codice del controllo */"
            sql_cmd+="DESCR_CTRL TEXT, /* descrizione del controllo */"
            sql_cmd+="DATA_INIZIO DATE, /* istante di inizio del controllo */"
            sql_cmd+="DATA_FINE DATE, /* istante di fine del controllo */"
            sql_cmd+="NUM_ERR INTEGER, /* numero degli errori individuati */"
            sql_cmd+="ID_SESSIONE INTEGER, /* riferimento alla sessione */"
            sql_cmd+="QUERY_SQL TEXT, /* query come viene eseguita (ovvero con le variabili sostituite) */"
            sql_cmd+="STATO INTEGER, /* stato dell'esecuzione: -1=aperta, 0=chiusa ok, 1=chiusa con errore durante la query */"
            sql_cmd+="MSG_ERR TEXT /* messaggio nel caso di stato di errore */"
            sql_cmd+=");"
            db_diagn.execute(sql_cmd)

            sql_cmd= "DROP TABLE IF EXISTS ERR_LOG;"
            db_diagn.execute(sql_cmd)

            sql_cmd= "CREATE TABLE ERR_LOG"
            sql_cmd+="("
            sql_cmd+="ID_ERR INTEGER PRIMARY KEY, /* identificativo univoco */"
            sql_cmd+="ID_ESECUZ INTEGER, /* riferimento alla esecuzione */"
            sql_cmd+="ALFA_ERR TEXT, /* risultato alfanumerico dell'errore */"
            sql_cmd+="GEOM_ERR GEOMETRY /* risultato geometrico dell'errore */"
            sql_cmd+=");"
            db_diagn.execute(sql_cmd)
            
            db_diagn.close()
            
            msg_out='ok'

        except Exception as e:
            msg_out='Errore: '+e.message
        finally:  
            return msg_out                                        
            
    def create_doc_mod_list(self):
        #return [{'COD_MOD':'pippo', 'DOC_MOD':'pluto'},{'COD_MOD':'minnie', 'DOC_MOD':'clarabella'}]
        if (not self.is_connected):
            self.err_msg="Occorre la connessione al DB di configurazione "
            self.db_status=1;
            return []
        
        doc_mod_list=[]
        try:
            self.db_status=0            
            self.err_msg=""
            db_cursor = self.db_conn.cursor()
            sql_cmd="SELECT COD_MOD, DOC_MOD FROM MODELLI"
            db_cursor.execute(sql_cmd)

            for row in db_cursor.fetchall():
                doc_mod_list.append({'COD_MOD':row[0], 'DOC_MOD':row[1]})
            
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
            doc_mod_list=[]
        finally:  
            return doc_mod_list                                        

    def get_versions(self):
        out_vers=[]
        if (not self.is_connected): out_vers
        try:
            db_cursor = self.db_conn.cursor()
            db_cursor.execute("select sqlite_version();")
            sqlite_vers=db_cursor.fetchone()[0] # attenzione! fetchone si svuota appena usato: non mettere in watch!
            db_cursor.execute("select spatialite_version();")
            spatial_vers=db_cursor.fetchone()[0] # attenzione! fetchone si svuota appena usato: non mettere in watch!
            out_vers=[sqlite_vers,spatial_vers]
        except Exception as e:
            out_vers=['errore',e.message]
        finally:  
            return out_vers
        
    def db_close(self):
        #if (not self.db_conn.is_connected): return self.db_status
        if (not self.is_connected): return self.db_status
        try:
            self.db_status=0
            self.err_msg=""
            self.db_conn.execute("DETACH DATABASE r")
            self.db_conn.execute("DETACH DATABASE l")
            self.db_conn.close()
            self.is_connected=False
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
        finally:  
            return self.db_status
    
    def test_r_tree(self):
        #sql_test='drop table if exists test_poi_butta_via'
        #self.db_conn.execute(sql_test)
        val_ret=False
        try:
            test_conn=sqlite3.connect(':memory:')
            test_cursor = test_conn.cursor()

            test_cursor.execute("drop table if exists test_poi_butta_via")

            test_cursor.execute("CREATE VIRTUAL TABLE test_poi_butta_via USING rtree (id, minx, miny, maxx, maxy)")

            test_cursor.execute("drop table if exists test_poi_butta_via")
            
            test_conn.close()
            val_ret=True
        except Exception as e:
            self.err_msg=e.message
            val_ret=False
        finally:  
            return val_ret

    def test_db_query(self):
        try:
            str_out=""
            
            db_conn=sqlite3.connect('C:/Users/utente/Desktop/GeoControlli_RT/prove/db_test.sqlite')
            db_conn.enable_load_extension(True)
            db_conn.execute("SELECT load_extension('mod_spatialite')")
            
            sql_cmd="select lay1.PK_UID, lay2.PK_UID"
            sql_cmd+=" from rt_0802_l lay1, rt_0201_a lay2"
            sql_cmd+=" where lay1.rowid in (select rowid from SpatialIndex where f_table_name = 'rt_0802_l' and search_frame = lay2.geometry)"

            result_set=db_conn.execute(sql_cmd)
            
            for row in result_set:
                str_out+='('+str(row[0])+'_'+str(row[1])+')'
                
            db_conn.close()
         
        except Exception as e:
            str_out='errore: '+e.message
            
        finally:    
            return str_out  
        
    def chk_geo_ndx(self, tbl_name):
        try:
            self.db_status=0            
            self.err_msg=""
            geo_ndx_list=[]
            db_cursor = self.db_conn.cursor()
            db_cursor2 = self.db_conn.cursor()
            sql_cmd="SELECT f_geometry_column, spatial_index_enabled FROM geometry_columns where f_table_name=?"
            db_cursor.execute(sql_cmd,[tbl_name])
            for row in db_cursor.fetchall():
                geo_name=row[0]
                ndx_pres=row[1]
                sql_cmd="select checkspatialindex(?, ?)"
                db_cursor2.execute(sql_cmd,[tbl_name,geo_name])
                ndx_ok=db_cursor2.fetchone()[0]
                geo_ndx_list.append({'GEO_NAME':geo_name, 'NDX_PRES':ndx_pres,'NDX_OK':ndx_ok})
        except Exception as e:
            self.db_status=1
            self.err_msg=e.message
        finally:  
            return geo_ndx_list        
'''
'''