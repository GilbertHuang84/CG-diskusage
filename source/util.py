import os
import constant


def human_size(number):
    current_idx = 0
    result = float(number)
    while result > constant.size_diff:
        if current_idx >= len(constant.size_unit):
            break
        result = result / constant.size_diff
        current_idx += 1
    return '{} {}'.format(round(result, constant.size_round), constant.size_unit[current_idx])


def classify_path(path, split_max, current_split=0):
    if current_split == split_max:
        yield list()
    else:
        split_path = path.split(os.path.sep)
        current_max_len = len(split_path) - split_max + current_split + 1
        for idx in range(current_max_len):
            next_values = classify_path(os.path.sep.join(split_path[idx + 1:]),
                                        current_split=current_split + 1,
                                        split_max=split_max)
            for next_value in next_values:
                yield [split_path[idx]] + next_value


def classify_possible_path(path):
    split_path_len = len(path.split(os.path.sep))
    for split_max in range(1, split_path_len + 1):
        for sort_key in classify_path(path=path, split_max=split_max):
            yield os.path.sep.join(sort_key)


def make_dictionary_by_classification(iterable, ignore_list=None):
    result = {}
    for child in iterable:
        child_path = child.part_path
        for sort_key in classify_possible_path(child_path):
            if ignore_list and sort_key in ignore_list:
                continue

            sort_value = result.setdefault(sort_key, dict())

            sort_value.setdefault(constant.sort_size_name, 0)
            sort_value[constant.sort_size_name] += child.total_size

            sort_children = sort_value.setdefault(constant.sort_children_name, list())
            sort_children.append(child)
    return result


def sorted_dictionary(dictionary, max_key=10):
    if max_key:
        return sorted(dictionary.items(), key=lambda item: item[1][constant.sort_size_name], reverse=True)[:max_key]
    else:
        return sorted(dictionary.items(), key=lambda item: item[1][constant.sort_size_name], reverse=True)
