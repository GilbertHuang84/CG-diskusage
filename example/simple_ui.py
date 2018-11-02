# coding:utf-8
import sys
from PySide.QtCore import Qt, QModelIndex
from PySide.QtGui import QApplication, QWidget
from PySide.QtGui import QVBoxLayout, QGridLayout, QHBoxLayout
from PySide.QtGui import QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem
import constant
import walk_folder
from data import LabelInfo
from util import human_size, make_dictionary_by_classification, sorted_dictionary


class DirectoryDetectWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle('Directory Detective Tool')
        main_layout = QVBoxLayout()

        path_layout = self._init_path_layout()
        guide_layout = self._init_guide_layout()
        detail_layout = self._init_detail_layout()

        main_layout.addLayout(path_layout)
        main_layout.addLayout(guide_layout)
        main_layout.addLayout(detail_layout)
        self.setLayout(main_layout)
        self.setGeometry(300, 300, 400, 350)
        self._connect()

        self._walk_folder = None
        self._last_path = None
        self.directory_info = None
        self._button_list = list()
        self._last_info = None

    def _init_path_layout(self):
        path_layout = QHBoxLayout()
        self.input_path = QLineEdit(self)
        self.input_path.setFixedHeight(35)
        self.input_path.setPlaceholderText('Type search path here')
        self.button_path = QPushButton('Scan', self)
        self.button_path.setFixedHeight(35)
        self.button_path.setFocus()

        path_layout.addWidget(QLabel('Path:', self))
        path_layout.addWidget(self.input_path, stretch=True)
        path_layout.addWidget(self.button_path)
        return path_layout

    def _init_guide_layout(self):
        self.guide_layout = QHBoxLayout()
        self.guide_layout.setAlignment(Qt.AlignLeft)
        return self.guide_layout

    def add_button(self, name, store_list):
        button = QPushButton(name)
        button.setFixedSize(60, 35)
        self._button_list.append((name, store_list))
        self.guide_layout.addWidget(button)
        self._refresh_key_tree(store_list)
        self._refresh_value_tree(store_list)

    def _init_detail_layout(self):
        detail_layout = QGridLayout()
        self.key_tree = QTreeWidget()
        self.key_tree.setColumnCount(2)
        self.key_tree.setColumnWidth(0, 200)
        self.key_tree.setHeaderLabels(['Key', 'Size'])

        self.value_tree = QTreeWidget()
        self.value_tree.setColumnCount(2)
        self.value_tree.setColumnWidth(0, 200)
        self.value_tree.setHeaderLabels(['Path', 'Size'])

        detail_layout.setColumnStretch(0, 1)
        detail_layout.setColumnStretch(1, 1)
        detail_layout.addWidget(self.value_tree)
        detail_layout.addWidget(self.key_tree)
        return detail_layout

    def _connect(self):
        self.button_path.clicked.connect(self.button_path_clicked)
        self.key_tree.doubleClicked.connect(self.key_tree_double_clicked)

    def button_path_clicked(self):
        del self._button_list[:]
        for _ in range(self.guide_layout.count()):
            current_item = self.guide_layout.takeAt(0)
            current_item.widget().setParent(None)

        path = unicode.encode(self.input_path.text())
        if self._last_path != path:
            self._walk_folder = walk_folder.run(path=path)

        max_level = 4
        self.directory_info = list(self._walk_folder.get_children_by_level(level=max_level))
        self.add_button('/', self.directory_info)

    def key_tree_double_clicked(self, selected_index=QModelIndex()):
        select_data = selected_index.data()
        ignore_list = [select_data]
        for item in self._button_list[1:]:
            ignore_list.append(item[0])

        store_dict = dict(self._last_info.get_children_by_key(key=select_data, ignore_list=ignore_list).sort_dictionary)
        store_list = list()

        for item in store_dict.values():
            store_list.extend(item['children'])

        store_list = list(set(store_list))
        self.add_button(select_data, store_list or list())

    def _get_size(self, size):
        return '{} <> {}%'.format(human_size(size), round(size * 100 / self._walk_folder.total_size, 2))

    def _refresh_key_tree(self, directory_info):
        info = LabelInfo(make_dictionary_by_classification(directory_info))

        # Clear
        for _ in range(self.key_tree.topLevelItemCount()):
            self.key_tree.takeTopLevelItem(0)

        # Add
        for k, v in info.sort_dictionary:
            tree_widget = QTreeWidgetItem()
            tree_widget.setText(0, k)
            total_size = 0
            for child in v['children']:
                total_size += child.total_size
            tree_widget.setText(1, self._get_size(v[constant.sort_size_name]))
            self.key_tree.addTopLevelItem(tree_widget)
        self._last_info = info

    def _refresh_value_tree(self, directory_info):
        info = sorted(directory_info, key=lambda x: x.total_size, reverse=True)

        # Clear
        for _ in range(self.value_tree.topLevelItemCount()):
            self.value_tree.takeTopLevelItem(0)

        # Add
        for item in info:
            tree_widget = QTreeWidgetItem()
            tree_widget.setText(0, item.part_path)
            tree_widget.setText(1, self._get_size(item.total_size))
            self.value_tree.addTopLevelItem(tree_widget)


if __name__ == '__main__':
     directory_detect_app = QApplication(sys.argv)
     directory_detect_window = DirectoryDetectWindow()
     directory_detect_window.show()
     directory_detect_app.exec_()
     sys.exit()
