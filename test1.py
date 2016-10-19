#!/usr/bin/python3.5
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
    
for a in os.walk("/home/travis/virtualenv/python3.5/lib/python3.5/site-packages/") :
    f1.write(repr(a) + "\n")
    





f1.close()




#from gi.repository import Gtk
from gi.repository import Poppler
