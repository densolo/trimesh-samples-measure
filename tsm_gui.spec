# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['tsm_gui.py'],
             #pathex=['C:\\Works\\trimesh-samples-measure'],
             pathex=['/Users/denis/work/matlab/trimesh-samples-measure'],
             binaries=[],
             datas=[
                 #('venv\\Lib\\site-packages\\trimesh\\resources', 'trimesh\\resources'),
                 #('sample_measure_lib\\resources', 'sample_measure_lib\\resources'),
                 ('venv/lib/python3.7/site-packages/trimesh/resources', 'trimesh/resources'),
                 ('sample_measure_lib/resources', 'sample_measure_lib/resources'),
                 ('venv/lib/python3.7/site-packages/pygubu', 'pygubu'),
             ],
             hiddenimports=[],
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='tsm_gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
