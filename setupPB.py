#!/usr/bin/python

from distutils.core import setup
import py2exe
import sys, os, site, shutil

site_dir = site.getsitepackages()[1]
include_dll_path = os.path.join(site_dir, "gnome")

gtk_dirs_to_include = ['etc', 'lib\\gtk-3.0', 'lib\\girepository-1.0',
'lib\\gio', 'lib\\gdk-pixbuf-2.0', 'share\\glib-2.0', 'share\\fonts',
'share\\icons', 'share\\themes\\Default', 'share\\themes\\HighContrast']

include_gi_path = os.path.join(site_dir, "gi")

gtk_dlls = []
tmp_dlls = []
cdir = os.getcwd()
for dll in os.listdir(include_dll_path):
    if dll.lower().endswith('.dll'):
        gtk_dlls.append(os.path.join(include_dll_path, dll))
        tmp_dlls.append(os.path.join(cdir, dll))

for dll in gtk_dlls:
    shutil.copy(dll, cdir)

#shutil.copy("_gi.pyd", cdir)

winoptions = {
        'script': 'pdfshuffler_g3.py',
        'icon_resources': [(1, "pdfshuffler40.ico")]
    }


winoptions2 = {
        'script': 'pdfbooklet240.py',
        'icon_resources': [(1, "pdfbooklet.ico")]
    }

setup(name="PdfBooklet",
    version="2.4.0",
    description="Create booklets from PDF files",
    author="Averell7, Gaston",
##    url="http://www.mousepawgames.com/",
##    author_email="info@mousepawgames.com",
##    maintainer="MousePaw Labs",
##    maintainer_email="info@mousepawgames.com",
##    data_files=[("", ["redstring.png", "redstring_interface.glade", "redstring.ico"])],
    #py_modules=["redstring"],
    windows=[winoptions, winoptions2, winoptions],   # for an unknown reason, the first target does not get an icon. This is a dirty workaround    
    options={"py2exe": {
        "unbuffered": True,
        "compressed": True,
        "bundle_files": 3,
        'packages': ['gi'],
        'includes': ['gi'],
        }},
    zipfile=None,
    )

dest_dir = os.path.join(cdir, 'dist')
for dll in tmp_dlls:
    shutil.copy(dll, dest_dir)
    os.remove(dll)

try :
    for d in gtk_dirs_to_include:
        shutil.copytree(os.path.join(site_dir, "gnome", d),
            os.path.join(dest_dir, d))
except :
    pass
    
# Delete useless dll

to_delete = ["API-MS-Win-Core-Debug-L1-1-0.dll",
            "API-MS-Win-Core-DelayLoad-L1-1-0.dll",
            "API-MS-Win-Core-ErrorHandling-L1-1-0.dll",
            "API-MS-Win-Core-File-L1-1-0.dll",
            "API-MS-Win-Core-Handle-L1-1-0.dll",
            "API-MS-Win-Core-Heap-L1-1-0.dll",
            "API-MS-Win-Core-Interlocked-L1-1-0.dll",
            "API-MS-Win-Core-IO-L1-1-0.dll",
            "API-MS-Win-Core-LibraryLoader-L1-1-0.dll",
            "API-MS-Win-Core-Localization-L1-1-0.dll",
            "API-MS-Win-Core-LocalRegistry-L1-1-0.dll",
            "API-MS-Win-Core-Misc-L1-1-0.dll",
            "API-MS-Win-Core-ProcessEnvironment-L1-1-0.dll",
            "API-MS-Win-Core-ProcessThreads-L1-1-0.dll",
            "API-MS-Win-Core-Profile-L1-1-0.dll",
            "API-MS-Win-Core-String-L1-1-0.dll",
            "API-MS-Win-Core-Synch-L1-1-0.dll",
            "API-MS-Win-Core-SysInfo-L1-1-0.dll",
            "API-MS-Win-Core-ThreadPool-L1-1-0.dll",
            "API-MS-Win-Security-Base-L1-1-0.dll",
            "DNSAPI.DLL",
            "IPHLPAPI.DLL",
            "MPR.dll",
            "MSIMG32.DLL",
            "NSI.dll",
            "WINNSI.DLL" ]


for dll in to_delete :
    try :
        os.remove(os.path.join(cdir, "dist", dll))
    except :
        print "error for : ", os.path.join(cdir, "dist", dll)
        
