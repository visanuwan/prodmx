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
            Protein Functional Domain Analysis
            based on Compressed Sparse Matrix
            ************************************
            - Build a protein domain matrix
        '''),
        prog = 'prodmx-buildDomain',
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

def get_filtered_dom(hmm_result):
    agg_cols = defaultdict(int)
    result_dict = pfam_filter.result_path_to_dict(hmm_result)
    for prot_id in natural_sort([*result_dict]):
        for prot_result in pfam_filter.filter_hmmsearch_result_list(result_dict.get(prot_id)):
            temp_result = prot_result.split('\t')
            agg_cols[temp_result[5]] += 1
    return agg_cols

def get_filtered_dom_keep(db_path, config, genome_id, hmm_result):
    agg_cols = defaultdict(int)
    result_dict = pfam_filter.result_path_to_dict(hmm_result)

    conn = sqlite3.connect(db_path)

    for prot_acc in natural_sort([*result_dict]):
        set_domain_acc = set()

        for prot_result in pfam_filter.filter_hmmsearch_result_list(result_dict.get(prot_acc)):
            temp_result = prot_result.split('\t')
            agg_cols[temp_result[5]] += 1

            domain_acc = temp_result[5]
            set_domain_acc.add(domain_acc)

        if len(set_domain_acc) != 0:
            # add to domain table
            for domain_acc in set_domain_acc:
                tup_record = (domain_acc,)
                sql_execute_record(config['insert_domain'].get('query'), tup_record, conn)

            # add to protein table
            tup_record = (prot_acc, genome_id)
            protein_id = sql_execute_record_get_lastrowid(config['insert_protein'].get('query'), tup_record, conn)
    
            # add to protein_domain table
            for domain_acc in set_domain_acc:
                # get domain_id
                tup_record = (domain_acc,)
                domain_id = sql_execute_record_get_fetchoneid(config['select_domain_id'].get('query'), tup_record, conn)
        
                # add to protein_domain table
                tup_record = (protein_id, domain_id)
                sql_execute_record(config['insert_protein_domain'].get('query'), tup_record, conn)

    conn.commit()
    conn.close()

    return agg_cols

def build_dom(out_fol_path, args, config, all_hmm_result_path):
    row = []
    col = []
    data = []

    list_col = []
    list_row = []

    db_path = "{}/prodmx_dom.db".format(out_fol_path)

    ############## create db ##############

    if args.keep:
        conn = sqlite3.connect(db_path)
        with conn:
            sql_execute(config['create_genome'].get('query'), conn)
            sql_execute(config['create_protein'].get('query'), conn)
            sql_execute(config['create_domain'].get('query'), conn)
            sql_execute(config['create_protein_domain'].get('query'), conn)

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
            agg_cols = get_filtered_dom_keep(db_path, config, genome_id, hmm_result)
        else:
            agg_cols = get_filtered_dom(hmm_result)

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
            Protein Functional Domain Analysis
            based on Compressed Sparse Matrix
            ************************************
            - Build a protein domain matrix
        ''')

    print(head_run)

    chk_mkdir(out_fol_path)

    print("filtering hmm results and creating result objects\n")
    row, col, data, list_col, list_row = build_dom(out_fol_path, args, config, all_hmm_result_path)

    print("writing result objects to file\n")
    build_csr_matrix(out_fol_path, row, col, data, list_col, list_row)
    print("finished\n")

if __name__ == "__main__":
    exit(main())