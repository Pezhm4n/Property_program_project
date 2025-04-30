# Makefile برای پروژه مدیریت املاک
# متغیرهای مسیر
SRCDIR = src
INCDIR = include
OBJDIR = obj
LIBDIR = lib
TESTDIR = test
BINDIR = bin

# کامپایلر و فلگ‌ها
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -I$(INCDIR)
LDFLAGS = -shared

# تشخیص سیستم عامل
ifeq ($(OS),Windows_NT)
    SHARED_LIB = $(LIBDIR)/property_lib.dll
    SHARED_FLAG = -shared
    RM_CMD = del /F /Q
    MKDIR_CMD = mkdir
    PATH_SEP = \\
else
    SHARED_LIB = $(LIBDIR)/libproperty.so
    SHARED_FLAG = -shared -fPIC
    CFLAGS += -fPIC
    RM_CMD = rm -f
    MKDIR_CMD = mkdir -p
    PATH_SEP = /
endif

# لیست فایل‌های منبع
SOURCES = $(wildcard $(SRCDIR)/*.c)
OBJECTS = $(patsubst $(SRCDIR)/%.c,$(OBJDIR)/%.o,$(SOURCES))
HEADERS = $(wildcard $(INCDIR)/*.h)

# همه هدف‌ها
.PHONY: all clean directories test

all: directories $(SHARED_LIB)

# ایجاد دایرکتوری‌های مورد نیاز
directories:
	@if not exist $(OBJDIR) $(MKDIR_CMD) $(OBJDIR)
	@if not exist $(LIBDIR) $(MKDIR_CMD) $(LIBDIR)
	@if not exist $(BINDIR) $(MKDIR_CMD) $(BINDIR)

# قانون‌های ساخت
$(SHARED_LIB): $(OBJECTS)
	$(CC) $(SHARED_FLAG) -o $@ $^ $(LDFLAGS)
	@echo "کتابخانه با موفقیت ساخته شد: $(SHARED_LIB)"

$(OBJDIR)/%.o: $(SRCDIR)/%.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

# ساخت برنامه تست
test: directories $(SHARED_LIB)
	$(CC) $(CFLAGS) -o $(BINDIR)/test_property $(TESTDIR)/test_property.c -L$(LIBDIR) -lproperty
	@echo "برنامه تست با موفقیت ساخته شد: $(BINDIR)/test_property"

# تمیز کردن فایل‌های تولید شده
clean:
	$(RM_CMD) $(OBJDIR)$(PATH_SEP)*.o
	$(RM_CMD) $(SHARED_LIB)
	$(RM_CMD) $(BINDIR)$(PATH_SEP)*

# قوانین خاص برای کامپایل فایل‌های منبع اصلی
$(OBJDIR)/property.o: $(SRCDIR)/property.c $(INCDIR)/property.h
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJDIR)/residential.o: $(SRCDIR)/residential.c $(INCDIR)/residential.h
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJDIR)/commercial.o: $(SRCDIR)/commercial.c $(INCDIR)/commercial.h
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJDIR)/land.o: $(SRCDIR)/land.c $(INCDIR)/land.h
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJDIR)/user.o: $(SRCDIR)/user.c $(INCDIR)/user.h
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJDIR)/data_manager.o: $(SRCDIR)/data_manager.c $(INCDIR)/data_manager.h
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJDIR)/utils.o: $(SRCDIR)/utils.c $(INCDIR)/utils.h
	$(CC) $(CFLAGS) -c $< -o $@ 