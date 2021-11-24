# -*- mode: python ; coding: utf-8 -*-


block_cipher = pyi_crypto.PyiBlockCipher(key='Je892g6554a5be20')


a = Analysis(['app_locate.py'],
             pathex=['C:\\Users\\Microsoft\\AppData\\Local\\Programs\\Python\\Python38\\Lib\\site-packages\\cv2'],
             binaries=[],
             datas=[('config.ini','./'),('slices.dat','./'),('slices_19141051','./')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='GTAV赌场指纹解锁辅助',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          version='version_info.txt', icon='icon.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='GTAV赌场指纹解锁辅助_低内存')
