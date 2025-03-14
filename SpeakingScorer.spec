# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('task_definitions.py', '.'), ('utils/config_manager.py', 'utils'), ('prompts/*', 'prompts/')],
    hiddenimports=['google.cloud.aiplatform', 'soundfile', 'librosa', 'numpy', 'pandas', 'xlsxwriter', 'PyQt6', 'json'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SpeakingScorer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='c:\\automated_speaking_scorer\\version_info.txt',
    uac_admin=True,
    icon=['c:\\automated_speaking_scorer\\resources\\app_icon.ico'],
)
