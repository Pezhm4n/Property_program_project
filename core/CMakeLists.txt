cmake_minimum_required(VERSION 3.20)
project(RealEstateCore VERSION 1.0.0 LANGUAGES C)

# Set C17 Standard
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Enable Warnings Policy based on Coding Standards
if(MSVC)
    add_compile_options(/W4 /WX) # /WX treats warnings as errors
else()
    add_compile_options(-Wall -Wextra -Werror)
endif()

# Core Shared Library
add_library(re_core SHARED
    src/api/exports.c
    src/services/auth_service.c
    src/services/property_service.c
    src/services/report_service.c
    src/repository/db_connection.c
    src/repository/user_repo.c
    src/repository/property_repo.c
    src/repository/audit_repo.c
    src/repository/migrations.c
    src/dto/json_parser.c
    src/dto/dto_validators.c
    src/errors/error_handler.c
)

# Includes
target_include_directories(re_core PUBLIC include)
target_include_directories(re_core PRIVATE src)

# Optional: Enable testing
enable_testing()
