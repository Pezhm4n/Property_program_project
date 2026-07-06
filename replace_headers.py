import os

c_files=['core/include/re_core.h','core/include/re_types.h','core/src/api/exports.c','core/src/services/auth_service.c','core/src/services/property_service.c','core/src/services/report_service.c','core/src/repository/db_connection.c','core/src/repository/user_repo.c','core/src/repository/property_repo.c','core/src/repository/audit_repo.c','core/src/repository/migrations.c','core/src/models/user_model.h','core/src/models/property_model.h','core/src/dto/json_parser.c','core/src/dto/dto_validators.c','core/src/errors/error_handler.c','core/tests/test_services/test_auth.c']
sql_files=['core/migrations/0001_initial.sql','core/migrations/0002_report_views.sql']
py_files=['bridge/setup.py','bridge/re_bridge/__init__.py','bridge/re_bridge/loader.py','bridge/re_bridge/exceptions.py','bridge/tests/__init__.py','app/main.py','app/tests/__init__.py']

for f in c_files:
    open(f,'w').write(f'/**\n * @file {os.path.basename(f)}\n * @brief Auto-generated skeleton file\n * @copyright Real Estate Management System\n */\n')

for f in sql_files:
    open(f,'w').write(f'-- Migration: {os.path.basename(f)}\n-- Description: Standard migration header\n-- Created at: 2026\n')

for f in py_files:
    open(f,'w').write(f'\"\"\"\n{os.path.basename(f)}\nReal Estate Management System\n\"\"\"\n')
