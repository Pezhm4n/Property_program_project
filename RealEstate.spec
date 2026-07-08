# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Inject Anaconda environment binary path so PyInstaller can resolve Shiboken/Qt6 dependencies
conda_bin = r"C:\Users\Ariike.ir\anaconda3\envs\pythonProject5\Library\bin"
if os.path.exists(conda_bin):
    os.environ["PATH"] = conda_bin + os.pathsep + os.environ["PATH"]

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['app', 'bridge'],
    binaries=[('core/build/re_core.dll', '.')],
    datas=[
        ('core/migrations', 'core/migrations'),
        ('app/resources/styles', 'app/resources/styles'),
        ('assets/fonts', 'assets/fonts'),
        ('assets/images', 'assets/images'),
        ('assets/icon.png', 'assets')
    ],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui', 'reportlab', 'xlsxwriter', 'sqlite3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'pandas', 'scipy', 'matplotlib', 'tkinter', 'jedi', 'IPython', 'notebook', 'nbconvert', 'nbformat'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RealEstate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='assets/icon.ico',
)
