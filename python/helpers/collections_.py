'''The collections module has several helper functions to work with collections'''

from dotmap import DotMap

# Public methods
def dict_to_columns(cfg, data):
    '''Convert the dictionary to columns for use in the bar chart.

    Args:
        cfg (DotMap): The configuration.
        data (dict): The dictionary to be converted.

    Returns:
        list: A list of values.
    '''
    col_count = cfg.chart.col_count
    dict_length = len(data)
    if dict_length == 0:
        return []

    if dict_length <= col_count:
        entries_per_column = 1
        col_count = dict_length
    else:
        entries_per_column = dict_length / col_count

    colums = [0] * col_count
    index_dict = 0

    for key in data:
        index = int(index_dict / entries_per_column)
        if index >= col_count:
            continue
        colums[index] += data[key]
        index_dict += 1

    return colums

def div_array(array, factor):
    '''Divide every entry in the list by `factor`.

    Args:
        array (list): The list of values.
        factor (type): The division factor.

    Returns:
        list: The resulting list.
    '''
    return [int(i / factor) for i in array]

def dot_dict(**kwargs):
    '''Create a new `DotMap` for the passed named arguments.

    Args:
        **kwargs (Any): Named values to be inserted into the `DotMap`.

    Returns:
        DotMap: The dotmap.
    '''
    return DotMap(dict(kwargs))
