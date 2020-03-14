import sys
import textwrap
import argparse
from tqdm import tqdm
from collections import defaultdict
import prodmx.pfam_filter as pfam_filter
from prodmx.util import natural_sort, chk_mkdir
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

def build_dom(all_hmm_result_path):
    row = []
    col = []
    data = []

    list_col = []
    list_row = []

    list_all_hmm_result_path = []
    with open(all_hmm_result_path) as f:
        list_all_hmm_result_path = f.read().splitlines()

    for idx_row, line in enumerate(tqdm(list_all_hmm_result_path), start=0):
        temp_line = line.strip().split("\t")
        assembly = temp_line[0]
        hmm_result = temp_line[1]
        list_row.append(assembly)

        agg_cols = get_filtered_dom(hmm_result)
        
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

    print("\nmake folder for results at {}\n".format(out_fol_path))
    chk_mkdir(out_fol_path)

    print("\nfilter hmm results and make result objects\n")
    row, col, data, list_col, list_row = build_dom(all_hmm_result_path)

    print("\nwrite result objects to file\n")
    build_csr_matrix(out_fol_path, row, col, data, list_col, list_row)


if __name__ == "__main__":
    exit(main())