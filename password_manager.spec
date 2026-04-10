# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 如果你有自定义图标，可以将其放入 icon.ico / icon.icns 并在此处引用
# icon_path = 'icon.ico' 

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[], # 如果有静态资源（如图片、QSS），在此添加，例如 [('ui/style.qss', 'ui')]
    hiddenimports=['PySide6', 'cryptography', 'sqlite3'],
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
    [],
    exclude_binaries=True,
    name='PasswordManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # 设为 False 以在 Windows 上运行且不弹出命令行窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PasswordManager',
)

# macOS 特有配置
app = BUNDLE(
    coll,
    name='PasswordManager.app',
    icon=None,
    bundle_identifier='com.passwordmanager.app',
)
