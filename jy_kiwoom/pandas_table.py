import sys
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QTableView
class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None


if __name__ == '__main__':
    application = QApplication(sys.argv)

    raw_data = {'col0': [1, 2, 3, 4],
                'col1': [10, 20, 30, 40],
                'col2': [100, 200, 300, 400]}
    df = pd.DataFrame(raw_data)
    model = PandasModel(df)

    view = QTableView()
    view.setModel(model)

    view.show()
    sys.exit(application.exec_())