# -*- mode: python3 -*-

import os
import site

gnome_path = os.path.join(site.getsitepackages()[1], 'gnome')
typelib_path = os.path.join(gnome_path, 'lib', 'girepository-1.0')
missing_files = []

for tl in ["GdkPixbuf-2.0.typelib", "GModule-2.0.typelib", "Poppler-0.18.typelib"] :
    missing_files.append((os.path.join(typelib_path, tl), "./gi_typelibs"))


for dll in ["libpoppler-glib-8.dll", "libstdc++.dll", "libopenjp2.dll", "liblcms2-2.dll"] :
    missing_files.append((os.path.join(gnome_path, dll), "./"))



datafiles = [("./test.pdf", "./"), ("./data", "data")]

excluded = [("./share/*.*"), ("./share/etc/*.*")]

block_cipher = None


a = Analysis(['pdfbooklet307.py'],
             pathex=['d:\\Mes documents\\en cours\\PdfBooklet3'],
             binaries=missing_files,            
             datas=datafiles,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

"""
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='pdfbooklet',
          debug=False,
          strip=False,
          upx=True,
          console=False )
"""
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='pdfbooklet',
          debug=False,
          strip=False,
          upx=True,
          console=True,
          icon='pdfbooklet.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='pdfbooklet')
