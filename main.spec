# -*- mode: python -*-
import os

block_cipher = None
icon_dir = "Resources/Icons"

icon_list = os.listdir(icon_dir)
# ["start_scan.png",
#  "settings.png",
#  "add_template.png"]

data = []
for icon in icon_list:
    data.append((os.path.join(icon_dir, icon), os.path.join(icon_dir, icon), 'DATA'))

data.append(("Resources/phantomjs.exe", "Resources/phantomjs.exe", 'DATA'))

a = Analysis(['main.py'],
             pathex=['C:\\Users\\Alex Thiel\\Google Drive\\Projects\\Project - 2017 - NVIDIA Marketing Tool\\ImageCrawler'],
             binaries=None,
             datas=None,
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
          a.datas + data,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=True )
