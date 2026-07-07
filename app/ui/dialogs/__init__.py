from PySide6.QtWidgets import QMessageBox, QProgressDialog
from PySide6.QtCore import Qt

def show_error_dialog(parent, exception):
    dlg = QMessageBox(parent)
    dlg.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    dlg.setIcon(QMessageBox.Icon.Critical)
    
    title = "خطای سیستم"
    message_text = ""
    
    if hasattr(exception, 'code'):
        code = exception.code
        if code == -1:
            message_text = "اطلاعات وارد شده معتبر نیست. لطفاً فرمت فیلدها و مقادیر عددی را بررسی کنید."
        elif code == -2:
            message_text = "رکورد مورد نظر در پایگاه داده یافت نشد."
        elif code == -3:
            message_text = "این رکورد قبلاً در سیستم ثبت شده است و تکراری می‌باشد."
        elif code == -4:
            message_text = "نام کاربری یا کلمه عبور اشتباه است."
        elif code == -5:
            message_text = "حساب کاربری شما به دلیل تلاش‌های ناموفق مکرر قفل شده است. لطفاً ۵ دقیقه دیگر دوباره تلاش کنید."
        elif code == -6:
            message_text = "شما دسترسی لازم برای انجام این عملیات را ندارید."
        elif code == -99:
            message_text = "خطای داخلی سیستم رخ داده است. لطفاً مجدداً تلاش کنید."
        else:
            message_text = f"خطای ناشناخته در هسته برنامه رخ داد. (کد خطا: {code})"
            
        dlg.setWindowTitle(title)
        dlg.setText(message_text)
        if hasattr(exception, 'details') and exception.details:
            dlg.setDetailedText(exception.details)
    else:
        dlg.setWindowTitle("خطای برنامه")
        err_msg = str(exception)
        if "integrity_check" in err_msg or "integrity" in err_msg:
            err_msg = "اعتبارسنجی بکاپ با خطا مواجه شد. فایل پایگاه‌داده خراب یا ناسازگار است."
        dlg.setText(err_msg)
        
    dlg.exec()

def create_loading_dialog(parent, title="در حال بارگذاری..."):
    dlg = QProgressDialog(title, None, 0, 0, parent)
    dlg.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    dlg.setWindowModality(Qt.WindowModality.WindowModal)
    dlg.setWindowTitle("لطفاً منتظر بمانید")
    dlg.setMinimumDuration(0)
    return dlg
