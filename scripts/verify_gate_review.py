"""
verify_gate_review.py
Executes and demonstrates all 8 gate checks for the Architecture Gate Review.
Located in scripts/
"""
import os
import sys
import json
import time

# Add re_bridge direct parent to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(root_dir, 'bridge'))
from re_bridge.services import re_init, re_close, AuthService, PropertyService, DashboardService, ReportService, BackupService
from re_bridge.models import LoginRequest, PropertyDTO, SearchState

def run_gate_review():
    print("==================================================")
    print("        ARCHITECTURE GATE REVIEW SYSTEM           ")
    print("==================================================")
    
    db_file = os.path.join(root_dir, "real_estate_gate.db")
    migrations_dir = os.path.join(root_dir, "core", "migrations")
    
    # Clean old db
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass
            
    # Gate 1 & 2: Build, DLL presence and Load DLL
    print("\n[Gate 1 & 2] Build Verification & DLL Loading...")
    t0 = time.perf_counter()
    try:
        re_init(db_file, migrations_dir)
        duration = int((time.perf_counter() - t0) * 1000)
        print(f" -> [PASS] C Core DLL successfully loaded and initialized DB. Execution Time: {duration} ms")
    except Exception as e:
        print(f" -> [FAIL] Failed to load DLL/init DB: {e}")
        return
    # Gate 3: Login Verification (using dynamically seeded admin)
    print("\n[Gate 3] Login Verification...")
    t0 = time.perf_counter()
    token = None
    try:
        # Seed initial admin user first since auto-seeding has been removed
        AuthService.create_initial_admin("admin", "password123")
        req = LoginRequest(username="admin", password="password123")
        resp = AuthService.login(req)
        token = resp.token
        duration = int((time.perf_counter() - t0) * 1000)
        print(f" -> [PASS] Login successful. Session token generated: {token}. Execution Time: {duration} ms")
    except Exception as e:
        print(f" -> [FAIL] Login failed: {e}")
        
    # Gate 4: Property Registration in SQLite C Core
    print("\n[Gate 4] Property Registration...")
    t0 = time.perf_counter()
    prop_id = None
    try:
        p = PropertyDTO(
            id=0, is_archived=False, category="مسکونی", listing_type="فروش",
            city="تهران", municipal_district=1, address="محله ۱، خیابان ولیعصر", owner_phone="09123456789",
            area_sqm=120, sale_price=25000000, rent_deposit=0, rent_monthly=0, date_registered="1405/04/16"
        )
        res = PropertyService.create_property(token, p)
        prop_id = res.get("id")
        duration = int((time.perf_counter() - t0) * 1000)
        print(f" -> [PASS] Property registered successfully. Generated ID: {prop_id}. Execution Time: {duration} ms")
    except Exception as e:
        print(f" -> [FAIL] Property registration failed: {e}")

    # Gate 5: Search & Filtering via C Core
    print("\n[Gate 5] Search & Filtering via C Core...")
    t0 = time.perf_counter()
    try:
        state = SearchState(query="ولیعصر")
        results = PropertyService.get_properties(token, state)
        duration = int((time.perf_counter() - t0) * 1000)
        if len(results) > 0 and results[0].id == prop_id:
            print(f" -> [PASS] Search returned matching property from C Core. ID: {results[0].id}. Execution Time: {duration} ms")
        else:
            print(f" -> [FAIL] Search returned 0 or mismatched results.")
    except Exception as e:
        print(f" -> [FAIL] Search failed: {e}")

    # Gate 6: Dashboard Statistics from C Core (No Placeholders)
    print("\n[Gate 6] Dashboard aggregation from Core...")
    t0 = time.perf_counter()
    try:
        data = DashboardService.get_dashboard_data(token)
        duration = int((time.perf_counter() - t0) * 1000)
        print(f" -> Active properties count: {data['active_properties']}")
        print(f" -> Archived properties count: {data['archived_properties']}")
        print(f" -> Total commissions: {data['charts']['financials']['commission']}")
        print(f" -> Total taxes: {data['charts']['financials']['tax']}")
        print(f" -> Recent audit activity: {data['recent_activities'][0]}")
        
        # Verify no placeholders
        if data['total_properties'] == 1 and len(data['recent_activities']) > 0:
            print(f" -> [PASS] Dashboard aggregates actual database rows and audit logs successfully. Execution Time: {duration} ms")
        else:
            print(" -> [FAIL] Dashboard contains placeholders or wrong aggregation values.")
    except Exception as e:
        print(f" -> [FAIL] Dashboard query failed: {e}")

    # Gate 7: PDF Export Generation
    print("\n[Gate 7] PDF Export...")
    pdf_file = os.path.join(root_dir, "properties_report.pdf")
    if os.path.exists(pdf_file):
        os.remove(pdf_file)
    t0 = time.perf_counter()
    try:
        ReportService.export_properties_pdf(token, pdf_file)
        duration = int((time.perf_counter() - t0) * 1000)
        
        # Enhanced validation
        exists = os.path.exists(pdf_file)
        size = os.path.getsize(pdf_file)
        valid_pdf_header = False
        if exists and size > 0:
            with open(pdf_file, 'rb') as f:
                header = f.read(4)
                if header == b"%PDF":
                    valid_pdf_header = True
                    
        if exists and size > 0 and valid_pdf_header:
            print(f" -> [PASS] PDF report generated successfully. Size: {size} bytes, Valid PDF Header check passed. Execution Time: {duration} ms")
            os.remove(pdf_file)
        else:
            print(f" -> [FAIL] PDF validation failed: exists={exists}, size={size}, valid_header={valid_pdf_header}")
    except Exception as e:
        print(f" -> [FAIL] PDF generation failed: {e}")

    # Gate 8: Backup and Restore Verification
    print("\n[Gate 8] Backup & Restore...")
    backup_file = os.path.join(root_dir, "real_estate_gate_backup.db")
    if os.path.exists(backup_file):
        os.remove(backup_file)
    t0 = time.perf_counter()
    try:
        # Get count before backup
        props_before = PropertyService.get_properties(token)
        count_before = len(props_before)
        
        # Create backup
        BackupService.create_backup(token, backup_file)
        backup_exists = os.path.exists(backup_file)
        
        # Write another property to modify DB
        p_extra = PropertyDTO(
            id=0, is_archived=False, category="تجاری", listing_type="اجاره",
            city="تهران", municipal_district=3, address="محله ۳", owner_phone="09123456789",
            area_sqm=50, sale_price=0, rent_deposit=10000000, rent_monthly=500000, date_registered="1405/04/16"
        )
        PropertyService.create_property(token, p_extra)
        
        # Restore backup
        BackupService.restore_backup(token, backup_file)
        
        # Get count after restore
        props_after = PropertyService.get_properties(token)
        count_after = len(props_after)
        
        duration = int((time.perf_counter() - t0) * 1000)
        
        if backup_exists and count_before == count_after and count_before == 1:
            print(f" -> [PASS] Backup file created. Database restore matches properties count before backup ({count_before} == {count_after}). Execution Time: {duration} ms")
        else:
            print(f" -> [FAIL] Backup/Restore validation failed. Backup Exists: {backup_exists}, Before: {count_before}, After: {count_after}")
            
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
