import os
from collections import OrderedDict
import constant
from util import human_size, sorted_dictionary, make_dictionary_by_classification


class DirectoryInfo(object):
    def __init__(self, name, parent=None):
        self.name = name
        self._dict_children = dict()
        self.parent = parent
        self.size = 0
        self._total_size = None
        self._sub_size = None
        if parent:
            parent.add_child(self)
            self.level = parent.level + 1
        else:
            self.level = 0

    def add_child(self, child):
        self._dict_children[child.name] = child

    def add_file(self, file_path):
        if os.path.isfile(file_path):
            file_size = os.stat(file_path).st_size
            self.size += file_size

    def get_children_by_level(self, level):
        for child in self._dict_children.values():
            if child.level < level:
                for grandson in child.get_children_by_level(level=level):
                    yield grandson
            if child.level == level:
                yield child
        if self.level == level:
            yield self

    def get_child(self, child_path, depth=0, max_depth=None):
        if depth == 0:
            format_string = u'{}{}'.format(self.name, os.sep)
            child_path = child_path.lstrip(format_string)

        if max_depth and depth >= max_depth:
            return self

        split_child_path = child_path.split(os.sep, 1)
        if not split_child_path:
            return self

        current_child_path = split_child_path[0]
        child = self._dict_children.get(current_child_path) or DirectoryInfo(current_child_path, parent=self)
        if len(split_child_path) == 1:
            return child

        rest_child_path = split_child_path[1]
        return child.get_child(rest_child_path, depth=depth + 1, max_depth=max_depth)

    @property
    def children_info(self):
        result = OrderedDict({
            '`total_size': human_size(self.total_size),
            '`part_path': self.part_path,
        })
        for child_name, child_item in self._dict_children.items():
            result[child_item.full_path] = child_item.children_info
        return result

    def _get_path(self, is_full_path=False):
        if self.parent:
            parent_name = self.parent._get_path(is_full_path=is_full_path)
            if not parent_name or parent_name.endswith(os.sep):
                return u'{}{}'.format(parent_name, self.name)
            else:
                return u'{}{}{}'.format(parent_name, os.sep, self.name)
        else:
            if is_full_path:
                return self.name
            else:
                return ''

    @property
    def full_path(self):
        return self._get_path(is_full_path=True)

    @property
    def part_path(self):
        return self._get_path(is_full_path=False)

    @property
    def sub_size(self):
        if self._sub_size is None:
            sub_size = 0
            for child in self._dict_children.values():
                sub_size += child.total_size
            self._sub_size = sub_size
        return self._sub_size

    @property
    def total_size(self):
        if self._total_size is None:
            self._total_size = self.sub_size + self.size
        return self._total_size


class LabelInfo(object):
    def __init__(self, collection):
        self._collection = collection
        self._sort_dictionary = None

    @property
    def sort_dictionary(self):
        if not self._sort_dictionary:
            self._sort_dictionary = sorted_dictionary(self._collection, max_key=None)
        return self._sort_dictionary

    def items(self):
        return self._collection.items()

    def get_keys(self):
        return self._collection.keys()

    def get_value(self, key):
        return self._collection.get(key)

    def get_directory_by_key(self, key):
        return sorted(self.get_value(key=key)[constant.sort_children_name],
                      key=lambda item: item.total_size, reverse=True)

    def get_children_by_key(self, key, ignore_list=None):
        dictionary = make_dictionary_by_classification(iterable=self.get_value(key=key)[constant.sort_children_name],
                                                       ignore_list=ignore_list)
        return LabelInfo(dictionary)
