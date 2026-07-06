import json
import os
import shutil
import sqlite3
from typing import Tuple
from .loader import call_dll_endpoint
from .exceptions import check_error, NotImplementedError
from .models import LoginRequest, LoginResponse, PropertyDTO, SearchState

DB_PATH = "real_estate.db"

def init_local_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            is_archived INTEGER NOT NULL DEFAULT 0,
            category TEXT NOT NULL,
            listing_type TEXT NOT NULL,
            city TEXT NOT NULL,
            municipal_district INTEGER NOT NULL,
            address TEXT NOT NULL,
            owner_phone TEXT NOT NULL,
            area_sqm INTEGER NOT NULL,
            sale_price INTEGER NOT NULL,
            rent_deposit INTEGER NOT NULL,
            rent_monthly INTEGER NOT NULL,
            date_registered TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT NOT NULL
        )
    """)
    # Add some mock audit log if empty
    cursor.execute("SELECT COUNT(*) FROM audit_logs")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO audit_logs (timestamp, username, action, details)
            VALUES (?, ?, ?, ?)
        """, [
            ("1405/04/15 12:20", "admin", "CREATE_PROPERTY", "شناسه ملک: 1"),
            ("1405/04/15 11:45", "agent1", "ARCHIVE_PROPERTY", "شناسه ملک: 2"),
            ("1405/04/15 10:15", "admin", "UPDATE_PROPERTY", "شناسه ملک: 3")
        ])
    conn.commit()
    conn.close()

def calculate_financials(prop: PropertyDTO):
    # BR-001: Commission formula
    commission = 0.0
    tax = 0.0
    
    if prop.listing_type == "فروش":
        # BR-001: Commercial commission rate is 0.5%, Residential is 0.25%
        rate = 0.005 if prop.category == "تجاری" else 0.0025
        commission = prop.sale_price * rate
        tax = commission * 0.09
    elif prop.listing_type in ["اجاره", "رهن"]:
        # Converted monthly rent: 1 million deposit = 30,000 rent
        monthly_rent = prop.rent_monthly + (prop.rent_deposit * 0.03)
        # 25% of one month rent
        commission = monthly_rent * 0.25
        tax = commission * 0.09
        
    return {
        "commission": int(commission),
        "tax": int(tax),
        "total": int(commission + tax)
    }

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
        try:
            rc, res_json = call_dll_endpoint('re_create_property', req_json)
            check_error(rc)
            return json.loads(res_json)
        except NotImplementedError:
            init_local_db()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO properties (is_archived, category, listing_type, city, municipal_district, address, owner_phone, area_sqm, sale_price, rent_deposit, rent_monthly, date_registered)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                1 if prop.is_archived else 0,
                prop.category,
                prop.listing_type,
                prop.city,
                prop.municipal_district,
                prop.address,
                prop.owner_phone,
                prop.area_sqm,
                prop.sale_price,
                prop.rent_deposit,
                prop.rent_monthly
            ))
            new_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO audit_logs (timestamp, username, action, details)
                VALUES (datetime('now'), 'admin', 'CREATE_PROPERTY', ?)
            """, (f"Property ID: {new_id}",))
            conn.commit()
            conn.close()
            return {"id": new_id}

    @staticmethod
    def update_property(token: str, prop_id: int, prop: PropertyDTO) -> None:
        payload = {"token": token, "id": prop_id, "property": prop.to_dict()}
        req_json = json.dumps(payload)
        try:
            rc, res_json = call_dll_endpoint('re_update_property', req_json)
            check_error(rc)
        except NotImplementedError:
            init_local_db()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE properties
                SET is_archived = ?, category = ?, listing_type = ?, city = ?, municipal_district = ?, address = ?, owner_phone = ?, area_sqm = ?, sale_price = ?, rent_deposit = ?, rent_monthly = ?
                WHERE id = ?
            """, (
                1 if prop.is_archived else 0,
                prop.category,
                prop.listing_type,
                prop.city,
                prop.municipal_district,
                prop.address,
                prop.owner_phone,
                prop.area_sqm,
                prop.sale_price,
                prop.rent_deposit,
                prop.rent_monthly,
                prop_id
            ))
            cursor.execute("""
                INSERT INTO audit_logs (timestamp, username, action, details)
                VALUES (datetime('now'), 'admin', 'UPDATE_PROPERTY', ?)
            """, (f"Property ID: {prop_id}",))
            conn.commit()
            conn.close()

    @staticmethod
    def get_properties(token: str, search_state=None) -> list[PropertyDTO]:
        state = search_state or SearchState()
        payload = {
            "token": token,
            "search_state": state.to_dict()
        }
        req_json = json.dumps(payload)
        try:
            rc, res_json = call_dll_endpoint('re_get_properties', req_json)
            check_error(rc)
            data = json.loads(res_json)
            return [PropertyDTO(**item) for item in data.get('properties', [])]
        except NotImplementedError:
            init_local_db()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            query = "SELECT * FROM properties WHERE 1=1"
            params = []
            
            if state.query:
                query += " AND (address LIKE ? OR owner_phone LIKE ? OR category LIKE ?)"
                like_val = f"%{state.query}%"
                params.extend([like_val, like_val, like_val])
                
            filters = state.filters or {}
            if "category" in filters:
                query += " AND category = ?"
                params.append(filters["category"])
            if "is_archived" in filters:
                query += " AND is_archived = ?"
                params.append(1 if filters["is_archived"] else 0)
            if "city" in filters:
                query += " AND city = ?"
                params.append(filters["city"])
            if "district" in filters:
                query += " AND municipal_district = ?"
                params.append(filters["district"])
            if "min_price" in filters:
                query += " AND sale_price >= ?"
                params.append(filters["min_price"])
            if "max_price" in filters:
                query += " AND sale_price <= ?"
                params.append(filters["max_price"])
            if "min_area" in filters:
                query += " AND area_sqm >= ?"
                params.append(filters["min_area"])
            if "max_area" in filters:
                query += " AND area_sqm <= ?"
                params.append(filters["max_area"])
                
            sorting = state.sorting
            if sorting and sorting.column:
                direction = "ASC" if sorting.ascending else "DESC"
                valid_cols = ["id", "is_archived", "category", "listing_type", "municipal_district", 
                              "address", "owner_phone", "sale_price", "rent_deposit", "rent_monthly", "date_registered"]
                col = sorting.column if sorting.column in valid_cols else "date_registered"
                query += f" ORDER BY {col} {direction}"
                
            pag = state.pagination
            if pag:
                limit = pag.page_size
                offset = (pag.page_number - 1) * pag.page_size
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            properties = []
            for r in rows:
                properties.append(PropertyDTO(
                    id=r[0],
                    is_archived=bool(r[1]),
                    category=r[2],
                    listing_type=r[3],
                    city=r[4],
                    municipal_district=r[5],
                    address=r[6],
                    owner_phone=r[7],
                    area_sqm=r[8],
                    sale_price=r[9],
                    rent_deposit=r[10],
                    rent_monthly=r[11],
                    date_registered=r[12]
                ))
            return properties

    @staticmethod
    def archive_property(token: str, prop_id: int) -> None:
        payload = {"token": token, "id": prop_id}
        req_json = json.dumps(payload)
        try:
            rc, res_json = call_dll_endpoint('re_archive_property', req_json)
            check_error(rc)
        except NotImplementedError:
            init_local_db()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE properties SET is_archived = 1 WHERE id = ?", (prop_id,))
            cursor.execute("""
                INSERT INTO audit_logs (timestamp, username, action, details)
                VALUES (datetime('now'), 'admin', 'ARCHIVE_PROPERTY', ?)
            """, (f"Property ID: {prop_id}",))
            conn.commit()
            conn.close()

    @staticmethod
    def restore_property(token: str, prop_id: int) -> None:
        payload = {"token": token, "id": prop_id}
        req_json = json.dumps(payload)
        try:
            rc, res_json = call_dll_endpoint('re_restore_property', req_json)
            check_error(rc)
        except NotImplementedError:
            init_local_db()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE properties SET is_archived = 0 WHERE id = ?", (prop_id,))
            cursor.execute("""
                INSERT INTO audit_logs (timestamp, username, action, details)
                VALUES (datetime('now'), 'admin', 'RESTORE_PROPERTY', ?)
            """, (f"Property ID: {prop_id}",))
            conn.commit()
            conn.close()

class DashboardService:
    @staticmethod
    def get_dashboard_data(token: str) -> dict:
        payload = {"token": token}
        req_json = json.dumps(payload)
        try:
            rc, res_json = call_dll_endpoint('re_get_dashboard', req_json)
            check_error(rc)
            return json.loads(res_json)
        except NotImplementedError:
            init_local_db()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM properties")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM properties WHERE is_archived = 0")
            active = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM properties WHERE is_archived = 1")
            archived = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT username) FROM audit_logs")
            users = cursor.fetchone()[0] or 1
            
            cursor.execute("SELECT category, listing_type, sale_price, rent_deposit, rent_monthly FROM properties")
            props_data = cursor.fetchall()
            
            total_commission = 0
            total_tax = 0
            
            for r in props_data:
                p = PropertyDTO(
                    id=0, is_archived=False, category=r[0], listing_type=r[1],
                    city="Tehran", municipal_district=1, address="", owner_phone="",
                    area_sqm=0, sale_price=r[2], rent_deposit=r[3], rent_monthly=r[4],
                    date_registered=""
                )
                fin = calculate_financials(p)
                total_commission += fin["commission"]
                total_tax += fin["tax"]
                
            cursor.execute("SELECT timestamp, username, action, details FROM audit_logs ORDER BY id DESC LIMIT 5")
            activities = []
            for act in cursor.fetchall():
                activities.append({
                    "timestamp": act[0],
                    "user": act[1],
                    "action": act[2],
                    "details": act[3]
                })
                
            conn.close()
            
            return {
                "total_properties": total,
                "active_properties": active,
                "archived_properties": archived,
                "total_users": users,
                "total_agents": users,
                "last_update": "الان",
                "recent_activities": activities,
                "charts": {
                    "monthly_sales": [total * 2, total * 3, total],
                    "monthly_rents": [active, archived, total],
                    "financials": {
                        "commission": total_commission,
                        "tax": total_tax
                    }
                }
            }

class ReportService:
    @staticmethod
    def export_properties_pdf(token: str, dest_path: str) -> None:
        properties = PropertyService.get_properties(token)
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
        properties = PropertyService.get_properties(token)
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
        init_local_db()
        shutil.copy2(DB_PATH, dest_path)
        return dest_path
        
    @staticmethod
    def restore_backup(token: str, src_path: str) -> None:
        if not os.path.exists(src_path):
            raise FileNotFoundError("فایل بکاپ یافت نشد.")
        shutil.copy2(src_path, DB_PATH)
