import pickle
from collections import defaultdict
from scipy.sparse import csr_matrix
from scipy.sparse import save_npz

def build_csr_matrix(all_hmm_result):
    row = []
    col = []
    data = []

    list_col = []
    list_row = []

    with open(all_hmm_result, 'r') as f:
        for idx_row, line in enumerate(f, start=0):
            temp_line = line.strip().split("\t")
            assembly = temp_line[0]
            list_row.append(assembly)

            agg_cols = defaultdict(int)
            with open(temp_line[1], 'r') as arc_f:
                for arc_line in arc_f:
                    temp_arc_line = arc_line.strip().split("\t")
                    agg_cols[temp_arc_line[1]] += 1
            
            if len(agg_cols) > 0:
                for arc in agg_cols.keys():
                    if arc in list_col:
                        idx_col = list_col.index(arc)

                        row.append(idx_row)
                        col.append(idx_col)
                        data.append(agg_cols[arc])

                    else:
                        idx_col = len(list_col)

                        list_col.append(arc)

                        row.append(idx_row)
                        col.append(idx_col)
                        data.append(agg_cols[arc])
                
    csr_mat = csr_matrix((data, (row, col)), shape=(len(list_row),len(list_col)))
    npz_path = "{}/csr_matrix.npz".format(out_fol_path)
    save_npz(npz_path, csr_mat)

    csr_mat_bin = csr_matrix(([1 for x in range(len(data))], (row, col)), shape=(len(list_row),len(list_col)))
    npz_bin_path = "{}/csr_matrix_bin.npz".format(out_fol_path)
    save_npz(npz_bin_path, csr_mat_bin)

    obj_row_col = sparse_row_col(list_row = list_row,
                                list_col = list_col,
                                row = row,
                                col = col,
                                data = data)
    pickle_obj_row_col = "{}/obj_row_col.p".format(out_fol_path)
    pickle.dump(obj_row_col, open(pickle_obj_row_col, "wb"))