from ftplib import FTP

ftp = FTP('privftp.pro.proxad.net')     # connect to host, default port
x = ftp.login('webmaster@chartreux.org', 'esoJnaS')                     # user anonymous, passwd anonymous@
print x
ftp.cwd('transit')               # change into "debian" directory
#ftp.retrlines('LIST')           # list directory contents
#ftp.retrbinary('RETR Archeotes.sqlite', open('Archeotes.sqlite', 'wb').write)
x = ftp.storbinary('STOR log.txt' , open("log.txt", 'rb'))

ftp.quit()

print "====>", x