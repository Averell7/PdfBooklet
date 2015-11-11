#!/usr/bin/python
import os, glob


f1 = open("log.txt", "w")
try :
    import gi
except :    
    f1.write("echec gi")
    
try :
    from gi import repository
except :    
    f1.write("\nechec repository")
    

gifile = "/home/travis/virtualenv/python2.7.9/lib/python2.7/site-packages/"
if os.path.isdir(gifile) :
    f1.write("\nsite packages exists")
    temp = glob.glob(gifile +  "*.*")
    for data in temp :
        f1.write(repr(data) + "\n")
        
else :
    f1.write("echec1 \n")
        
gifile2 = "/home/travis/virtualenv/python2.7.9/lib/python2.7/site-packages/gi/"
if os.path.isdir(gifile) :
    f1.write("\ngi exists")
    temp = glob.glob(gifile +  "*.*")
    for data in temp :
        f1.write(repr(data) + "\n")

else :
    f1.write("echec2 \n")




f1.close()




#from gi.repository import Gtk
from gi.repository import Poppler
