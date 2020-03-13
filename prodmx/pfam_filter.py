import os
from prodmx.util import natural_sort

def split_str_rem_whitespace(raw_string):
    result_list = [x.strip() for x in raw_string.split(' ') if x != '']
    return result_list

def result_path_to_dict(result_path):
    result_basename = os.path.basename(result_path).split('.')[0]
    temp_result_dict = {}

    with open(result_path,'r') as f:
        for line in f:
            if not line.startswith("#"):
                temp_line = [result_basename]
                temp_line += split_str_rem_whitespace(line)[:22]
                temp_line[5] = temp_line[5].split(".")[0]

                if temp_line[1] in temp_result_dict.keys():
                    temp_result_dict[temp_line[1]].append(temp_line)
                else:
                    temp_result_dict[temp_line[1]] = [temp_line]
    return temp_result_dict

def filter_hmmsearch_result_list(result_list_from_dict):
    gen_dict = {}    
    for res_list in result_list_from_dict:

        if (float(res_list[13]) > 0.01) or (float(res_list[14]) < 25):
            continue

        temp_t = (int(res_list[18]),int(res_list[19]))
    
        if not temp_t in gen_dict.keys():
            gen_dict[temp_t] = [float(res_list[13]), float(res_list[14]), "\t".join(res_list)]
        
    group_intv = []
    for j in sorted(gen_dict.keys()):
        if len(group_intv) != 0:
            flag = 0
            for k in group_intv:
                temp_k = sorted(k)
                if j[1] > temp_k[0][0] and j[0] < temp_k[-1][1]:
                    k.append(j)
                    flag = 1
                    continue
            if flag == 0:
                group_intv.append([j])
        else:
            group_intv.append([j])
            
    print_list = []
    for group in group_intv:
        if len(group) != 1:
            local_maxima = group[0]
            for sub_group in group[1:]:
                if gen_dict[sub_group][0] < gen_dict[local_maxima][0]:
                    local_maxima = sub_group
                    continue
                if gen_dict[sub_group][0] == gen_dict[local_maxima][0]:
                    if gen_dict[sub_group][1] > gen_dict[local_maxima][1]:
                        local_maxima = sub_group
             
            print_list.append(gen_dict[local_maxima][2])
        else:
            print_list.append(gen_dict[group[0]][2])
            
    return print_list