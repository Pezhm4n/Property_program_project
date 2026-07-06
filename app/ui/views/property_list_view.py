from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, 
                                 QMessageBox, QLineEdit, QPushButton, QLabel, QComboBox, QStackedWidget)
from PySide6.QtCore import Qt
from ui.widgets.empty_state import EmptyStateWidget
from ui.models.property_table_model import PropertyTableModel
from ui.dialogs.property_dialog import PropertyDialog
from ui.dialogs.filter_dialog import FilterDialog
from ui.dialogs import show_error_dialog, create_loading_dialog
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bridge')))
from re_bridge.services import PropertyService
from re_bridge.models import SearchState, SortingDTO

class PropertyListView(QWidget):
    def __init__(self, session_manager):
        super().__init__()
        self.session = session_manager
        self.search_state = SearchState()
        
        layout = QVBoxLayout(self)
        
        # --- Search Toolbar ---
        search_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("جستجو (کد ملک، عنوان، آدرس، مالک، تماس)...")
        self.txt_search.returnPressed.connect(self._on_search)
        
        btn_search = QPushButton("🔍 جستجو")
        btn_search.clicked.connect(self._on_search)
        
        btn_filter = QPushButton("🎛 فیلتر پیشرفته")
        btn_filter.clicked.connect(self._on_filter)
        
        btn_clear = QPushButton("❌ پاک کردن")
        btn_clear.clicked.connect(self._on_clear_filters)
        
        search_layout.addWidget(self.txt_search)
        search_layout.addWidget(btn_search)
        search_layout.addWidget(btn_filter)
        search_layout.addWidget(btn_clear)
        layout.addLayout(search_layout)
        
        # --- Stacked Widget containing Table and Empty State ---
        self.stack = QStackedWidget()
        
        self.table = QTableView()
        self.model = PropertyTableModel()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.doubleClicked.connect(self.edit_property)
        
        # Stateless sorting logic via header click
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        
        self.empty_state = EmptyStateWidget(
            message="هیچ ملکی یافت نشد",
            hint="با تغییر فیلترها یا دکمه افزودن، ملک جدید اضافه کنید."
        )
        
        self.stack.addWidget(self.table)
        self.stack.addWidget(self.empty_state)
        
        layout.addWidget(self.stack)
        
        # --- Pagination Toolbar ---
        page_layout = QHBoxLayout()
        self.btn_prev = QPushButton("◀ قبلی")
        self.btn_prev.clicked.connect(self._page_prev)
        self.lbl_page = QLabel("صفحه 1")
        self.btn_next = QPushButton("بعدی ▶")
        self.btn_next.clicked.connect(self._page_next)
        
        self.cmb_page_size = QComboBox()
        self.cmb_page_size.addItems(["20", "50", "100"])
        self.cmb_page_size.currentTextChanged.connect(self._on_page_size_changed)
        
        page_layout.addStretch()
        page_layout.addWidget(QLabel("تعداد در صفحه:"))
        page_layout.addWidget(self.cmb_page_size)
        page_layout.addWidget(self.btn_prev)
        page_layout.addWidget(self.lbl_page)
        page_layout.addWidget(self.btn_next)
        page_layout.addStretch()
        layout.addLayout(page_layout)
        
    def _on_search(self):
        self.search_state.query = self.txt_search.text().strip()
        self.search_state.pagination.page_number = 1
        self.refresh_data()
        
    def _on_filter(self):
        dlg = FilterDialog(self, self.search_state.filters)
        if dlg.exec():
            self.search_state.filters = dlg.get_filters()
            self.search_state.pagination.page_number = 1
            self.refresh_data()
            
    def _on_clear_filters(self):
        self.txt_search.clear()
        self.search_state.query = ""
        self.search_state.filters = {}
        self.search_state.pagination.page_number = 1
        self.refresh_data()
        
    def _on_header_clicked(self, logical_index):
        # Maps logical index to column names based on PropertyTableModel headers
        columns = ["id", "is_archived", "category", "listing_type", "municipal_district", 
                   "address", "owner_phone", "sale_price", "rent_deposit", "rent_monthly"]
        
        if 0 <= logical_index < len(columns):
            col_name = columns[logical_index]
            if self.search_state.sorting.column == col_name:
                self.search_state.sorting.ascending = not self.search_state.sorting.ascending
            else:
                self.search_state.sorting.column = col_name
                self.search_state.sorting.ascending = True
                
            # Update visual sort indicator
            order = Qt.SortOrder.AscendingOrder if self.search_state.sorting.ascending else Qt.SortOrder.DescendingOrder
            self.table.horizontalHeader().setSortIndicator(logical_index, order)
            
            self.refresh_data()
            
    def _page_prev(self):
        if self.search_state.pagination.page_number > 1:
            self.search_state.pagination.page_number -= 1
            self.refresh_data()
            
    def _page_next(self):
        # We allow next page blindly unless data is empty, logic can be refined
        if self.model.rowCount() > 0:
            self.search_state.pagination.page_number += 1
            self.refresh_data()
            
    def _on_page_size_changed(self, text):
        self.search_state.pagination.page_size = int(text)
        self.search_state.pagination.page_number = 1
        self.refresh_data()

    def refresh_data(self):
        loading = create_loading_dialog(self, "در حال دریافت اطلاعات...")
        loading.show()
        try:
            properties = PropertyService.get_properties(self.session.session_token, self.search_state)
            self.model.update_data(properties)
            self.lbl_page.setText(f"صفحه {self.search_state.pagination.page_number}")
            
            if len(properties) == 0:
                self.stack.setCurrentWidget(self.empty_state)
            else:
                self.stack.setCurrentWidget(self.table)
            
            # Disable next if returned items < page_size
            self.btn_next.setEnabled(len(properties) == self.search_state.pagination.page_size)
            self.btn_prev.setEnabled(self.search_state.pagination.page_number > 1)
        except Exception as e:
            show_error_dialog(self, e)
        finally:
            loading.close()
            
    def get_selected_property(self):
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self.model.get_property_at(indexes[0].row())

    def add_property(self):
        dlg = PropertyDialog(self)
        if dlg.exec():
            dto = dlg.get_dto()
            try:
                PropertyService.create_property(self.session.session_token, dto)
                self.refresh_data()
            except Exception as e:
                show_error_dialog(self, e)

    def edit_property(self):
        prop = self.get_selected_property()
        if not prop:
            QMessageBox.warning(self, "خطا", "لطفاً یک ملک را انتخاب کنید.")
            return
            
        dlg = PropertyDialog(self, prop)
        if dlg.exec():
            dto = dlg.get_dto()
            try:
                PropertyService.update_property(self.session.session_token, prop.id, dto)
                self.refresh_data()
            except Exception as e:
                show_error_dialog(self, e)

    def archive_property(self):
        prop = self.get_selected_property()
        if not prop:
            QMessageBox.warning(self, "خطا", "لطفاً یک ملک را انتخاب کنید.")
            return
            
        try:
            PropertyService.archive_property(self.session.session_token, prop.id)
            self.refresh_data()
        except Exception as e:
            show_error_dialog(self, e)

    def restore_property(self):
        prop = self.get_selected_property()
        if not prop:
            QMessageBox.warning(self, "خطا", "لطفاً یک ملک را انتخاب کنید.")
            return
            
        try:
            PropertyService.restore_property(self.session.session_token, prop.id)
            self.refresh_data()
        except Exception as e:
            show_error_dialog(self, e)

    def _show_context_menu(self, pos):
        prop = self.get_selected_property()
        if not prop:
            return
            
        from PySide6.QtGui import QAction, QCursor
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        act_edit = QAction("✏ ویرایش ملک", self)
        act_edit.triggered.connect(self.edit_property)
        
        if prop.is_archived:
            act_archive = QAction("📂 خروج از بایگانی", self)
            act_archive.triggered.connect(self.restore_property)
        else:
            act_archive = QAction("📁 بایگانی کردن", self)
            act_archive.triggered.connect(self.archive_property)
            
        menu.addAction(act_edit)
        menu.addAction(act_archive)
        
        menu.exec(QCursor.pos())
