#!/usr/bin/python3

#
# PdfBooklet 3.0.6 - GTK+ based utility to create booklets and other layouts 
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
#

import os
import re
import glob
from ftplib import FTP
import zipfile


version = "3.0.6"
print "\n\n ================ start bdist =============================\n\n"
os.system('sudo python3 setup.py bdist')
print "\n\n ================ end bdist - start sdist =================\n\n"
os.system('sudo python3 setup.py sdist')
print "\n\n ================ end sdist - start bdist_rpm =============\n\n"
os.system('sudo python3 setup.py bdist_rpm')
print "\n\n ================ end bdist_rpm ===========================\n\n"
rpm_file = "./dist/pdfbooklet-" + version + "-1.noarch.rpm"
tar_file = "./dist/pdfbooklet-" + version + ".tar.gz"
tar64_file = "./dist/pdfbooklet-" + version + ".linux-x86_64.tar.gz"

if os.path.isfile(rpm_file) :
  print "found rpm", rpm_file
else :
    print "NOT found rpm", rpm_file
    os.system('ls')
  
if os.path.isfile(tar_file) :
  print "found tar", tar_file
else :
    print "NOT found tar", tar_file
    os.system('ls')
    
if os.path.isfile(tar64_file) :
  print "found tar", tar64_file
else :
    print "NOT found tar", tar64_file
    os.system('ls')
  


print "\n\n ================ Uploading tar.gz =======================\n\n"

ftp = FTP('perso-ftp.orange.fr')     # connect to host, default port
x = ftp.login('dysmas1956@wanadoo.fr', '4ua7x9x')                     # user anonymous, passwd anonymous@
print "Connect to Ftp : " + x
ftp.cwd('pdfbooklet')               # change into "debian" directory
#ftp.retrlines('LIST')           # list directory contents
#ftp.retrbinary('RETR Archeotes.sqlite', open('Archeotes.sqlite', 'wb').write)
try :
    command = 'STOR ' + tar_file[7:]
    x = ftp.storbinary(command, open(tar_file, 'rb'))    
except :    
    print "tar file error :", command

try :
    command = 'STOR ' + tar64_file[7:] 
    x = ftp.storbinary(command, open(tar64_file, 'rb'))
except :
    print "tar64 file error :", command
    
try :
    command = 'STOR ' + rpm_file[7:]
    x = ftp.storbinary(command, open(rpm_file, 'rb'))
except :
    print "rpm file error :", command


# generate pyinstaller file
print "\n\n ================ Generate pyinstaller file =======================\n\n"

os.chdir('./pdfbooklet')
os.system('sudo pyinstaller pdfbooklet.py')

print "\n\n ================ Uploading pyintaller files =======================\n\n"

pyinstaller_file = "/home/pyinstaller-" + version + ".zip"
zipfile1 = zipfile.ZipFile(pyinstaller_file, "w")
os.system('ls -l /home/')
for mydir in os.walk("./dist/") :
    for myfile in mydir[2] :
        path = os.path.join(mydir[0], myfile)
        if os.path.isfile(path) :
            zipfile1.write(path)
zipfile1.close()  
os.system('ls -l /home/')
            
command = 'STOR pyinstaller.zip'
x = ftp.storbinary(command, open(pyinstaller_file, 'rb'))


# generate Debian package
print "\n\n ================ Creating debian package =======================\n\n"

os.chdir('..')

new_dir = "./pdfbooklet-" + version + "/"
os.system('sudo alien --generate --scripts ' + rpm_file)
control_file = new_dir + "debian/control"
if os.path.isfile(control_file) :
  print "control found"
else :
    print "control NOT found. See log.txt"
    # walkdirectory
    f1 = open("./log.txt", "w")
    for data in os.walk("./") :
        f1.write(repr(data))
    f1.close()
    
    command = 'STOR ' + "./log.txt"
    x = ftp.storbinary(command, open("./log.txt", 'rb'))

f1 = open(control_file, "r")

data1 = f1.read()
data1 = data1.replace("${shlibs:Depends}", "python (>= 2.7), python3-cairo, python-gobject-cairo, python-gi-cairo, python3-gi, gir1.2-gtk-3.0, gir1.2-poppler-0.18")
#data1 = python-gobject, python-gobject-2, pypoppler|python-poppler\n")


f1.close()
f1 = open(control_file, "w")
f1.write(data1)
f1.close()


# correct pdfbooklet.cfg

dir1 = new_dir + "/usr/share/pdfbooklet/"

os.system("ls " + dir1  )
print "~~~~~~~~1"
os.system("sudo chmod 777 " + dir1  )
print "~~~~~~~~2"
os.system("ls -l " + new_dir +  "/usr/share/" )
print "~~~~~~~~3"




# Build debian package
os.system("cd " + new_dir + "; sudo dpkg-buildpackage")

deb_file = "./pdfbooklet_" + version + "-2_all.deb"
print "=========> deb file is : ", deb_file



# install package
print "\n\n ================ Installing debian package =============================\n\n"
os.system("sudo dpkg -i " + deb_file)
os.system("sudo apt-get -f -y install")

print "\n\n ================ build.py terminated =============================\n\n"





x = ftp.storbinary('STOR ' + deb_file[2:], open(deb_file, 'rb'))
print x


ftp.quit()



#os.system('rpmrebuild -b -R --change-spec-requires rebuild.py -p ' + new_file )



