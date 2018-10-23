import os
import constant


def get_sort_keys(path, split_max, current_split=0):
    if current_split == split_max:
        yield list()
    else:
        split_path = path.split(os.path.sep)
        current_max_len = len(split_path) - split_max + current_split + 1
        for idx in range(current_max_len):
            next_values = get_sort_keys(os.path.sep.join(split_path[idx + 1:]),
                                        current_split=current_split + 1,
                                        split_max=split_max)
            for next_value in next_values:
                yield [split_path[idx]] + next_value


def get_all_sort_key(path):
    split_path_len = len(path.split(os.path.sep))
    for split_max in range(1, split_path_len + 1):
        for sort_key in get_sort_keys(path=path, split_max=split_max):
            yield os.path.sep.join(sort_key)


def collect_sort(iterable, ignore_list=None):
    result = {}
    for child in iterable:
        child_path = child.part_path
        for sort_key in get_all_sort_key(child_path):
            if ignore_list and sort_key in ignore_list:
                continue

            sort_value = result.setdefault(sort_key, dict())

            sort_value.setdefault(constant.sort_size_name, 0)
            sort_value[constant.sort_size_name] += child.total_size

            sort_children = sort_value.setdefault(constant.sort_children_name, list())
            sort_children.append(child)
    return result


def collect_sort_key(directory_info, max_level):
    return collect_sort(directory_info.get_children_by_level(level=max_level))


def sorted_collect_key(collect_key, max_key=10):
    if max_key:
        return sorted(collect_key.items(), key=lambda item: item[1][constant.sort_size_name], reverse=True)[:max_key]
    else:
        return sorted(collect_key.items(), key=lambda item: item[1][constant.sort_size_name], reverse=True)

