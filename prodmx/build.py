import pickle
from scipy.sparse import csr_matrix
from scipy.sparse import save_npz
from prodmx.util import sparse_row_col

def build_csr_matrix(out_fol_path, row, col, data, list_col, list_row):
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