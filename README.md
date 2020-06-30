## ProdMX : Protein Functional Domain based on Compressed Sparse Matrices

ProdMX is a tool with user-friendly utilities developed to facilitate high-throughput analysis of protein functional domains and domain architectures. The ProdMX employs a compressed sparse matrix algorithm to reduce computational resources and time used to perform the matrix manipulation during functional domain analysis.

### Dependencies

* Python 3.5 or newer and the following packages:
    * [pandas](https://github.com/pandas-dev/pandas)
    * [h5py](https://github.com/h5py/h5py)
    * [numpy](https://github.com/numpy/numpy)
    * [tqdm](https://github.com/tqdm/tqdm)
    * [scipy](https://github.com/scipy/scipy)

### Installation from source

```
git clone https://github.com/visanuwan/prodmx
python -m pip install prodmx
```
### Usage

Generally, the use of the ProdMX tool starts with constructing the compressed sparse matrix of either protein functional domains or domain architectures in a command-line environment. The input of ProdMX is a tab-delimited file containing two columns of genome labels and the path to their HMMER results.

**Protein functional domain**

```
prodmx-buildDomain [-h] [-v] [-i INPUT] [-o OUTPUT] [-k]
```

**Domain architecture**

```
prodmx-buildArchitecture [-h] [-v] [-i INPUT] [-o OUTPUT] [-k]
```
For the detail of commands and examples, see the example of analyses using ProdMX in [Jupyter Notebook.](test/prodmx_example.ipynb)
