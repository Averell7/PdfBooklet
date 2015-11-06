#!/usr/bin/python


try :
    from gi.repository import Gtk
except :
    print ("Gtk not accepted")    
    try :
        from gi.repository import GTK
    except :
        print ("GTK not accepted")
        from gi.repository import gtk
            

                    

from gi.repository import Poppler
