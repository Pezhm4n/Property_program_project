from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QSpinBox
from PySide6.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bridge')))
from re_bridge.models import PropertyDTO

class PropertyDialog(QDialog):
    def __init__(self, parent=None, property_dto=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("ثبت / ویرایش ملک")
        self.resize(420, 580)
        self.property_id = None
        self.is_archived = False
        self.original_dto = property_dto
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.cmb_category = QComboBox()
        self.cmb_category.addItems(["مسکونی", "تجاری", "زمین"])
        
        self.cmb_listing_type = QComboBox()
        self.cmb_listing_type.addItems(["فروش", "اجاره", "رهن"])
        
        self.txt_city = QLineEdit()
        self.txt_city.setText("تهران")
        
        self.spn_district = QSpinBox()
        self.spn_district.setRange(1, 22)
        
        self.txt_address = QLineEdit()
        self.txt_phone = QLineEdit()
        
        self.spn_area = QSpinBox()
        self.spn_area.setRange(1, 1000000)
        self.spn_area.setValue(100)
        
        self.spn_sale = QSpinBox()
        self.spn_sale.setRange(0, 2000000000)
        self.spn_sale.setSingleStep(100000)
        
        self.spn_deposit = QSpinBox()
        self.spn_deposit.setRange(0, 2000000000)
        self.spn_deposit.setSingleStep(100000)
        
        self.spn_rent = QSpinBox()
        self.spn_rent.setRange(0, 2000000000)
        self.spn_rent.setSingleStep(100000)
        
        form.addRow("نوع ملک:", self.cmb_category)
        form.addRow("نوع آگهی:", self.cmb_listing_type)
        form.addRow("شهر:", self.txt_city)
        form.addRow("منطقه:", self.spn_district)
        form.addRow("آدرس:", self.txt_address)
        form.addRow("شماره تماس:", self.txt_phone)
        form.addRow("متراژ (متر مربع):", self.spn_area)
        form.addRow("قیمت فروش:", self.spn_sale)
        form.addRow("مبلغ رهن:", self.spn_deposit)
        form.addRow("مبلغ اجاره:", self.spn_rent)
        
        layout.addLayout(form)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        # Initial focus UX
        self.txt_address.setFocus()
        
        if property_dto:
            self._load_dto(property_dto)
            
    def _load_dto(self, dto: PropertyDTO):
        self.property_id = dto.id
        self.is_archived = dto.is_archived
        self.cmb_category.setCurrentText(dto.category)
        self.cmb_listing_type.setCurrentText(dto.listing_type)
        self.txt_city.setText(dto.city)
        self.spn_district.setValue(dto.municipal_district)
        self.txt_address.setText(dto.address)
        self.txt_phone.setText(dto.owner_phone)
        self.spn_area.setValue(dto.area_sqm)
        self.spn_sale.setValue(dto.sale_price)
        self.spn_deposit.setValue(dto.rent_deposit)
        self.spn_rent.setValue(dto.rent_monthly)
        
    def accept(self):
        # 1. Strip input strings
        city = self.txt_city.text().strip()
        address = self.txt_address.text().strip()
        phone = self.txt_phone.text().strip()
        
        # Update text widgets
        self.txt_city.setText(city)
        self.txt_address.setText(address)
        self.txt_phone.setText(phone)
        
        # 2. Check for empty fields
        from ui.dialogs import show_error_dialog
        if not city:
            show_error_dialog(self, ValueError("لطفاً نام شهر را وارد کنید."))
            return
        if not address:
            show_error_dialog(self, ValueError("لطفاً آدرس ملک را وارد کنید."))
            return
        if not phone:
            show_error_dialog(self, ValueError("لطفاً شماره تماس مالک را وارد کنید."))
            return
            
        # 3. Validate phone format (starts with 09, 11 digits)
        if len(phone) != 11 or not phone.startswith("09") or not phone.isdigit():
            show_error_dialog(self, ValueError("شماره تماس معتبر نیست. باید ۱۱ رقم بوده و با ۰۹ شروع شود."))
            return
            
        # 4. Check listing pricing rules
        ltype = self.cmb_listing_type.currentText()
        if ltype == "فروش" and self.spn_sale.value() <= 0:
            show_error_dialog(self, ValueError("برای آگهی فروش، قیمت فروش باید بیشتر از صفر باشد."))
            return
        if (ltype == "اجاره" or ltype == "رهن") and (self.spn_deposit.value() <= 0 and self.spn_rent.value() <= 0):
            show_error_dialog(self, ValueError("برای آگهی رهن/اجاره، مبلغ رهن یا اجاره باید بیشتر از صفر باشد."))
            return
            
        super().accept()

    def get_dto(self) -> PropertyDTO:
        return PropertyDTO(
            id=self.property_id or 0,
            is_archived=self.is_archived,
            category=self.cmb_category.currentText(),
            listing_type=self.cmb_listing_type.currentText(),
            city=self.txt_city.text(),
            municipal_district=self.spn_district.value(),
            address=self.txt_address.text(),
            owner_phone=self.txt_phone.text(),
            area_sqm=self.spn_area.value(),
            sale_price=self.spn_sale.value(),
            rent_deposit=self.spn_deposit.value(),
            rent_monthly=self.spn_rent.value(),
            date_registered=self.original_dto.date_registered if self.original_dto else ""
        )
