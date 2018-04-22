'''
Created on 19/set/2017

@author: Raffaele&Virgilio Factory
'''

class ClsSessione(object):
    '''
    classdocs
    '''

    def __init__(self, cod_cts, consegna, data_inizio, path_dat, path_cfg, path_log,operatore,note):
        self.id_sessione=0
        self.cod_cts=cod_cts
        self.consegna=consegna
        self.data_inizio=data_inizio
        self.path_dat=path_dat
        self.path_cfg=path_cfg
        self.path_log=path_log # meaningful?
        self.operatore=operatore
        self.note=note
