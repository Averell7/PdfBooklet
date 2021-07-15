#!/usr/bin/python3

#
# PdfBooklet 3.1.1 - GTK+ based utility to create booklets and other layouts
# from PDF documents.
# Copyright (C) 2008-2012 GAF Software
# <https://sourceforge.net/projects/pdfbooklet>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# =====>  Version number must be changed in setup.py (in the comment, line 4, and in the code) and build.py (in the code)

import os
import io
import re
import glob
import ftplib
from ftplib import FTP
# import pysftp
import zipfile
import tarfile

def fix_bin_file(file1):
    data1 = b"#!/usr/bin/python3\n"
    data1b = file1.readline()
    data2 = file1.read()
    data3 = data1 + data2
    x = len(data3)
    out = io.BytesIO()
    out.write(data3)
    return (out, x)

pyinstaller_file = ""

version = "3.1.2"
print ("\n\n ================ start bdist =============================\n\n")
# creates pdfbooklet-3.x.x.linux-[system].tar.gz
os.system('python3 setup.py bdist > /dev/null')
print ("\n\n ================ end bdist - start sdist =================\n\n")
# creates pdfbooklet-3.x.x.tar.gz
os.system('python3 setup.py sdist > /dev/null')
print ("\n\n ================ end sdist - start bdist_rpm =============\n\n")
os.system('python3 setup.py bdist_rpm > /dev/null')
# dependencies are set in the setup.cfg file
print ("\n\n ================ end bdist_rpm ===========================\n\n")

"""
print ("\n\n ================ Generate pyinstaller file =======================\n\n" )


os.chdir('./pdfbooklet')
os.system('sudo pyinstaller pdfbooklet.py -y > /dev/null')

pyinstaller_file = "pyinstaller-" + version + ".zip"
zipfile1 = zipfile.ZipFile("../dist/" + pyinstaller_file, "w")
os.system('ls -l /home/')
for mydir in os.walk("./dist/") :
    for myfile in mydir[2] :
        path = os.path.join(mydir[0], myfile)
        if os.path.isfile(path) :
            zipfile1.write(path)
zipfile1.close()

os.chdir("..")
"""

#os.system("tree -d")               # option -d will print directories only
os.chdir("dist")

rpm_file =   "pdfbooklet-" + version + "-1.noarch.rpm"
tar_file =   "pdfbooklet-" + version + ".tar.gz"
tar64_file = "./pdfbooklet-" + version + ".linux-x86_64.tar.gz"
corr_tar64_file = "./pdfbooklet-" + version + "-all_64_corr.tar.gz"
deb_file = "./pdfbooklet_" + version + "-2_all.deb"

input1 = tarfile.open(tar64_file, "r")
output = tarfile.open(corr_tar64_file, "w")
names = input1.getnames()
for name in names:    
    x = re.search(r"\./usr/lib/python.*?packages", name)
    if x:
        original_package = x.group(0)
        break

for name in names:
    member = input1.getmember(name)
    member.name = member.name.replace(original_package,"./usr/lib/python3/dist-packages")
    file1 = input1.extractfile(member)
    if name == "./usr/bin/pdfbooklet" :
        (file2, size) = fix_bin_file(file1)
        file2.seek(0)
        member.size = size
        output.addfile(member, file2)
        continue
    if file1:
        output.addfile(member, file1)

input1.close()
output.close()

"""
# generate Debian package
print ("\n\n ================ Creating debian package =======================\n\n")

#os.system('alien --generate --scripts ' + rpm_file) 
os.system('alien --generate ' + corr_tar64_file) 
new_dir = "./pdfbooklet-" + version + "/"

os.chdir(new_dir)


control_file = "./debian/control"
if os.path.isfile(control_file) :
    print ("control found")
    f1 = open(control_file, "r")

    data1 = f1.read()
    data1 = data1.replace("${shlibs:Depends}", "python (>= 2.7), python-gi, python-gi-cairo, python3-gi, python3-gi-cairo, python3-cairo, gir1.2-gtk-3.0, gir1.2-poppler-0.18")
    # above dependencies are for Debian. Unsure if python3-cairo is necessary. 
    # for rpm, something like that will be necessary, but unsufficient : python-gobject, python-gobject-2, pypoppler|python-poppler\n")

    f1.close()
    f1 = open(control_file, "w")
    f1.write(data1)
    f1.close()
else :
    print ("============> ERROR : control NOT found.")

# post installation commands
# correct pdfbooklet.cfg

pb_dir = "./usr/share/pdfbooklet/"
text = "chmod 777 " + pb_dir
# I am unsure of the right place of this file, so let us put it in both places
os.system(" echo " + text + "> ./postinst")
os.system(" echo " + text + "> ./debian/postinst")

# Build debian package
os.system("dpkg-buildpackage")
os.chdir("..")
"""

if os.path.isfile(rpm_file) :
  print ("found rpm", rpm_file)
else :
    print ("NOT found rpm", rpm_file)

if os.path.isfile(tar_file) :
  print ("found tar", tar_file)
else :
    print ("NOT found tar", tar_file)

if os.path.isfile(tar64_file) :
  print ("found tar", tar64_file)
else :
    print ("NOT found tar", tar64_file)

if os.path.isfile(deb_file) :
  print ("found deb", deb_file)
else :
    print ("NOT found deb", deb_file)

if os.path.isfile(pyinstaller_file) :
  print ("found pyinstaller", pyinstaller_file)
else :
    print ("NOT found pyinstaller", pyinstaller_file)

os.system('ls')



# install package
"""
print ("\n\n ================ Installing debian package =============================\n\n")
os.system("sudo dpkg -i " + deb_file)
os.system("sudo apt-get -f -y install")
"""

print ("\n\n ================ build terminated =============================\n\n")




print("\n\n ================ End of build.py =======================\n\n")

