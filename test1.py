#!/usr/bin/python


try :
    from gi.repository import Gtk
except :
    print ("Gtk not accepted")    
    try :
        from gi.repository import GTK
    except :
        print ("GTK not accepted")

        try :
            from gi.repository import gtk
        except :
            print ("gtk not accepted")
            
            try :
                from gi.repository import Gtk3
            except :
                print ("Gtk3 not accepted")

                try :
                    from gi.repository import GTK3
                except :
                    print ("GTK3 not accepted")
    
                    try :
                        from gi.repository import GTK3
                    except :
                        print ("GTK3 not accepted")

from gi.repository import Poppler
