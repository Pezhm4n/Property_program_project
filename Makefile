# Makefile for Property Management Library

# کامپایلر C
CC=gcc

# پرچم‌های کامپایلر
CFLAGS=-Wall -Wextra -pedantic -std=c11 -fPIC -I./include

# فایل‌های سورس
SRC_DIR=src
SRC_FILES=$(wildcard $(SRC_DIR)/*.c)
OBJ_FILES=$(SRC_FILES:.c=.o)

# نام کتابخانه
LIB_NAME=property_lib

# مسیر کتابخانه
LIB_DIR=lib

# تشخیص سیستم عامل
UNAME:=$(shell uname)
ifeq ($(UNAME), Linux)
    LIB_EXTENSION=so
    LIB_FLAGS=-shared
endif
ifeq ($(UNAME), Darwin)
    LIB_EXTENSION=dylib
    LIB_FLAGS=-dynamiclib
endif
ifeq ($(OS), Windows_NT)
    LIB_EXTENSION=dll
    LIB_FLAGS=-shared
endif

# نام کامل کتابخانه
SHARED_LIB=$(LIB_DIR)/lib$(LIB_NAME).$(LIB_EXTENSION)

# مسیر پوشه‌های خروجی
OUTPUT_DIRS=$(LIB_DIR)

# ساخت کتابخانه
all: $(OUTPUT_DIRS) $(SHARED_LIB)

# ساخت پوشه‌های خروجی
$(OUTPUT_DIRS):
	mkdir -p $@

# ساخت کتابخانه اشتراکی
$(SHARED_LIB): $(OBJ_FILES)
	$(CC) $(LIB_FLAGS) -o $@ $^ $(LDFLAGS)

# قوانین کامپایل فایل‌های .c به .o
$(SRC_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# نصب کتابخانه
install:
	mkdir -p $(DESTDIR)/usr/local/lib
	mkdir -p $(DESTDIR)/usr/local/include/$(LIB_NAME)
	cp $(SHARED_LIB) $(DESTDIR)/usr/local/lib/
	cp include/*.h $(DESTDIR)/usr/local/include/$(LIB_NAME)/

# پاک کردن فایل‌های موقت و کتابخانه
clean:
	rm -f $(SRC_DIR)/*.o
	rm -f $(SHARED_LIB)

# ساخت مثال‌ها
examples: $(SHARED_LIB)
	$(CC) $(CFLAGS) -o examples/user_example examples/user_example.c -L$(LIB_DIR) -l$(LIB_NAME)
	$(CC) $(CFLAGS) -o examples/property_example examples/property_example.c -L$(LIB_DIR) -l$(LIB_NAME)

# ایجاد مستندات با Doxygen
docs:
	doxygen Doxyfile

.PHONY: all clean install examples docs 