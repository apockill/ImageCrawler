# -*- mode: python -*-

block_cipher = None

# Fix missing DLL problems
added_files = [
               ('C:\\Users\\Alex Thiel\\Envs\\nvidia\\Lib\\site-packages\\PyQt5\\Qt\\bin\\Qt5Core.dll', '.'),
               ('C:\\Users\\Alex Thiel\\Envs\\nvidia\\Lib\\site-packages\\PyQt5\\Qt\\bin\\Qt5Gui.dll', '.'),
               ('C:\\Users\\Alex Thiel\\Envs\\nvidia\\Lib\\site-packages\\PyQt5\\Qt\\bin\\Qt5Widgets.dll', '.')
              ]


a = Analysis(['main.py'],
             pathex=['C:\\Users\\Alex Thiel\\Google Drive\\Projects\\Project - 2017 - NVIDIA Marketing Tool\\ImageCrawler',
		     'C:\\Users\\Alex Thiel\\Envs\\nvidia\\Lib\\site-packages\\PyQt5\\Qt\\bin\\'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)


exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=True )
