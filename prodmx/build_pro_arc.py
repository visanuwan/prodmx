import os
import sys
import sqlite3
import textwrap
import argparse
from tqdm import tqdm
from configparser import ConfigParser
from collections import defaultdict
import prodmx.pfam_filter as pfam_filter
from prodmx.util import natural_sort, chk_mkdir, sql_execute, sql_execute_record, sql_execute_record_get_lastrowid, sql_execute_record_get_fetchoneid
from prodmx.build import build_csr_matrix

def get_args():
    parser = argparse.ArgumentParser(
        description = textwrap.dedent('''\
            ProdMX - Protein Functional Domain Analysis
            based on Compressed Sparse Matrix
            *******************************************
            - Build a domain architecture matrix
        '''),
        prog = 'prodmx-buildArchitecture',
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s beta')
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='file containing IDs and paths to hmmsearch results'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='path to an output folder (not replace, if exists)'
    )
    parser.add_argument(
        '-k', '--keep',
        action='store_true',
        help='Store protein ids for further analyses'
    )
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return args

def get_filtered_arc(hmm_result):
    agg_cols = defaultdict(int)
    result_dict = pfam_filter.result_path_to_dict(hmm_result)
    for prot_id in natural_sort([*result_dict]):
        list_arc = []
        for prot_result in pfam_filter.filter_hmmsearch_result_list(result_dict.get(prot_id)):
            temp_result = prot_result.split('\t')
            list_arc.append(temp_result[5])
        architecture = "_".join(list_arc)
        if architecture != '':
            agg_cols[architecture] += 1
    return agg_cols

def get_filtered_arc_keep(db_path, config, genome_id, hmm_result):
    agg_cols = defaultdict(int)
    result_dict = pfam_filter.result_path_to_dict(hmm_result)

    conn = sqlite3.connect(db_path)

    for prot_acc in natural_sort([*result_dict]):
        list_arc = []

        for prot_result in pfam_filter.filter_hmmsearch_result_list(result_dict.get(prot_acc)):
            temp_result = prot_result.split('\t')
            list_arc.append(temp_result[5])
        architecture = "_".join(list_arc)
        if architecture != '':
            model_acc = architecture
            agg_cols[architecture] += 1

            # add to model table
            tup_record = (model_acc,)
            sql_execute_record(config['insert_model'].get('query'), tup_record, conn)

            # add to protein table
            tup_record = (prot_acc, genome_id)
            protein_id = sql_execute_record_get_lastrowid(config['insert_protein'].get('query'), tup_record, conn)

            # add to protein_model table
            # get model_id
            tup_record = (model_acc,)
            model_id = sql_execute_record_get_fetchoneid(config['select_model_id'].get('query'), tup_record, conn)

            # add to protein_model table
            tup_record = (protein_id, model_id)
            sql_execute_record(config['insert_protein_model'].get('query'), tup_record, conn)
    
    conn.commit()
    conn.close()
    
    return agg_cols

def build_arc(out_fol_path, args, config, all_hmm_result_path):
    row = []
    col = []
    data = []

    list_col = []
    list_row = []
    
    db_path = "{}/prodmx.db".format(out_fol_path)

    ############## create db ##############

    if args.keep:
        conn = sqlite3.connect(db_path)
        with conn:
            sql_execute(config['create_genome'].get('query'), conn)
            sql_execute(config['create_protein'].get('query'), conn)
            sql_execute(config['create_model'].get('query'), conn)
            sql_execute(config['create_protein_model'].get('query'), conn)

    ##############

    list_all_hmm_result_path = []
    with open(all_hmm_result_path) as f:
        list_all_hmm_result_path = f.read().splitlines()

    for idx_row, line in enumerate(tqdm(list_all_hmm_result_path), start=0):
        temp_line = line.strip().split("\t")
        assembly = temp_line[0]
        hmm_result = temp_line[1]
        list_row.append(assembly)

        ############## check keep ##############

        if args.keep:
            conn = sqlite3.connect(db_path)
            with conn:
                tup_record = (assembly,)
                genome_id = sql_execute_record_get_lastrowid(config['insert_genome'].get('query'), tup_record, conn)
            agg_cols = get_filtered_arc_keep(db_path, config, genome_id, hmm_result)
        else:
            agg_cols = get_filtered_arc(hmm_result)

        ##############
        
        if len(agg_cols) > 0:
            for col_id in agg_cols.keys():
                if col_id in list_col:
                    idx_col = list_col.index(col_id)

                    row.append(idx_row)
                    col.append(idx_col)
                    data.append(agg_cols[col_id])

                else:
                    idx_col = len(list_col)

                    list_col.append(col_id)

                    row.append(idx_row)
                    col.append(idx_col)
                    data.append(agg_cols[col_id])
    return row, col, data, list_col, list_row

def main():
    args = get_args()
    all_hmm_result_path = args.input
    out_fol_path = args.output

    template_query_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    config = ConfigParser()
    config.read(template_query_path)

    head_run = textwrap.dedent('''\
            ProdMX - Protein Functional Domain Analysis
            based on Compressed Sparse Matrix
            *******************************************
            - Build a domain architecture matrix
        ''')

    print(head_run)

    chk_mkdir(out_fol_path)

    print("\nfiltering hmm results and making result objects\n")
    row, col, data, list_col, list_row = build_arc(out_fol_path, args, config, all_hmm_result_path)

    print("\nwriting result objects to file\n")
    build_csr_matrix(out_fol_path, row, col, data, list_col, list_row)
    print("\nfinished\n")


if __name__ == "__main__":
    exit(main())