#!/usr/bin/python

from ftplib import FTP

ftp = FTP('perso-ftp.orange.fr')     # connect to host, default port
x = ftp.login('dysmas1956@wanadoo.fr', '4ua7x9x')                     # user anonymous, passwd anonymous@
print x
ftp.cwd('pdfbooklet')               # change into "debian" directory
#ftp.retrlines('LIST')           # list directory contents
#ftp.retrbinary('RETR Archeotes.sqlite', open('Archeotes.sqlite', 'wb').write)
x = ftp.storbinary('STOR log.txt' , open("log.txt", 'rb'))

ftp.quit()

print "====>", x