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
            message_text = "رکورد مورد نظر یافت نشد."
        elif code == -3:
            message_text = "این رکورد قبلاً در سیستم ثبت شده است و تکراری می‌باشد."
        elif code == -4:
            message_text = "نام کاربری یا کلمه عبور اشتباه است."
        elif code == -5:
            message_text = "حساب کاربری شما به دلیل تلاش‌های ناموفق مکرر قفل شده است. لطفاً ۵ دقیقه دیگر دوباره تلاش کنید."
        elif code == -6:
            message_text = "شما دسترسی لازم برای انجام این عملیات را ندارید."
        elif code == -7:
            message_text = "خطایی در پایگاه داده رخ داده است."
        elif code == -8:
            message_text = "نشست شما منقضی شده است. لطفاً دوباره وارد شوید."
        elif code == -10:
            message_text = "پایگاه داده شلوغ است. لطفاً چند لحظه دیگر دوباره تلاش کنید."
        elif code == -11:
            message_text = "پایگاه داده برنامه خراب شده است."
        elif code == -12:
            message_text = "عملیات غیرمجاز: امکان حذف، غیرفعال کردن یا دمو کردن آخرین مدیر سیستم یا خودتان وجود ندارد."
        elif code == -99:
            message_text = "خطای داخلی سیستم رخ داده است. لطفاً مجدداً تلاش کنید."
        else:
            message_text = f"خطای عملکردی در سیستم رخ داد. (کد: {code})"
            
        dlg.setWindowTitle(title)
        dlg.setText(message_text)
        
        details = getattr(exception, 'details', "")
        if details and not any(k in details for k in ["Traceback", "Exception", "File ", "line ", "at 0x"]):
            dlg.setDetailedText(details)
    else:
        dlg.setWindowTitle("خطای برنامه")
        err_msg = str(exception)
        if any(k in err_msg for k in ["Traceback", "Exception", "File ", "line ", "at 0x"]):
            message_text = "یک خطای غیرمنتظره در برنامه رخ داده است. لطفاً با پشتیبانی تماس بگیرید."
        elif "integrity_check" in err_msg or "integrity" in err_msg:
            message_text = "اعتبارسنجی بکاپ با خطا مواجه شد. فایل پایگاه‌داده خراب یا ناسازگار است."
        else:
            message_text = err_msg
        dlg.setText(message_text)
        
    dlg.exec()

def create_loading_dialog(parent, title="در حال بارگذاری..."):
    dlg = QProgressDialog(title, None, 0, 0, parent)
    dlg.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    dlg.setWindowModality(Qt.WindowModality.WindowModal)
    dlg.setWindowTitle("لطفاً منتظر بمانید")
    dlg.setMinimumDuration(0)
    return dlg
