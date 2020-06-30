import os
import sqlite3
import pickle
import pandas as pd
from configparser import ConfigParser
from scipy.sparse import load_npz
from prodmx.util import sparse_row_col, sql_select_list_model_protein

class loadMatrix(object):
    def __init__(self, matrix_fol):
        self.matrix_fol = matrix_fol
        self.path_matrix_csr = "{}/csr_matrix.npz".format(self.matrix_fol)
        self.path_obj_row_col = "{}/obj_row_col.p".format(self.matrix_fol)
        self.path_db = "{}/prodmx.db".format(self.matrix_fol)
        self.matrix = load_npz(self.path_matrix_csr)
        self.obj_pickle = pickle.load(open(self.path_obj_row_col, 'rb'))
        self.dict_row_pos = dict(zip(self.obj_pickle.list_row, [x for x in range(len(self.obj_pickle.list_row))]))
        self.dict_pos_row = {v: k for k, v in self.dict_row_pos.items()}
        self.dict_col_pos = dict(zip(self.obj_pickle.list_col, [x for x in range(len(self.obj_pickle.list_col))]))
        self.dict_pos_col = {v: k for k, v in self.dict_col_pos.items()}

    def getRow(self):
        return self.obj_pickle.list_row

    def getColumn(self):
        return self.obj_pickle.list_col
    
    def sumColumn(self, list_row, list_col):
        self.list_pos_row = [self.dict_row_pos.get(x) for x in list_row]
        self.list_pos_col = [self.dict_col_pos.get(x) for x in list_col]
        self.raw_sum_col = self.matrix[self.list_pos_row, :][:, self.list_pos_col].sum(axis=0)
        self.df_sum_col = pd.DataFrame([(x,y) for x,y in zip(list_col, self.raw_sum_col.A1)], columns=['col_name','col_sum'])
        return self.df_sum_col

    def sumRow(self, list_row, list_col):
        self.list_pos_row = [self.dict_row_pos.get(x) for x in list_row]
        self.list_pos_col = [self.dict_col_pos.get(x) for x in list_col]
        self.raw_sum_row = self.matrix[self.list_pos_row, :][:, self.list_pos_col].sum(axis=1)
        self.df_sum_row = pd.DataFrame([(x,y) for x,y in zip(list_row, self.raw_sum_row.A1)], columns=['row_name','row_sum'])
        return self.df_sum_row

    def calCore(self, list_row, list_col, direction='column', conservation=95):
        if direction == 'column':
            self.num_cutoff = round(len(list_row) * (conservation / 100.0))
            self.df_result = self.sumColumn(list_row=list_row, list_col=list_col)
            self.df_return = self.df_result[self.df_result['col_sum'] >= self.num_cutoff]
            return self.df_return
        if direction == 'row':
            self.num_cutoff = round(len(list_col) * (conservation / 100.0))
            self.df_result = self.sumRow(list_row=list_row, list_col=list_col)
            self.df_return = self.df_result[self.df_result['row_sum'] >= self.num_cutoff]
            return self.df_return

    def getProteinId(self, list_row, list_col, output):
        if os.path.isfile(self.path_db):
            template_query_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
            config = ConfigParser()
            config.read(template_query_path)
            conn = sqlite3.connect(self.path_db)
            with conn:
                list_result = sql_select_list_model_protein(list_row, list_col, config['select_model_protein'].get('query'), conn)
            df_result = pd.DataFrame(list_result)
            df_result.to_csv(output, sep='\t', index=False, header=False)
        else:
            error_msg = '''
                Database file does not exists.
                Please rebuilt a matrix folder with -k option
            '''
            print(error_msg)


class loadBinMatrix(object):
    def __init__(self, matrix_fol):
        self.matrix_fol = matrix_fol
        self.path_matrix_csr = "{}/csr_matrix_bin.npz".format(self.matrix_fol)
        self.path_obj_row_col = "{}/obj_row_col.p".format(self.matrix_fol)
        self.path_db = "{}/prodmx.db".format(self.matrix_fol)
        self.matrix = load_npz(self.path_matrix_csr)
        self.obj_pickle = pickle.load(open(self.path_obj_row_col, 'rb'))
        self.dict_row_pos = dict(zip(self.obj_pickle.list_row, [x for x in range(len(self.obj_pickle.list_row))]))
        self.dict_pos_row = {v: k for k, v in self.dict_row_pos.items()}
        self.dict_col_pos = dict(zip(self.obj_pickle.list_col, [x for x in range(len(self.obj_pickle.list_col))]))
        self.dict_pos_col = {v: k for k, v in self.dict_col_pos.items()}

    def getRow(self):
        return self.obj_pickle.list_row

    def getColumn(self):
        return self.obj_pickle.list_col
    
    def sumColumn(self, list_row, list_col):
        self.list_pos_row = [self.dict_row_pos.get(x) for x in list_row]
        self.list_pos_col = [self.dict_col_pos.get(x) for x in list_col]
        self.raw_sum_col = self.matrix[self.list_pos_row, :][:, self.list_pos_col].sum(axis=0)
        self.df_sum_col = pd.DataFrame([(x,y) for x,y in zip(list_col, self.raw_sum_col.A1)], columns=['col_name','col_sum'])
        return self.df_sum_col

    def sumRow(self, list_row, list_col):
        self.list_pos_row = [self.dict_row_pos.get(x) for x in list_row]
        self.list_pos_col = [self.dict_col_pos.get(x) for x in list_col]
        self.raw_sum_row = self.matrix[self.list_pos_row, :][:, self.list_pos_col].sum(axis=1)
        self.df_sum_row = pd.DataFrame([(x,y) for x,y in zip(list_row, self.raw_sum_row.A1)], columns=['row_name','row_sum'])
        return self.df_sum_row

    def calCore(self, list_row, list_col, direction='column', conservation=95):
        if direction == 'column':
            self.num_cutoff = round(len(list_row) * (conservation / 100.0))
            self.df_result = self.sumColumn(list_row=list_row, list_col=list_col)
            self.df_return = self.df_result[self.df_result['col_sum'] >= self.num_cutoff]
            return self.df_return
        if direction == 'row':
            self.num_cutoff = round(len(list_col) * (conservation / 100.0))
            self.df_result = self.sumRow(list_row=list_row, list_col=list_col)
            self.df_return = self.df_result[self.df_result['row_sum'] >= self.num_cutoff]
            return self.df_return

    def getProteinId(self, list_row, list_col, output):
        if os.path.isfile(self.path_db):
            template_query_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
            config = ConfigParser()
            config.read(template_query_path)
            conn = sqlite3.connect(self.path_db)
            with conn:
                list_result = sql_select_list_model_protein(list_row, list_col, config['select_model_protein'].get('query'), conn)
            df_result = pd.DataFrame(list_result)
            df_result.to_csv(output, sep='\t', index=False, header=False)
        else:
            error_msg = '''
                Database file does not exists.
                Please rebuilt a matrix folder with -k option
            '''
            print(error_msg)
    