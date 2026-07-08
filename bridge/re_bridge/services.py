"""
services.py
Real Estate Management System
"""
import json
import os
import shutil
from .loader import call_dll_endpoint
from .exceptions import check_error
from .models import LoginRequest, PropertyDTO, SearchState

_current_db_path = "real_estate.db"

def re_init(db_path: str = "real_estate.db", migrations_path: str = "core/migrations") -> int:
    global _current_db_path
    _current_db_path = db_path
    from .loader import get_dll
    dll = get_dll()
    rc = dll.re_initialize(db_path.encode('utf-8'), migrations_path.encode('utf-8'))
    check_error(rc)
    return rc

def re_close() -> None:
    from .loader import get_dll
    dll = get_dll()
    dll.re_shutdown()

class AuthService:
    @staticmethod
    def login(req: LoginRequest) -> dict:
        req_json = json.dumps(req.to_dict())
        rc, res_json = call_dll_endpoint('re_login', req_json)
        check_error(rc)
        return json.loads(res_json)
        
    @staticmethod
    def logout(token: str) -> None:
        req_json = json.dumps({"token": token})
        rc, _ = call_dll_endpoint('re_logout', req_json)
        check_error(rc)

    @staticmethod
    def has_any_user() -> bool:
        rc, res_json = call_dll_endpoint('re_has_any_user', '{}')
        check_error(rc)
        data = json.loads(res_json)
        return data.get('has_users', False)
        
    @staticmethod
    def create_initial_admin(username, password) -> bool:
        req_json = json.dumps({"username": username, "password": password})
        rc, res_json = call_dll_endpoint('re_create_initial_admin', req_json)
        check_error(rc)
        data = json.loads(res_json)
        return data.get('status') == 'created'

    @staticmethod
    def change_password(username, current_password, new_password) -> bool:
        req_json = json.dumps({
            "username": username,
            "current_password": current_password,
            "new_password": new_password
        })
        rc, res_json = call_dll_endpoint('re_change_password', req_json)
        check_error(rc)
        data = json.loads(res_json)
        return data.get('status') == 'success'

class PropertyService:
    @staticmethod
    def create_property(token: str, prop: PropertyDTO) -> dict:
        payload = {"token": token, "property": prop.to_dict()}
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_create_property', req_json)
        check_error(rc)
        return json.loads(res_json)

    @staticmethod
    def update_property(token: str, prop_id: int, prop: PropertyDTO) -> None:
        payload = {"token": token, "id": prop_id, "property": prop.to_dict()}
        req_json = json.dumps(payload)
        rc, _ = call_dll_endpoint('re_update_property', req_json)
        check_error(rc)

    @staticmethod
    def get_properties(token: str, search_state=None) -> list[PropertyDTO]:
        state = search_state or SearchState()
        payload = {
            "token": token,
            "search_state": state.to_dict()
        }
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_get_properties', req_json)
        check_error(rc)
        data = json.loads(res_json)
        return [PropertyDTO(**item) for item in data.get('properties', [])]

    @staticmethod
    def archive_property(token: str, prop_id: int) -> None:
        payload = {"token": token, "id": prop_id}
        req_json = json.dumps(payload)
        rc, _ = call_dll_endpoint('re_archive_property', req_json)
        check_error(rc)

    @staticmethod
    def restore_property(token: str, prop_id: int) -> None:
        payload = {"token": token, "id": prop_id}
        req_json = json.dumps(payload)
        rc, _ = call_dll_endpoint('re_restore_property', req_json)
        check_error(rc)

class DashboardService:
    @staticmethod
    def get_dashboard_data(token: str) -> dict:
        payload = {"token": token}
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_get_dashboard', req_json)
        check_error(rc)
        return json.loads(res_json)

class ReportService:
    @staticmethod
    def export_properties_pdf(token: str, dest_path: str) -> None:
        payload = {"token": token}
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_get_report', req_json)
        check_error(rc)
        data = json.loads(res_json)
        properties = [PropertyDTO(**item) for item in data.get('properties', [])]
        
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        import arabic_reshaper
        from bidi.algorithm import get_display
        
        # Register Vazirmatn font for Persian/Arabic character rendering support
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        font_path = os.path.join(base_dir, 'assets', 'fonts', 'Vazirmatn-Regular.ttf')
        font_bold_path = os.path.join(base_dir, 'assets', 'fonts', 'Vazirmatn-Bold.ttf')
        
        has_font = False
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Vazirmatn', font_path))
                if os.path.exists(font_bold_path):
                    pdfmetrics.registerFont(TTFont('Vazirmatn-Bold', font_bold_path))
                else:
                    pdfmetrics.registerFont(TTFont('Vazirmatn-Bold', font_path))
                has_font = True
            except Exception:
                pass
                
        font_name = 'Vazirmatn' if has_font else 'Helvetica'
        font_bold_name = 'Vazirmatn-Bold' if has_font else 'Helvetica-Bold'
        
        def reshape_text(text: str) -> str:
            if not text:
                return ""
            try:
                return get_display(arabic_reshaper.reshape(str(text)))
            except Exception:
                return str(text)

        c = canvas.Canvas(dest_path, pagesize=letter)
        width, height = letter
        
        # Draw formal header panel
        c.setFillColor(colors.HexColor('#0f172a'))
        c.rect(30, height - 90, width - 60, 60, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont(font_bold_name, 16)
        c.drawRightString(width - 50, height - 60, reshape_text("گزارش جامع سیستم مدیریت املاک"))
        
        c.setFont(font_name, 9)
        c.drawRightString(width - 50, height - 80, reshape_text(f"تعداد کل املاک ثبت شده: {len(properties)} مورد"))
        c.drawString(50, height - 75, reshape_text("گزارش رسمی سیستم"))
        
        # Draw a separator
        c.setStrokeColor(colors.HexColor('#cbd5e1'))
        c.setLineWidth(1)
        c.line(30, height - 110, width - 30, height - 110)
        
        # Prepare table headers and records
        table_data = [
            [
                reshape_text("شناسه"),
                reshape_text("دسته‌بندی"),
                reshape_text("نوع معامله"),
                reshape_text("شهر"),
                reshape_text("منطقه"),
                reshape_text("آدرس"),
                reshape_text("متراژ (متر)"),
                reshape_text("قیمت / اجاره (تومان)")
            ]
        ]
        
        for p in properties:
            if p.listing_type == "فروش":
                price_str = f"{p.sale_price:,}"
            else:
                price_str = f"ودیعه: {p.rent_deposit:,} / اجاره: {p.rent_monthly:,}"
                
            table_data.append([
                str(p.id),
                reshape_text(p.category),
                reshape_text(p.listing_type),
                reshape_text(p.city),
                str(p.municipal_district),
                reshape_text(p.address),
                f"{p.area_sqm:,}",
                reshape_text(price_str)
            ])
            
        col_widths = [35, 60, 60, 60, 35, 150, 52, 100]
        chunk_size = 22
        chunks = [table_data[i:i + chunk_size] for i in range(1, len(table_data), chunk_size)]
        
        if not chunks:
            t_empty = Table([table_data[0], [reshape_text("هیچ ملکی ثبت نشده است"), "", "", "", "", "", "", ""]], colWidths=col_widths)
            t_empty.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), font_name),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('SPAN', (0,1), (-1,1)),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
            ]))
            _, te_height = t_empty.wrap(width - 60, height)
            t_empty.drawOn(c, 30, height - 140 - te_height)
            c.save()
            return
            
        for page_idx, chunk in enumerate(chunks):
            if page_idx > 0:
                c.showPage()
                c.setFillColor(colors.HexColor('#0f172a'))
                c.rect(30, height - 90, width - 60, 60, fill=True, stroke=False)
                c.setFillColor(colors.white)
                c.setFont(font_bold_name, 16)
                c.drawRightString(width - 50, height - 60, reshape_text("گزارش جامع سیستم مدیریت املاک"))
                c.setFont(font_name, 9)
                c.drawRightString(width - 50, height - 80, reshape_text(f"صفحه {page_idx + 1} از {len(chunks)}"))
                c.setStrokeColor(colors.HexColor('#cbd5e1'))
                c.line(30, height - 110, width - 30, height - 110)
                
            page_table_data = [table_data[0]] + chunk
            page_table = Table(page_table_data, colWidths=col_widths)
            page_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), font_bold_name),
                ('FONTNAME', (0,1), (-1,-1), font_name),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
            ]))
            _, pt_height = page_table.wrap(width - 60, height - 150)
            page_table.drawOn(c, 30, height - 130 - pt_height)
            
            c.setFillColor(colors.HexColor('#64748b'))
            c.setFont(font_name, 8)
            c.drawString(30, 30, reshape_text(f"گزارش جامع املاک | صفحه {page_idx + 1} از {len(chunks)}"))
            
        c.save()
        
        # Log export PDF action
        try:
            payload = {
                "token": token,
                "action": "EXPORT_PDF",
                "entity": "reports",
                "entity_id": 0,
                "old_values": "{}",
                "new_values": json.dumps({"dest_file": os.path.basename(dest_path)})
            }
            call_dll_endpoint('re_log_audit', json.dumps(payload))
        except Exception:
            pass

    @staticmethod
    def export_properties_excel(token: str, dest_path: str) -> None:
        payload = {"token": token}
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_get_report', req_json)
        check_error(rc)
        data = json.loads(res_json)
        properties = [PropertyDTO(**item) for item in data.get('properties', [])]
        
        import xlsxwriter
        
        workbook = xlsxwriter.Workbook(dest_path)
        worksheet = workbook.add_worksheet()
        
        # Enforce RTL layout in Excel sheet for Persian localization compatibility
        worksheet.right_to_left()
        
        # Styles formatting
        header_format = workbook.add_format({
            'bold': True,
            'font_name': 'Vazirmatn',
            'font_size': 11,
            'font_color': 'white',
            'bg_color': '#1e293b',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        cell_format = workbook.add_format({
            'font_name': 'Vazirmatn',
            'font_size': 10,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        headers = [
            "شناسه", "دسته‌بندی", "نوع معامله", "شهر", "منطقه شهرداری",
            "آدرس کامل", "تلفن مالک", "متراژ (متر مربع)", "قیمت فروش (تومان)",
            "مبلغ رهن (تومان)", "اجاره ماهیانه (تومان)"
        ]
        
        worksheet.set_row(0, 24)
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)
            
        # Standardized column widths
        col_widths = [8, 14, 14, 14, 15, 35, 16, 18, 20, 20, 20]
        for col_idx, width in enumerate(col_widths):
            worksheet.set_column(col_idx, col_idx, width)
            
        for row_num, p in enumerate(properties, start=1):
            worksheet.set_row(row_num, 20)
            worksheet.write(row_num, 0, p.id, cell_format)
            worksheet.write(row_num, 1, p.category, cell_format)
            worksheet.write(row_num, 2, p.listing_type, cell_format)
            worksheet.write(row_num, 3, p.city, cell_format)
            worksheet.write(row_num, 4, p.municipal_district, cell_format)
            worksheet.write(row_num, 5, p.address, cell_format)
            worksheet.write(row_num, 6, p.owner_phone, cell_format)
            worksheet.write(row_num, 7, p.area_sqm, cell_format)
            worksheet.write(row_num, 8, p.sale_price, cell_format)
            worksheet.write(row_num, 9, p.rent_deposit, cell_format)
            worksheet.write(row_num, 10, p.rent_monthly, cell_format)
            
        workbook.close()

        # Log export Excel action
        try:
            payload = {
                "token": token,
                "action": "EXPORT_EXCEL",
                "entity": "reports",
                "entity_id": 0,
                "old_values": "{}",
                "new_values": json.dumps({"dest_file": os.path.basename(dest_path)})
            }
            call_dll_endpoint('re_log_audit', json.dumps(payload))
        except Exception:
            pass

class BackupService:
    @staticmethod
    def create_backup(token: str, dest_path: str) -> str:
        re_close()
        try:
            shutil.copy2(_current_db_path, dest_path)
        finally:
            re_init(_current_db_path)
            
        # Write sidecar JSON metadata
        import datetime
        metadata = {
            "app_version": "2.0.0",
            "schema_version": 5,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": "system"
        }
        
        # Write sidecar JSON file
        try:
            with open(dest_path + ".json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4)
        except Exception:
            pass

        # Log backup event
        try:
            payload = {
                "token": token,
                "action": "BACKUP",
                "entity": "database",
                "entity_id": 0,
                "old_values": "{}",
                "new_values": json.dumps({"backup_file": os.path.basename(dest_path)})
            }
            call_dll_endpoint('re_log_audit', json.dumps(payload))
        except Exception:
            pass

        return dest_path

    @staticmethod
    def restore_backup(token: str, src_path: str) -> None:
        if not os.path.exists(src_path):
            raise FileNotFoundError("فایل بکاپ یافت نشد.")
            
        # Verify JSON sidecar metadata compatibility
        metadata_path = src_path + ".json"
        if not os.path.exists(metadata_path):
            raise ValueError("فایل متادیتای بکاپ (.json) یافت نشد.")
            
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except Exception as e:
            raise ValueError(f"خواندن متادیتای بکاپ ناموفق بود: {str(e)}")
            
        # Check compatibility: Mismatched major version
        app_version = "2.0.0"
        backup_version = meta.get("app_version", "0.0.0")
        
        try:
            app_major = int(app_version.split('.')[0])
            backup_major = int(str(backup_version).split('.')[0])
        except (ValueError, IndexError, TypeError):
            raise ValueError("فرمت نسخه پشتیبان نامعتبر است.")
            
        if backup_major > app_major:
            raise ValueError(f"نسخه بکاپ ({backup_version}) جدیدتر از نسخه نرم‌افزار ({app_version}) است.")
        if backup_major < app_major:
            raise ValueError(f"نسخه بکاپ ({backup_version}) قدیمی و ناسازگار با نسخه نرم‌افزار ({app_version}) است.")
            
        # Verify integrity of backup database before replacing
        import sqlite3
        conn = None
        try:
            conn = sqlite3.connect(src_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            res = cursor.fetchone()
            if not res or res[0] != "ok":
                raise ValueError("فایل بکاپ خراب یا نامعتبر است.")
            
            # Check row count and table structure compatibility
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            if not cursor.fetchone():
                raise ValueError("ساختار فایل بکاپ نامعتبر است.")
        except Exception as e:
            raise ValueError(f"اعتبارسنجی بکاپ با خطا مواجه شد: {str(e)}")
        finally:
            if conn:
                conn.close()
                
        re_close()
        try:
            shutil.copy2(src_path, _current_db_path)
        finally:
            re_init(_current_db_path)

        # Log restore event
        try:
            payload = {
                "token": token,
                "action": "RESTORE_DATABASE",
                "entity": "database",
                "entity_id": 0,
                "old_values": "{}",
                "new_values": json.dumps({"restore_file": os.path.basename(src_path)})
            }
            call_dll_endpoint('re_log_audit', json.dumps(payload))
        except Exception:
            pass

class UserManagementService:
    @staticmethod
    def get_all_users(token: str) -> list:
        req_json = json.dumps({"token": token})
        rc, res_json = call_dll_endpoint('re_get_users', req_json)
        check_error(rc)
        data = json.loads(res_json)
        return data.get('users', [])

    @staticmethod
    def create_user(token: str, user_data: dict) -> dict:
        payload = {"token": token, "user": user_data}
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_create_user', req_json)
        check_error(rc)
        return json.loads(res_json)

    @staticmethod
    def change_role(token: str, user_id: int, new_role_id: int) -> None:
        payload = {"token": token, "user_id": user_id, "new_role_id": new_role_id}
        req_json = json.dumps(payload)
        rc, _ = call_dll_endpoint('re_change_user_role', req_json)
        check_error(rc)

    @staticmethod
    def reset_password(token: str, user_id: int, new_password: str) -> None:
        payload = {"token": token, "user_id": user_id, "new_password": new_password}
        req_json = json.dumps(payload)
        rc, _ = call_dll_endpoint('re_reset_user_password', req_json)
        check_error(rc)

    @staticmethod
    def toggle_status(token: str, user_id: int, enable: bool) -> None:
        payload = {"token": token, "user_id": user_id, "enable": enable}
        req_json = json.dumps(payload)
        rc, _ = call_dll_endpoint('re_toggle_user_status', req_json)
        check_error(rc)
