#!/usr/bin/python



f1 = open("log.txt", "w")
try :
    import gi
except :    
    f1.write("echec gi")
    
try :
    from gi import repository
except :    
    f1.write("echec repository")
    
f1.close()


#from gi.repository import Gtk
from gi.repository import Poppler
