# encoding=utf-8
import os
from data import DirectoryInfo


def run(path, folder_depth=4, limit_folder_count=None):
    path = unicode(path, 'utf-8')
    root = DirectoryInfo(name=path)
    index = 0
    for top, dirs, non_dirs in os.walk(path):
        child = root.get_child(top, max_depth=folder_depth)
        map(lambda non_dir: child.add_file(file_path=os.path.join(top, non_dir)), non_dirs)

        index += 1
        if limit_folder_count is not None and index >= limit_folder_count:
            break
    return root

