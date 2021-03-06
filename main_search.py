# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import sys
from search_mag import AliRequest
from tools import *
from mag_search_ui import Ui_MainWindow
from web_thread import WebThread
from result_filter import ResultFilter


class MainSearchUi(QtGui.QMainWindow, Ui_MainWindow, QtToPython):
    def __init__(self):
        super(MainSearchUi, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('MagSearch V0.1.1')
        self.search_pushbutton.clicked.connect(self.search_button_clicked)
        self.result_treewidget.customContextMenuRequested.connect(self.result_tree_widget_context)
        self.resize_treewidget_column()
        self.exist_mag_list = []
        self.input_lineedit.setFocus(4)

    def keyPressEvent(self, e):
        if self.input_lineedit.hasFocus() and e.key() == QtCore.Qt.Key_Return:
            self.search_button_clicked()

    def resize_treewidget_column(self):
        self.result_treewidget.setColumnWidth(0, 300)
        self.result_treewidget.setColumnWidth(1, 100)
        self.result_treewidget.setColumnWidth(2, 400)

    def show_status(self, message, timeout=5):
        return self.statusbar.showMessage(message, timeout*1000)

    def get_search_text(self):
        return self.get_line_edit_unicode(self.input_lineedit)

    def search_button_clicked(self):
        self.search_clear()
        search_text = self.get_search_text()
        self.show_status(u"开始搜索 %s , 请稍后……" % search_text)
        self.web_thread = WebThread(search_text, AliRequest, self.get_page_num())
        self.web_thread.finishSignal.connect(self.web_thread_finished)
        self.web_thread.start()

    def get_page_num(self):
        return int(self.get_line_edit_unicode(self.pgnum_lineedit))

    def web_thread_finished(self, all_mag_list):
        self.filter_before_show(all_mag_list)

    def search_clear(self):
        self.result_treewidget.clear()
        self.exist_mag_list = []

    @log_wrap
    def filter_before_show(self, result):
        if result == ['FINISHED']:
            return self.remove_duplicate_mag(result)
        else:
            self.show_status(requests_error[result[0]]) if result in requests_error_list \
                else self.remove_duplicate_mag(result) if ResultFilter()(result, self.get_filter_dict(), 'one') else None

    def get_filter_dict(self):
        return {'contain': self.get_line_edit_unicode(self.filter_lineedit)
                if self.use_filter_checkbox.isChecked() else False, 'size': self.get_size_limit_from_gui()}

    def get_size_limit_from_gui(self):
        if self.size_limit_checkbox.isChecked():
            return [self.get_line_edit_int(self.more_than_lineedit)*1024*1024 if self.more_than_lineedit.text() else 0,
                    self.get_line_edit_int(self.less_than_lineedit)*1024*1024 if self.less_than_lineedit.text() else 10000000000000]
        else:
            return [False, False]

    @log_wrap
    def show_search_result_list(self, result_list):
        for result in result_list:
            self.show_status(requests_error[result[0]]) if result in requests_error_list \
                else self.remove_duplicate_mag(result)
            QtCore.QCoreApplication.processEvents()
        self.show_status(u"搜索结束!", 10)

    def remove_duplicate_mag(self, result):
        """
        
        :param result: 
        :return: 
        """
        if len(result) == 3:
            if result[2] not in self.exist_mag_list:
                self.exist_mag_list.append(result[2])
                return self.show_search_result(result)
        elif result == ['FINISHED']:
            return self.show_status(u"搜索结束! 搜索到 %s 条结果! " % self.result_treewidget.topLevelItemCount(), 0)

    def show_search_result(self, result):
        return self.result_treewidget.addTopLevelItem(QtGui.QTreeWidgetItem(result))

    def result_tree_widget_context(self):
        context_menu = QtGui.QMenu()
        context_menu.addAction(u"复制磁力链接", self.copy_magnet)
        context_menu.exec_(QtGui.QCursor.pos())

    def copy_magnet(self):
        clip = app.clipboard()
        clip.setText(self.get_current_item_string(self.result_treewidget, 2))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainSearchUi()
    window.show()
    sys.exit(app.exec_())



