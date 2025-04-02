# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Determine the ffmpeg binary path based on platform
if sys.platform == 'win32':
    ffmpeg_binary = 'bin/ffmpeg.exe'
else:
    ffmpeg_binary = 'bin/ffmpeg'

# Add ffmpeg binary to the list of binaries
binaries = [(ffmpeg_binary, 'bin')]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=collect_submodules('pydub'),
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
    a.zipfiles,
    a.datas,
    [],
    name='automated_speaking_scorer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'  # Make sure to create this icon file
) 