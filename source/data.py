import os
from collections import OrderedDict
from util import human_size


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

    def get_child(self, child_path, depth=0, max_depth=None):
        if depth == 0:
            format_string = u'{}{}'.format(self.name, os.sep)
            child_path = child_path.lstrip(format_string)

        if max_depth and depth >= max_depth:
            return self

        split_child_path = child_path.split(os.sep, 1)
        if len(split_child_path) < 1:
            return self

        current_child_path = split_child_path[0]
        if current_child_path in self._dict_children:
            child = self._dict_children[current_child_path]
        else:
            child = DirectoryInfo(current_child_path, parent=self)
        if len(split_child_path) == 1:
            return child

        rest_child_path = split_child_path[1]
        return child.get_child(rest_child_path, depth=depth + 1, max_depth=max_depth)

    @property
    def children_info(self):
        result = OrderedDict({
            '`total_size': human_size(self.total_size),
        })
        for child_name, child_item in self._dict_children.items():
            result[child_item.full_path] = child_item.children_info
        return result

    @property
    def full_path(self):
        if self.parent:
            parent_name = self.parent.full_path
            if parent_name.endswith(os.sep):
                return u'{}{}'.format(parent_name, self.name)
            else:
                return u'{}{}{}'.format(parent_name, os.sep, self.name)
        else:
            return self.name

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
