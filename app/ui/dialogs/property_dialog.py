from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QSpinBox, QWidget
from PySide6.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bridge')))
from re_bridge.models import PropertyDTO

class PropertyDialog(QDialog):
    def __init__(self, parent=None, property_dto=None, token=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("ثبت / ویرایش ملک")
        self.resize(420, 580)
        self.property_id = None
        self.is_archived = False
        self.original_dto = property_dto
        self.token = token
        
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
        
        # Tab Order
        QWidget.setTabOrder(self.cmb_category, self.cmb_listing_type)
        QWidget.setTabOrder(self.cmb_listing_type, self.txt_city)
        QWidget.setTabOrder(self.txt_city, self.spn_district)
        QWidget.setTabOrder(self.spn_district, self.txt_address)
        QWidget.setTabOrder(self.txt_address, self.txt_phone)
        QWidget.setTabOrder(self.txt_phone, self.spn_area)
        QWidget.setTabOrder(self.spn_area, self.spn_sale)
        QWidget.setTabOrder(self.spn_sale, self.spn_deposit)
        QWidget.setTabOrder(self.spn_deposit, self.spn_rent)
        QWidget.setTabOrder(self.spn_rent, self.buttons)
        
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
        
    def validate_fields(self) -> list:
        default_style = ""
        error_style = "border: 1.5px solid #ef4444; background-color: #fef2f2;"
        
        self.txt_city.setStyleSheet(default_style)
        self.txt_address.setStyleSheet(default_style)
        self.txt_phone.setStyleSheet(default_style)
        self.spn_area.setStyleSheet(default_style)
        self.spn_sale.setStyleSheet(default_style)
        self.spn_deposit.setStyleSheet(default_style)
        self.spn_rent.setStyleSheet(default_style)
        
        city = self.txt_city.text().strip()
        address = self.txt_address.text().strip()
        phone = self.txt_phone.text().strip()
        
        errors = []
        if not city:
            self.txt_city.setStyleSheet(error_style)
            errors.append("نام شهر نمی‌تواند خالی باشد.")
            
        if not address:
            self.txt_address.setStyleSheet(error_style)
            errors.append("آدرس ملک نمی‌تواند خالی باشد.")
            
        if not phone:
            self.txt_phone.setStyleSheet(error_style)
            errors.append("شماره تماس مالک نمی‌تواند خالی باشد.")
        elif len(phone) != 11 or not phone.startswith("09") or not phone.isdigit():
            self.txt_phone.setStyleSheet(error_style)
            errors.append("شماره تماس باید ۱۱ رقم بوده و با ۰۹ شروع شود.")
            
        if self.spn_area.value() <= 0:
            self.spn_area.setStyleSheet(error_style)
            errors.append("متراژ ملک باید بیشتر از صفر باشد.")
            
        ltype = self.cmb_listing_type.currentText()
        if ltype == "فروش" and self.spn_sale.value() <= 0:
            self.spn_sale.setStyleSheet(error_style)
            errors.append("برای آگهی فروش، قیمت فروش باید بیشتر از صفر باشد.")
            
        if (ltype == "اجاره" or ltype == "رهن") and (self.spn_deposit.value() <= 0 and self.spn_rent.value() <= 0):
            self.spn_deposit.setStyleSheet(error_style)
            self.spn_rent.setStyleSheet(error_style)
            errors.append("برای آگهی رهن/اجاره، مبلغ رهن یا اجاره باید بیشتر از صفر باشد.")
            
        return errors

    def accept(self):
        # 1. Strip input strings
        city = self.txt_city.text().strip()
        address = self.txt_address.text().strip()
        phone = self.txt_phone.text().strip()
        
        # Update text widgets
        self.txt_city.setText(city)
        self.txt_address.setText(address)
        self.txt_phone.setText(phone)
        
        # 2. Inline client-side validations
        errors = self.validate_fields()
        if errors:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "خطای اعتبارسنجی", "\n".join(errors))
            return
            
        # 3. Try saving to DB inside accept() to preserve inputs on failure
        if self.token:
            from re_bridge.services import PropertyService
            from ui.dialogs import show_error_dialog
            dto = self.get_dto()
            try:
                if self.property_id:
                    PropertyService.update_property(self.token, self.property_id, dto)
                else:
                    PropertyService.create_property(self.token, dto)
            except Exception as e:
                # Highlight inputs if it is validation (-1) or duplicate (-3) error
                if hasattr(e, 'code') and e.code in (-1, -3):
                    error_style = "border: 1.5px solid #ef4444; background-color: #fef2f2;"
                    self.txt_phone.setStyleSheet(error_style)
                    self.txt_address.setStyleSheet(error_style)
                show_error_dialog(self, e)
                return  # Stay open!
                
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
