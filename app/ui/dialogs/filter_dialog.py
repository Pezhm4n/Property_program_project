from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QSpinBox
from PySide6.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bridge')))
from re_bridge.models import SearchState

class FilterDialog(QDialog):
    def __init__(self, parent=None, current_filters=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("فیلتر پیشرفته")
        self.resize(380, 440)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.cmb_category = QComboBox()
        self.cmb_category.addItems(["همه", "مسکونی", "تجاری", "زمین"])
        
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["همه", "فعال", "آرشیو شده"])
        
        self.txt_city = QLineEdit()
        self.spn_district = QSpinBox()
        self.spn_district.setRange(0, 22)
        self.spn_district.setSpecialValueText("همه")
        
        self.spn_min_price = QSpinBox()
        self.spn_min_price.setRange(0, 2000000000)
        self.spn_min_price.setSingleStep(100000)
        self.spn_min_price.setSpecialValueText("نامحدود")
        
        self.spn_max_price = QSpinBox()
        self.spn_max_price.setRange(0, 2000000000)
        self.spn_max_price.setSingleStep(100000)
        self.spn_max_price.setSpecialValueText("نامحدود")
        self.spn_max_price.setValue(0)
        
        self.spn_min_area = QSpinBox()
        self.spn_min_area.setRange(0, 100000)
        self.spn_min_area.setSpecialValueText("نامحدود")
        
        self.spn_max_area = QSpinBox()
        self.spn_max_area.setRange(0, 100000)
        self.spn_max_area.setSpecialValueText("نامحدود")
        
        form.addRow("نوع ملک:", self.cmb_category)
        form.addRow("وضعیت:", self.cmb_status)
        form.addRow("شهر:", self.txt_city)
        form.addRow("منطقه:", self.spn_district)
        form.addRow("حداقل قیمت:", self.spn_min_price)
        form.addRow("حداکثر قیمت:", self.spn_max_price)
        form.addRow("حداقل متراژ:", self.spn_min_area)
        form.addRow("حداکثر متراژ:", self.spn_max_area)
        
        layout.addLayout(form)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        if current_filters:
            self._load_filters(current_filters)
            
    def _load_filters(self, filters: dict):
        if "category" in filters:
            self.cmb_category.setCurrentText(filters["category"])
        if "is_archived" in filters:
            self.cmb_status.setCurrentText("آرشیو شده" if filters["is_archived"] else "فعال")
        if "city" in filters:
            self.txt_city.setText(filters["city"])
        if "district" in filters:
            self.spn_district.setValue(filters["district"])
        if "min_price" in filters:
            self.spn_min_price.setValue(filters["min_price"])
        if "max_price" in filters:
            self.spn_max_price.setValue(filters["max_price"])
        if "min_area" in filters:
            self.spn_min_area.setValue(filters["min_area"])
        if "max_area" in filters:
            self.spn_max_area.setValue(filters["max_area"])
            
    def get_filters(self) -> dict:
        filters = {}
        if self.cmb_category.currentText() != "همه":
            filters["category"] = self.cmb_category.currentText()
            
        if self.cmb_status.currentText() != "همه":
            filters["is_archived"] = (self.cmb_status.currentText() == "آرشیو شده")
            
        if self.txt_city.text().strip():
            filters["city"] = self.txt_city.text().strip()
            
        if self.spn_district.value() > 0:
            filters["district"] = self.spn_district.value()
            
        if self.spn_min_price.value() > 0:
            filters["min_price"] = self.spn_min_price.value()
            
        if self.spn_max_price.value() > 0:
            filters["max_price"] = self.spn_max_price.value()
            
        if self.spn_min_area.value() > 0:
            filters["min_area"] = self.spn_min_area.value()
            
        if self.spn_max_area.value() > 0:
            filters["max_area"] = self.spn_max_area.value()
            
        return filters
