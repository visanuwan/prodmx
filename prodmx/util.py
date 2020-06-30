from os import mkdir
from os.path import isdir
from re import split
import itertools

class sparse_row_col(object):
    def __init__(self, **kwargs):
        self.list_row = kwargs.get("list_row")
        self.list_col = kwargs.get("list_col")
        self.row = kwargs.get("row")
        self.col = kwargs.get("col")
        self.data = kwargs.get("data")

    def get_list_row(self):
        return self.list_row

    def get_list_col(self):
        return self.list_col

    def get_row(self):
        return self.row

    def get_col(self):
        return self.col

    def get_data(self):
        return self.data

    def get_bin_data(self):
        return [1 for x in range(len(self.data))]

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

def chk_mkdir(d):
    if not isdir(d):
        print("\ncreates a new folder at {}\n".format(d))
        mkdir(d)

def sql_execute(sql, conn):
    c = conn.cursor()
    c.execute(sql)

def sql_execute_record(sql, tup_record, conn):
    c = conn.cursor()
    c.execute(sql, tup_record)
    
def sql_execute_record_get_lastrowid(sql, tup_record, conn):
    c = conn.cursor()
    c.execute(sql, tup_record)
    return c.lastrowid
    
def sql_execute_record_get_fetchoneid(sql, tup_record, conn):
    c = conn.cursor()
    return c.execute(sql, tup_record).fetchone()[0]

def sql_select_list_model_protein(list_genome, list_model, sql, conn):
    list_result = []
    for genome in list_genome:
        for model in list_model:
            c = conn.cursor()
            tup = (genome, model)
            list_result = list(itertools.chain(list_result, c.execute(sql, tup).fetchall()))
    return list_result