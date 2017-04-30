#! /usr/bin/env python3

import sys
import argparse
import os
from PyQt4 import QtCore
from PyQt4 import QtGui
from glob import glob
from operations import initiate_operation, is_writable


class HomeWidget(QtGui.QWidget):

    def __init__(self, status_bar, parent=None):
        super(HomeWidget, self).__init__(parent)
        self.status_bar = status_bar
        self.form = QtGui.QFormLayout()
        self.grid = QtGui.QGridLayout()
        self.source_widget = QtGui.QLineEdit()
        self.dst_widget = QtGui.QLineEdit()
        self.recursive = False
        self.sort = False
        self.add_content()
        self.setLayout(self.form)

    def add_content(self):
        self.add_path_button('Source')
        self.add_path_button('Destination')
        self.add_grid_content()

        verticalSpacer = QtGui.QSpacerItem(
            0, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.form.addItem(verticalSpacer)
        self.form.addRow(self.grid)

    def add_grid_content(self):
        sort_box = QtGui.QCheckBox('Sort folders')
        sort_box.stateChanged.connect(lambda x: self.check_box(x, box='sort'))

        recursive_box = QtGui.QCheckBox('Recursive')
        recursive_box.stateChanged.connect(
            lambda x: self.check_box(x, box='recursive'))

        run_button = QtGui.QPushButton('Run')
        run_button.setFixedWidth(70)
        run_button.clicked.connect(self.run_stuff)

        quit_button = QtGui.QPushButton('Quit')
        quit_button.setFixedWidth(70)
        quit_button.clicked.connect(self.close_widget)

        self.grid.addWidget(sort_box, 0, 0, QtCore.Qt.AlignLeft)
        self.grid.addWidget(recursive_box, 1, 0, QtCore.Qt.AlignLeft)
        self.grid.addWidget(run_button, 2, 0, QtCore.Qt.AlignLeft)
        self.grid.addWidget(quit_button, 2, 0, QtCore.Qt.AlignRight)

    def run_stuff(self):
        initiate_operation(src=self.source_widget.text(),
                           dst=self.dst_widget.text(),
                           sort=self.sort,
                           recur=self.recursive,
                           types=None,
                           status=self.status_bar,
                           gui='qt')

    def check_box(self, state, box=None):
        if box == 'sort':
            self.sort = bool(state)
        if box == 'recursive':
            self.recursive = bool(state)

    def add_path_button(self, label, display_text='Choose'):
        path_label = QtGui.QLabel(label.title())
        path_label.setAlignment(QtCore.Qt.AlignLeft)
        choice_button = QtGui.QPushButton(display_text)
        choice_button.resize(choice_button.minimumSizeHint())
        choice_button.clicked.connect(
            lambda: self.button_action(label.lower()))

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.switch_button(label.lower()))
        hbox.addWidget(choice_button)

        self.form.addRow(path_label, hbox)

    def button_action(self, text):
        diag = QtGui.QFileDialog.getExistingDirectory(self, 'Choose directory')
        self.switch_button(text).setText(diag)

    def switch_button(self, text):
        if text == 'source':
            return self.source_widget
        if text == 'destination':
            return self.dst_widget

    def close_widget(self):
        choice = QtGui.QMessageBox.question(
            self, 'Leave', 'Exit application?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            sys.exit()


class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(350, 200, 500, 200)
        self.setFixedSize(550, 250)
        self.setWindowTitle('Sorter')
        self.status_bar = QtGui.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.central_widget = HomeWidget(status_bar=self.status_bar)
        self.setCentralWidget(self.central_widget)
        self.init_menubar()
        self.setStyle(QtGui.QStyleFactory.create('Plastique'))
        self.show()

    def init_menubar(self):
        action_quit = QtGui.QAction("&Quit", self)
        action_quit.setShortcut("Ctrl+Q")
        action_quit.setStatusTip('Leave')
        action_quit.triggered.connect(self.close_application)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(action_quit)

    def close_application(self):
        choice = QtGui.QMessageBox.question(self,
                                            'Leave',
                                            'Exit application?',
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        if choice == QtGui.QMessageBox.Yes:
            sys.exit()


def run():
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument('source', help='Source directory', nargs=1)
        parser.add_argument('-d', '--destination',
                            help='Destination directory. Full path required.', nargs=1)
        parser.add_argument(
            '--sort-folders', help='Sort folders into categories', action='store_true')
        parser.add_argument('-r', '--recursive',
                            help='Recursively check into folders in the specified source directory.', action='store_true')
        parser.add_argument(
            '-t', '--types', help='File formats to sort.', nargs='+')
        options = vars(parser.parse_args())

        source_path = os.path.abspath(options['source'][0])
        proceed = True

        if options['destination']:
            destination_path = os.path.abspath(options['destination'][0])
        else:
            destination_path = source_path

        if options['types']:
            file_types = options['types']
            glob_pattern = '*.'
        else:
            file_types = ['*']
            glob_pattern = ''

        if not os.path.isdir(source_path):
            proceed = False
            print('Given source folder is NOT a folder.')
        else:
            if not is_writable(source_path):
                proceed = False

        if destination_path:
            if not os.path.isdir(destination_path):
                proceed = False
                print('Given destination folder is NOT a folder.')
            else:
                if not is_writable(destination_path):
                    proceed = False

        initiate_operation(src=source_path,
                           dst=destination_path,
                           sort=options['sort_folders'],
                           recur=options['recursive'],
                           types=file_types,
                           status=None,
                           parser=parser)
    else:
        try:
            import PyQt4
            run()
        except ImportError:
            from tkgui import TkGui
            app = TkGui()
            app.tk_run()
        