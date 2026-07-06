#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to compile the C library for the property management program.
This script automatically detects the Python architecture and compiles the appropriate library.
"""

import os
import sys
import platform
import struct
import subprocess
import shutil
import logging

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'compile_log.txt')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('compile_lib')

# Add console handler for logging
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

def get_python_bits():
    """Detect if Python is 32 or 64 bit"""
    return struct.calcsize("P") * 8

def find_visual_studio_paths():
    """Find possible paths for Visual Studio installations"""
    # Common paths where Visual Studio might be installed
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    
    vs_paths = []
    
    # Check for different versions of Visual Studio
    for base_dir in [program_files, program_files_x86]:
        # VS 2019
        vs2019_path = os.path.join(base_dir, "Microsoft Visual Studio", "2019")
        if os.path.exists(vs2019_path):
            for edition in ["Community", "Professional", "Enterprise", "BuildTools"]:
                edition_path = os.path.join(vs2019_path, edition)
                if os.path.exists(edition_path):
                    vs_paths.append(edition_path)
        
        # VS 2017
        vs2017_path = os.path.join(base_dir, "Microsoft Visual Studio", "2017")
        if os.path.exists(vs2017_path):
            for edition in ["Community", "Professional", "Enterprise", "BuildTools"]:
                edition_path = os.path.join(vs2017_path, edition)
                if os.path.exists(edition_path):
                    vs_paths.append(edition_path)
        
        # VS 2015
        vs2015_path = os.path.join(base_dir, "Microsoft Visual Studio 14.0")
        if os.path.exists(vs2015_path):
            vs_paths.append(vs2015_path)
    
    return vs_paths

def compile_with_msvc():
    """Compile the library using MSVC"""
    logger.info("Compiling with MSVC...")
    
    # Set up paths
    project_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_dir, "src")
    include_dir = os.path.join(project_dir, "include")
    lib_dir = os.path.join(project_dir, "lib")
    obj_dir = os.path.join(project_dir, "obj")
    
    # Create necessary directories
    os.makedirs(lib_dir, exist_ok=True)
    os.makedirs(obj_dir, exist_ok=True)
    
    # Check for source files
    c_files = [f for f in os.listdir(src_dir) if f.endswith('.c')]
    if not c_files:
        logger.error("No C source files found in the src directory!")
        return False
    
    # Determine compiler flags based on architecture
    python_bits = get_python_bits()
    if python_bits == 64:
        cflags = "/O2 /W3 /nologo /D_AMD64_ /D_WIN64 /DWIN64 /D_WINDOWS /DNDEBUG /MD"
        ldflags = "/DLL /MACHINE:X64 /NOLOGO /INCREMENTAL:NO"
    else:
        cflags = "/O2 /W3 /nologo /D_X86_ /DWIN32 /D_WINDOWS /DNDEBUG /MD"
        ldflags = "/DLL /MACHINE:X86 /NOLOGO /INCREMENTAL:NO"
    
    # Compile each source file
    object_files = []
    for c_file in c_files:
        src_file = os.path.join(src_dir, c_file)
        obj_file = os.path.join(obj_dir, c_file.replace('.c', '.obj'))
        object_files.append(f'"{obj_file}"')
        
        cmd = f'cl.exe {cflags} /I"{include_dir}" /c /Fo"{obj_file}" "{src_file}"'
        logger.info(f"Compiling {c_file}...")
        
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error compiling {c_file}: {e}")
            return False
    
    # Create the DLL
    output_dll = os.path.join(lib_dir, "property_lib.dll")
    cmd = f'link.exe {ldflags} /OUT:"{output_dll}" {" ".join(object_files)}'
    logger.info("Creating DLL...")
    
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating DLL: {e}")
        return False
    
    # Clean up object files
    for obj_file in os.listdir(obj_dir):
        if obj_file.endswith('.obj'):
            os.remove(os.path.join(obj_dir, obj_file))
    
    logger.info(f"DLL successfully created at: {output_dll}")
    return True

def compile_with_gcc():
    """Compile the library using GCC (MinGW)"""
    logger.info("Compiling with GCC...")
    
    # Set up paths
    project_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_dir, "src")
    include_dir = os.path.join(project_dir, "include")
    lib_dir = os.path.join(project_dir, "lib")
    
    # Create necessary directories
    os.makedirs(lib_dir, exist_ok=True)
    
    # Check for source files
    c_files = [f for f in os.listdir(src_dir) if f.endswith('.c')]
    if not c_files:
        logger.error("No C source files found in the src directory!")
        return False
    
    # Create source file list
    source_files = [os.path.join(src_dir, f) for f in c_files]
    source_files_str = ' '.join([f'"{f}"' for f in source_files])
    
    # Determine compiler flags based on architecture
    python_bits = get_python_bits()
    if python_bits == 64:
        arch_flag = "-m64"
    else:
        arch_flag = "-m32"
    
    # Output DLL path
    output_dll = os.path.join(lib_dir, "property_lib.dll")
    
    # Compile command
    cmd = f'gcc {arch_flag} -shared -o "{output_dll}" {source_files_str} -I"{include_dir}" -Wl,--out-implib,"{lib_dir}/libproperty.a" -O2'
    logger.info("Compiling DLL...")
    
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error compiling DLL: {e}")
        return False
    
    logger.info(f"DLL successfully created at: {output_dll}")
    return True

def main():
    """Main function to compile the library"""
    logger.info("Starting library compilation process...")
    
    # Check Python architecture
    python_bits = get_python_bits()
    logger.info(f"Python architecture: {python_bits}-bit")
    
    # Check for compilers
    try:
        subprocess.check_output("cl.exe", stderr=subprocess.STDOUT, shell=True)
        msvc_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        msvc_available = False
    
    try:
        subprocess.check_output("gcc --version", stderr=subprocess.STDOUT, shell=True)
        gcc_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        gcc_available = False
    
    if not msvc_available and not gcc_available:
        logger.error("No suitable compiler found. Please install Visual Studio with C++ tools or MinGW GCC.")
        return False
    
    # Let user choose compiler if both are available
    if msvc_available and gcc_available:
        print("\nAvailable compilers:")
        print("1. MSVC (Visual Studio)")
        print("2. GCC (MinGW)")
        
        choice = input("\nPlease enter the compiler number (1 or 2): ")
        if choice == "1":
            return compile_with_msvc()
        elif choice == "2":
            return compile_with_gcc()
        else:
            logger.error("Invalid choice. Exiting.")
            return False
    elif msvc_available:
        return compile_with_msvc()
    else:
        return compile_with_gcc()

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nCompilation completed successfully!")
        else:
            print("\nCompilation failed. Check logs for details.")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\nUnexpected error: {e}")
        sys.exit(1) 