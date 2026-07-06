from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex

class PropertyTableModel(QAbstractTableModel):
    def __init__(self, properties=None):
        super().__init__()
        self._data = properties or []
        self._headers = [
            "شناسه", "وضعیت", "نوع ملک", "نوع آگهی", "منطقه", 
            "آدرس", "شماره تماس", "قیمت فروش", "رهن", "اجاره"
        ]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
            
        prop = self._data[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0: return str(prop.id)
            if col == 1: return "آرشیو شده" if prop.is_archived else "فعال"
            if col == 2: return prop.category
            if col == 3: return prop.listing_type
            if col == 4: return str(prop.municipal_district)
            if col == 5: return prop.address
            if col == 6: return prop.owner_phone
            if col == 7: return f"{prop.sale_price:,}" if prop.sale_price else "-"
            if col == 8: return f"{prop.rent_deposit:,}" if prop.rent_deposit else "-"
            if col == 9: return f"{prop.rent_monthly:,}" if prop.rent_monthly else "-"
            
        elif role == Qt.ItemDataRole.ForegroundRole:
            if prop.is_archived:
                # return a gray color for archived items
                from PySide6.QtGui import QColor
                return QColor(128, 128, 128)
                
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def update_data(self, new_data):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()

    def get_property_at(self, row):
        if 0 <= row < len(self._data):
            return self._data[row]
        return None
