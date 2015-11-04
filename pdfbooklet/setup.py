
from distutils.core import setup
import py2exe, glob

options = {
    #"bundle_files": 1,
    #"ascii": 1, # to make a smaller executable, don't include the encodings
    "compressed": 1, # compress the library archive
    'includes': 'cairo, pango, pangocairo, atk, gobject',
    
}
    
winoptions1 = {
        'script': 'pdfBooklet.py',
        'icon_resources': [(1, "pdfbooklet.ico")]
}

winoptions2 = {
        'script': 'pdfshuffler_g.py',
        'icon_resources': [(1, "pdfshuffler.ico")]
    }

additional_files = [('.', glob.glob('*.gif'))]

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "2.3.2",
    description = "py2exe sample script",
    name = "py2exe samples",
    options = {"py2exe": options},
    zipfile = None, # append zip-archive to the executable.
    
    # targets to build
    windows = [winoptions1, winoptions2],
    data_files = additional_files
    )
