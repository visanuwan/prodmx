import sys
import prodmx.pfam_filter as pfam_filter
from prodmx.util import natural_sort

def main():
    hmm_result = sys.argv[1]
    result_dict = pfam_filter.result_path_to_dict(hmm_result)
    for prot_id in natural_sort([*result_dict]):
        for prot_result in pfam_filter.filter_hmmsearch_result_list(result_dict.get(prot_id)):
            temp_result = prot_result.split('\t')
            print(prot_id, temp_result[5])

if __name__ == "__main__":
    exit(main())