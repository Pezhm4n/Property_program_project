"""
services.py
Real Estate Management System
"""
import json
import os
import shutil
from typing import Tuple
from .loader import call_dll_endpoint
from .exceptions import check_error
from .models import LoginRequest, LoginResponse, PropertyDTO, SearchState

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
    def login(req: LoginRequest) -> LoginResponse:
        req_json = json.dumps(req.to_dict())
        rc, res_json = call_dll_endpoint('re_login', req_json)
        check_error(rc)
        data = json.loads(res_json)
        return LoginResponse(token=data.get('token', ''))
        
    @staticmethod
    def logout(token: str) -> None:
        req_json = json.dumps({"token": token})
        rc, _ = call_dll_endpoint('re_logout', req_json)
        check_error(rc)

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
        
        c = canvas.Canvas(dest_path, pagesize=letter)
        width, height = letter
        
        c.drawString(100, height - 80, "Real Estate Management System - Properties Report")
        c.drawString(100, height - 100, f"Total Properties: {len(properties)}")
        
        y = height - 140
        for p in properties:
            if y < 50:
                c.showPage()
                y = height - 80
            text = f"ID: {p.id} | {p.category} | {p.listing_type} | {p.area_sqm} sqm | Price: {p.sale_price}"
            c.drawString(100, y, text)
            y -= 20
            
        c.save()

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
        
        headers = ["ID", "Category", "Listing Type", "City", "District", "Address", "Owner Phone", "Area (sqm)", "Price", "Deposit", "Rent"]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)
            
        for row_num, p in enumerate(properties, start=1):
            worksheet.write(row_num, 0, p.id)
            worksheet.write(row_num, 1, p.category)
            worksheet.write(row_num, 2, p.listing_type)
            worksheet.write(row_num, 3, p.city)
            worksheet.write(row_num, 4, p.municipal_district)
            worksheet.write(row_num, 5, p.address)
            worksheet.write(row_num, 6, p.owner_phone)
            worksheet.write(row_num, 7, p.area_sqm)
            worksheet.write(row_num, 8, p.sale_price)
            worksheet.write(row_num, 9, p.rent_deposit)
            worksheet.write(row_num, 10, p.rent_monthly)
            
        workbook.close()

class BackupService:
    @staticmethod
    def create_backup(token: str, dest_path: str) -> str:
        re_close()
        try:
            shutil.copy2(_current_db_path, dest_path)
        finally:
            re_init(_current_db_path)
        return dest_path
        
    @staticmethod
    def restore_backup(token: str, src_path: str) -> None:
        if not os.path.exists(src_path):
            raise FileNotFoundError("فایل بکاپ یافت نشد.")
        re_close()
        try:
            shutil.copy2(src_path, _current_db_path)
        finally:
            re_init(_current_db_path)
