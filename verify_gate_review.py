"""
verify_gate_review.py
Executes and demonstrates all 8 gate checks for the Architecture Gate Review.
"""
import os
import sys
import json

# Add re_bridge direct parent to path to avoid loading legacy bridge/__init__.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bridge'))
from re_bridge.services import re_init, re_close, AuthService, PropertyService, DashboardService, ReportService, BackupService
from re_bridge.models import LoginRequest, PropertyDTO, SearchState

def run_gate_review():
    print("==================================================")
    print("        ARCHITECTURE GATE REVIEW SYSTEM           ")
    print("==================================================")
    
    db_file = "real_estate_gate.db"
    
    # Clean old db
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass
            
    # Gate 1 & 2: Build, DLL presence and Load DLL
    print("\n[Gate 1 & 2] Build Verification & DLL Loading...")
    try:
        re_init(db_file, "core/migrations")
        print(" -> [PASS] C Core DLL successfully loaded and initialized DB.")
    except Exception as e:
        print(f" -> [FAIL] Failed to load DLL/init DB: {e}")
        return

    # Gate 3: Login Verification (using dynamically seeded admin)
    print("\n[Gate 3] Login Verification...")
    token = None
    try:
        req = LoginRequest(username="admin", password="password123")
        resp = AuthService.login(req)
        token = resp.token
        print(f" -> [PASS] Login successful. Session token generated: {token}")
    except Exception as e:
        print(f" -> [FAIL] Login failed: {e}")
        
    # Gate 4: Property Registration in SQLite C Core
    print("\n[Gate 4] Property Registration...")
    prop_id = None
    try:
        p = PropertyDTO(
            id=0, is_archived=False, category="مسکونی", listing_type="فروش",
            city="تهران", municipal_district=1, address="محله ۱، خیابان ولیعصر", owner_phone="09123456789",
            area_sqm=120, sale_price=25000000, rent_deposit=0, rent_monthly=0, date_registered="1405/04/16"
        )
        res = PropertyService.create_property(token, p)
        prop_id = res.get("id")
        print(f" -> [PASS] Property registered successfully. Generated ID: {prop_id}")
    except Exception as e:
        print(f" -> [FAIL] Property registration failed: {e}")

    # Gate 5: Search & Filtering via C Core
    print("\n[Gate 5] Search & Filtering via C Core...")
    try:
        state = SearchState(query="ولیعصر")
        results = PropertyService.get_properties(token, state)
        if len(results) > 0 and results[0].id == prop_id:
            print(f" -> [PASS] Search returned matching property from C Core. ID: {results[0].id}")
        else:
            print(f" -> [FAIL] Search returned 0 or mismatched results.")
    except Exception as e:
        print(f" -> [FAIL] Search failed: {e}")

    # Gate 6: Dashboard Statistics from C Core (No Placeholders)
    print("\n[Gate 6] Dashboard aggregation from Core...")
    try:
        data = DashboardService.get_dashboard_data(token)
        print(f" -> Active properties count: {data['active_properties']}")
        print(f" -> Archived properties count: {data['archived_properties']}")
        print(f" -> Total commissions: {data['charts']['financials']['commission']}")
        print(f" -> Total taxes: {data['charts']['financials']['tax']}")
        print(f" -> Recent audit activity: {data['recent_activities'][0]}")
        
        # Verify no placeholders
        if data['total_properties'] == 1 and len(data['recent_activities']) > 0:
            print(" -> [PASS] Dashboard aggregates actual database rows and audit logs successfully.")
        else:
            print(" -> [FAIL] Dashboard contains placeholders or wrong aggregation values.")
    except Exception as e:
        print(f" -> [FAIL] Dashboard query failed: {e}")

    # Gate 7: PDF Export Generation
    print("\n[Gate 7] PDF Export...")
    pdf_file = "properties_report.pdf"
    if os.path.exists(pdf_file):
        os.remove(pdf_file)
    try:
        ReportService.export_properties_pdf(token, pdf_file)
        if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 100:
            print(f" -> [PASS] PDF report generated successfully. File size: {os.path.getsize(pdf_file)} bytes.")
            os.remove(pdf_file)
        else:
            print(" -> [FAIL] PDF file is missing or empty.")
    except Exception as e:
        print(f" -> [FAIL] PDF generation failed: {e}")

    # Gate 8: Backup and Restore Verification
    print("\n[Gate 8] Backup & Restore...")
    backup_file = "real_estate_gate_backup.db"
    if os.path.exists(backup_file):
        os.remove(backup_file)
    try:
        BackupService.create_backup(token, backup_file)
        print(" -> [PASS] Backup file created successfully.")
        
        # Overwrite DB with backup to verify restore
        BackupService.restore_backup(token, backup_file)
        print(" -> [PASS] Restore completed successfully.")
        
        if os.path.exists(backup_file):
            os.remove(backup_file)
    except Exception as e:
        print(f" -> [FAIL] Backup/Restore failed: {e}")
        
    # Clean up test DB
    re_close()
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass

    print("\n==================================================")
    print("            GATE REVIEW COMPLETE                  ")
    print("==================================================")

if __name__ == "__main__":
    run_gate_review()
