import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


kospi_top5 = {
    'code': ['005930', '015760', '005380', '090430', '012330'],
    'name': ['삼성전자', '한국전력', '현대차', '아모레퍼시픽', '현대모비스'],
    'cprice': ['1,269,000', '60,100', '132,000', '414,500', '243,500']
}
column_idx_lookup = {'code': 0, 'name': 1, 'cprice': 2}

# QWidget instead of QMainWindow is used as a superclass to hold a layout of widgets
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(800, 200, 300, 600)
        self.setupSimpleUI()
        self.setupComplexUI()

        layout = QVBoxLayout()
        layout.addWidget(self.simpleTableWidget)
        layout.addWidget(self.tableWidget)

        self.setLayout(layout)

    # 2 x 2 simple table
    def setupSimpleUI(self):
        self.simpleTableWidget = QTableWidget(self)
        self.simpleTableWidget.resize(290, 290)
        self.simpleTableWidget.setRowCount(2)
        self.simpleTableWidget.setColumnCount(2)
        self.setSimpleTableWidgetData()

    def setSimpleTableWidgetData(self):
        self.simpleTableWidget.setItem(0, 0, QTableWidgetItem("(0,0)"))
        self.simpleTableWidget.setItem(0, 1, QTableWidgetItem("(0,1)"))
        self.simpleTableWidget.setItem(1, 0, QTableWidgetItem("(1,0)"))
        self.simpleTableWidget.setItem(1, 1, QTableWidgetItem("(1,1)"))

    # Sophisticated table
    def setupComplexUI(self):
        self.tableWidget = QTableWidget(self)
        self.tableWidget.resize(290, 290)
        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

    def setTableWidgetData(self):
        column_headers = ['종목코드', '종목명', '종가']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

        for k, v in kospi_top5.items():
            col = column_idx_lookup[k]
            for row, val in enumerate(v):
                item = QTableWidgetItem(val)
                if col == 2:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

                self.tableWidget.setItem(row, col, item)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()