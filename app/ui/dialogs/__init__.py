from PySide6.QtWidgets import QMessageBox, QProgressDialog
from PySide6.QtCore import Qt

def show_error_dialog(parent, exception):
    dlg = QMessageBox(parent)
    dlg.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    dlg.setIcon(QMessageBox.Icon.Critical)
    
    if hasattr(exception, 'message') and hasattr(exception, 'code'):
        dlg.setWindowTitle("خطای سیستم")
        dlg.setText(f"{exception.message} (Code: {exception.code})")
        if exception.details:
            dlg.setDetailedText(exception.details)
    else:
        dlg.setWindowTitle("خطای ناشناخته")
        dlg.setText(str(exception))
        
    dlg.exec()

def create_loading_dialog(parent, title="در حال بارگذاری..."):
    dlg = QProgressDialog(title, None, 0, 0, parent)
    dlg.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    dlg.setWindowModality(Qt.WindowModality.WindowModal)
    dlg.setWindowTitle("لطفاً منتظر بمانید")
    dlg.setMinimumDuration(0)
    return dlg
