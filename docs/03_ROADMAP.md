# ROADMAP

این نقشه راه، مسیر توسعه سیستم دسکتاپ مدیریت املاک را از معماری تا انتشار نهایی شرح می‌دهد. در حال حاضر **Phase 0 به صورت کامل پایان یافته و معماری تثبیت (Freeze) شده است.**

## Phase 0: Architecture Freeze (طراحی و تثبیت معماری)
هدف: نهایی‌سازی تمام تصمیمات معماری، ساختارها و APIها پیش از نوشتن حتی یک خط کد.
- [x] **Phase 0.1:** Vision + Scope + ADR + Roadmap
- [x] **Phase 0.2:** Architecture (Layers, Diagrams) + Folder Structure
- [x] **Phase 0.3:** Database Design (جداول، ویوها، ایندکس‌ها، تریگرها، و ER Diagram)
- [x] **Phase 0.4:** API Specification + JSON Schema + Error Codes
- [x] **Phase 0.5:** Coding Standards + Build Guide + Testing Strategy + Git Workflow + Definition of Done

## Phase 1: Repository Initialization (زیرساخت مخزن)
هدف: ایجاد ساختار پوشه‌ها و تنظیمات اولیه بیلد و CI.
- **پیش‌نیاز:** اتمام و تأیید کامل Phase 0.
- **خروجی:** ساختار کامل فولدرها، فایل `CMakeLists.txt` پایه، تنظیمات Pytest پایه، اسکریپت‌های اولیه، و راه‌اندازی GitHub Actions.

## Phase 2: Database & Core C Models (لایه داده در C)
- [ ] پیاده‌سازی مدیریت دیتابیس، مایگریشن‌ها و Repositoryها.

## Phase 3: Core Business Logic & Auth (لایه منطق در C)
- [ ] پیاده‌سازی اعتبارسنجی‌ها، Serviceها، DTOها و خروجی `re_core.dll`.

## Phase 4: Python Bridge (ارتباط C و Python)
- [ ] کلاس‌های واسط Python ctypes و Error Exception Mapping.

## Phase 5: GUI Foundation (پایه‌های رابط کاربری)
- [ ] PySide6 Main Window و Login Flow.

## Phase 6: GUI CRUD & Reports (تکمیل امکانات رابط کاربری)
- [ ] فرم‌های املاک، داشبورد، چارت‌ها و گزارش‌ها.

## Phase 6.5: Testing (تضمین کیفیت و تست‌های جامع)
- [ ] Unit Tests, Integration Tests, GUI Tests.

## Phase 7: Polish, Packaging & Release (بسته‌بندی و انتشار)
- [ ] ارائه Portable Distribution همراه با فایل اجرایی و نصاب.
