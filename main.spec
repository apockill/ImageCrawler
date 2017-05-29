# -*- mode: python -*-

block_cipher = None
icon_dir = "Icons\\"
icon_list = ["start_scan.png",
             "settings.png"]

data = []
for icon in icon_list:
    data.append((os.path.join(icon_dir, icon), os.path.join(icon_dir, icon), 'DATA'))

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
