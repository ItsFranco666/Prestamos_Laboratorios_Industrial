# gestion_universitaria.spec

# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Define the base directory for assets
# Assuming 'assets' folder is at the same level as 'main.py'
# and 'views', 'utils' are subdirectories
basedir = os.path.abspath(os.path.dirname(sys.argv[0]))

a = Analysis(
    ['main.py'],
    pathex=[basedir], # Add the base directory to the path for modules
    binaries=[('libiconv.dll', 'libiconv.dll')],
    datas=[
        ('assets/app_icon.ico', 'assets'),
        ('assets/app_icon.png', 'assets'),
        ('assets/excel_icon.png', 'assets'),
        # Incluye todos los archivos de la carpeta assets
        ('assets/', 'assets'),
        ('uso_de_espacios.db', '.'),
        ('views', 'views'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        'customtkinter',
        'sqlite3',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'darkdetect',
        'pyzbar',
        'pyzbar.pyzbar',
        'cv2',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    a.datas,
    [],
    name='Sistema de Gestión de Laboratorios',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True, # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Set to True for console window (for debugging), False for no console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico',
    version='version_info.txt'
)