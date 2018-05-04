# -*- mode: python -*-

block_cipher = None


a = Analysis(['mycode.py'],
             pathex=['F:\\code\\\xb1\xe0\xd2\xeb\xd4\xad\xc0\xed'],
             binaries=[],
             datas=[],
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
          name='mycode',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
