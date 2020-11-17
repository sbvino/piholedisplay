# Public methods
def dict_to_columns(cfg, dict):
    col_count = cfg.chart.col_count
    dict_length = len(dict);
    if dict_length == 0:
        return []

    if dict_length <= col_count:
        entries_per_column = 1
        col_count = dict_length
    else:
        entries_per_column = dict_length / col_count

    colums = [0] * col_count
    index_dict = 0

    for key in dict:
        index = int(index_dict / entries_per_column);
        if index >= col_count:
            continue
        colums[index] += dict[key]
        index_dict += 1

    return colums

def div_array(array, factor):
    return [int(i / factor) for i in array]