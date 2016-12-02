#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

# PdfShuffler 0.6.0 Rev 82, modified for Windows compatibility
# See the Class PdfShuffler_Windows_cod" / class PdfShuffler_Linux_code :

# updated for python 3 and Gtk 3

# Version inside pdfBooklet : 3.0.1


"""

 PdfShuffler 0.6.0 - GTK+ based utility for splitting, rearrangement and
 modification of PDF documents.
 Copyright (C) 2008-2012 Konstantinos Poulios
 <https://sourceforge.net/projects/pdfshuffler>

 This file is part of PdfShuffler.

 PdfShuffler is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""

import os
import shutil       # for file operations like whole directory deletion
import sys          # for proccessing of command line args
import stat
import urllib       # for parsing filename information passed by DnD
import threading
import tempfile
import glob
from copy import copy
import locale       #for multilanguage support
import gettext
import elib_intl3
# elib_intl does not work if the strings are unicode
domain = "pdfshuffler"     # these lines have no effect in python 3
locale = "share/locale"

elib_intl3.install(domain, locale)

APPNAME = 'PdfShuffler' # PDF-Shuffler, PDFShuffler, pdfshuffler
VERSION = '0.6.0'
WEBSITE = 'http://pdfshuffler.sourceforge.net/'
LICENSE = 'GNU General Public License (GPL) Version 3.'

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Poppler', '0.18')
from gi.repository import Gtk, Gdk, Poppler
from gi.repository import Pango        # for adjusting the text alignment in CellRendererText
from gi.repository import Gio          # for inquiring mime types information
from gi.repository import GObject      # for using custom signals
##from gi.repository import cairo        # Raises the error : 'gi.repository.cairo' object has no attribute 'ImageSurface'
import cairo

from PyPDF2_G.pdf import PdfFileWriter, PdfFileReader

from pdfshuffler_iconview3 import CellRendererImage
GObject.type_register(CellRendererImage)


import time

Gtk.rc_parse("./gtkrc")

class PdfShuffler:
    prefs = {
        'window width': min(700, Gdk.Screen.get_default().get_width() / 2),
        'window height': min(600, Gdk.Screen.get_default().get_height() - 50),

        'window x': 0,
        'window y': 0,
        'initial thumbnail size': 300,
        'initial zoom level': -14,
    }

    MODEL_ROW_INTERN = 1001
    MODEL_ROW_EXTERN = 1002
    TEXT_URI_LIST = 1003
    MODEL_ROW_MOTION = 1004
    TARGETS_IV = [Gtk.TargetEntry.new('MODEL_ROW_INTERN', Gtk.TargetFlags.SAME_WIDGET, MODEL_ROW_INTERN),
                  Gtk.TargetEntry.new('MODEL_ROW_EXTERN', Gtk.TargetFlags.OTHER_APP, MODEL_ROW_EXTERN),
                  Gtk.TargetEntry.new('MODEL_ROW_MOTION', 0, MODEL_ROW_MOTION)]
    TARGETS_SW = [Gtk.TargetEntry.new('text/uri-list', 0, TEXT_URI_LIST),
                  Gtk.TargetEntry.new('MODEL_ROW_EXTERN', Gtk.TargetFlags.OTHER_APP, MODEL_ROW_EXTERN)]



    def __init__(self):

        if os.name == "nt" :
            self.winux = PdfShuffler_Windows_code()
        else :
            self.winux = PdfShuffler_Linux_code()


        # Create the temporary directory
        self.tmp_dir = tempfile.mkdtemp("pdfshuffler")
        self.selection_start = 0
        os.chmod(self.tmp_dir, stat.S_IRWXO)        # TODO il y avait 0700. RWXO est plutôt 777 ?
        icon_theme = Gtk.IconTheme.get_default()
        try:
            Gtk.window_set_default_icon(icon_theme.load_icon("pdfshuffler", 64, 0))
        except:
            print(_("Can't load icon. Application is not installed correctly."))

        # Import the user interface file, trying different possible locations
        ui_path = '/usr/share/pdfbooklet/data/pdfshuffler_g.glade'
        if not os.path.exists(ui_path):
            ui_path = '/usr/local/share/pdfbooklet/data/pdfshuffler_g.glade'

        # Windows standard path
        if not os.path.exists(ui_path):
            if getattr( sys, 'frozen', False ) :    # running in a bundle (pyinstaller)
                ui_path = os.path.join(sys._MEIPASS, "data/pdfshuffler_g.glade")
            else :                                  # running live
                ui_path = './data/pdfshuffler_g.glade'
                print (ui_path), "  debug"

        if not os.path.exists(ui_path):
            parent_dir = os.path.dirname( \
                         os.path.dirname(os.path.realpath(__file__)))
            ui_path = os.path.join(parent_dir, 'data', 'pdfshuffler_g.glade')

        if not os.path.exists(ui_path):
            head, tail = os.path.split(parent_dir)
            while tail != 'lib' and tail != '':
                head, tail = os.path.split(head)
            if tail == 'lib':
                ui_path = os.path.join(head, 'share', 'pdfbooklet', \
                                       'data/pdfshuffler_g.glade')

        self.uiXML = Gtk.Builder()
        self.uiXML.add_from_file(ui_path)
        self.uiXML.connect_signals(self)

        # Create the main window, and attach delete_event signal to terminating
        # the application
        self.window = self.uiXML.get_object('main_window')
        self.window.set_title(APPNAME)
        self.window.set_border_width(0)
        self.window.move(self.prefs['window x'], self.prefs['window y'])
        self.window.set_default_size(self.prefs['window width'],
                                     self.prefs['window height'])
        self.window.connect('delete_event', self.close_application)

        # Create a scrolled window to hold the thumbnails-container
        self.sw = self.uiXML.get_object('scrolledwindow')
        self.sw.drag_dest_set(Gtk.DestDefaults.MOTION |
                              Gtk.DestDefaults.HIGHLIGHT |
                              Gtk.DestDefaults.DROP |
                              Gtk.DestDefaults.MOTION,
                              self.TARGETS_SW,
                              Gdk.DragAction.COPY |
                              Gdk.DragAction.MOVE)
        self.sw.connect('drag_data_received', self.sw_dnd_received_data)
        self.sw.connect('button_press_event', self.sw_button_press_event)
        self.sw.connect('scroll_event', self.sw_scroll_event)

        # Create an alignment to keep the thumbnails center-aligned
        align = Gtk.Alignment.new(0.5, 0.5, 0, 0)       # python 3
        self.sw.add_with_viewport(align)

        # Create ListStore model and IconView
        self.model = Gtk.ListStore(str,         # 0.Text descriptor
                                   GObject.TYPE_PYOBJECT,
                                                # 1.Cached page image
                                   int,         # 2.Document number
                                   int,         # 3.Page number
                                   float,       # 4.Scale
                                   str,         # 5.Document filename
                                   int,         # 6.Rotation angle
                                   float,       # 7.Crop left
                                   float,       # 8.Crop right
                                   float,       # 9.Crop top
                                   float,       # 10.Crop bottom
                                   int,         # 11.Page width
                                   int,         # 12.Page height
                                   float)       # 13.Resampling factor

        self.zoom_set(self.prefs['initial zoom level'])
        self.iv_col_width = self.prefs['initial thumbnail size']

        self.iconview = Gtk.IconView(self.model)
        self.iconview.set_item_width(self.iv_col_width + 12)

        self.cellthmb = CellRendererImage()
##        self.cellthmb = IDRenderer()
        self.iconview.pack_start(self.cellthmb, False)
        self.iconview.add_attribute(self.cellthmb, "image", 1)
        self.iconview.add_attribute(self.cellthmb, "scale", 4)
        self.iconview.add_attribute(self.cellthmb, "rotation", 6)
        self.iconview.add_attribute(self.cellthmb, "cropL", 7)
        self.iconview.add_attribute(self.cellthmb, "cropR", 8)
        self.iconview.add_attribute(self.cellthmb, "cropT", 9)
        self.iconview.add_attribute(self.cellthmb, "cropB", 10)
        self.iconview.add_attribute(self.cellthmb, "width", 11)
        self.iconview.add_attribute(self.cellthmb, "height", 12)
        self.iconview.add_attribute(self.cellthmb, "resample", 13)

        self.celltxt = Gtk.CellRendererText()
        self.celltxt.set_property('width', self.iv_col_width)
        self.celltxt.set_property('wrap-width', self.iv_col_width)
        self.celltxt.set_property('alignment', Pango.Alignment.CENTER)
        self.iconview.pack_start(self.celltxt, False)
        self.iconview.set_properties(self.celltxt, text_column=0)

        self.iconview.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.iconview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                                               self.TARGETS_IV,
                                               Gdk.DragAction.COPY |
                                               Gdk.DragAction.MOVE)
        self.iconview.enable_model_drag_dest(self.TARGETS_IV,
                                             Gdk.DragAction.DEFAULT)
        self.iconview.connect('drag_begin', self.iv_drag_begin)
        self.iconview.connect('drag_data_get', self.iv_dnd_get_data)
        self.iconview.connect('drag_data_received', self.iv_dnd_received_data)
        self.iconview.connect('drag_data_delete', self.iv_dnd_data_delete)
        self.iconview.connect('drag_motion', self.iv_dnd_motion)
        self.iconview.connect('drag_leave', self.iv_dnd_leave_end)
        self.iconview.connect('drag_end', self.iv_dnd_leave_end)
        self.iconview.connect('button_press_event', self.iv_button_press_event)

        align.add(self.iconview)

        # Progress bar
        self.progress_bar = self.uiXML.get_object('progressbar')
        self.progress_bar_timeout_id = 0

        # Define window callback function and show window
        self.window.connect('size_allocate', self.on_window_size_request)        # resize
        self.window.connect('key_press_event', self.on_keypress_event ) # keypress
        self.window.show_all()
        self.progress_bar.hide()

        # Change iconview color background
##        style = self.sw.get_style().copy()
##        for state in (Gtk.StateType.NORMAL, Gtk.StateType.PRELIGHT, Gtk.StateType.ACTIVE):
##            style.base[state] = style.bg[Gtk.StateType.NORMAL]
##        self.iconview.set_style(style)

        # Creating the popup menu
##        self.popup = Gtk.Menu()
##        popup_rotate_right = Gtk.ImageMenuItem(_('_Rotate Right'))
##        popup_rotate_left = Gtk.ImageMenuItem(_('Rotate _Left'))
##        popup_crop = Gtk.MenuItem(_('C_rop...'))
##        popup_delete = Gtk.ImageMenuItem(Gtk.STOCK_DELETE)
##        popup_rotate_right.connect('activate', self.rotate_page_right)
##        popup_rotate_left.connect('activate', self.rotate_page_left)
##        popup_crop.connect('activate', self.crop_page_dialog)
##        popup_delete.connect('activate', self.clear_selected)
##        popup_rotate_right.show()
##        popup_rotate_left.show()
##        popup_crop.show()
##        popup_delete.show()
##        self.popup.append(popup_rotate_right)
##        self.popup.append(popup_rotate_left)
##        self.popup.append(popup_crop)
##        self.popup.append(popup_delete)

        self.popup = self.uiXML.get_object('contextmenu1')

        # Initializing variables
        self.export_directory = self.winux.home_dir()

        self.import_directory = self.export_directory
        self.nfile = 0
        self.iv_auto_scroll_direction = 0
        self.iv_auto_scroll_timer = None
        self.pdfqueue = []

        GObject.type_register(PDF_Renderer)
        GObject.signal_new('update_thumbnail', PDF_Renderer,
                           GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
                           [GObject.TYPE_INT, GObject.TYPE_PYOBJECT,
                            GObject.TYPE_FLOAT])
        self.rendering_thread = 0

        self.set_unsaved(False)

        # Importing documents passed as command line arguments
        for filename in sys.argv[1:]:
            self.add_pdf_pages(filename)




    def render(self):
        if self.rendering_thread:
            self.rendering_thread.quit = True
            self.rendering_thread.join()
        #FIXME: the resample=2. factor has to be dynamic when lazy rendering
        #       is implemented
        self.rendering_thread = PDF_Renderer(self.model, self.pdfqueue, 2)
        self.rendering_thread.connect('update_thumbnail', self.update_thumbnail)
        self.rendering_thread.start()

        if self.progress_bar_timeout_id:
            GObject.source_remove(self.progress_bar_timeout_id)
        self.progress_bar_timout_id = \
            GObject.timeout_add(50, self.progress_bar_timeout)

    def set_unsaved(self, flag):
        self.is_unsaved = flag
        GObject.idle_add(self.retitle)

    def retitle(self):
        title = ''
        if len(self.pdfqueue) == 1:
            title += self.pdfqueue[0].filename
        elif len(self.pdfqueue) == 0:
            title += _("No document")
        else:
            title += _("Several documents")
        if self.is_unsaved:
            title += '*'
        title += ' - ' + APPNAME
        self.window.set_title(title)

    def progress_bar_timeout(self):
        cnt_finished = 0
        cnt_all = 0
        for row in self.model:
            cnt_all += 1
            if row[1]:
                cnt_finished += 1
        fraction = float(cnt_finished)/float(cnt_all)

        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(_('Rendering thumbnails... [%(i1)s/%(i2)s]')
                                   % {'i1' : cnt_finished, 'i2' : cnt_all})
        if fraction >= 0.999:
            self.progress_bar.hide()
            return False
##        elif not self.progress_bar.flags() & Gtk.VISIBLE:  python 3 : flags unknown
        else :
            self.progress_bar.show_all()



        return True

    def update_thumbnail(self, object, num, thumbnail, resample):
        row = self.model[num]
        Gdk.threads_enter()
        row[13] = resample
        row[4] = self.zoom_scale
        row[1] = thumbnail
        Gdk.threads_leave()

    def on_window_size_request(self, window, event):
        """Main Window resize - workaround for autosetting of
           iconview cols no."""

        #add 12 because of: http://bugzilla.gnome.org/show_bug.cgi?id=570152
        col_num = 9 * window.get_size()[0] \
            / (10 * (self.iv_col_width + self.iconview.get_column_spacing() * 2))
        self.iconview.set_columns(col_num)

    def update_geometry(self, iter):
        """Recomputes the width and height of the rotated page and saves
           the result in the ListStore"""

        if not self.model.iter_is_valid(iter):
            return

        nfile, npage, rotation = self.model.get(iter, 2, 3, 6)
        crop = self.model.get(iter, 7, 8, 9, 10)
        page = self.pdfqueue[nfile-1].document.get_page(npage-1)
        w0, h0 = page.get_size()

        rotation = int(rotation) % 360
        rotation = ((rotation + 45) / 90) * 90
        if rotation == 90 or rotation == 270:
            w1, h1 = h0, w0
        else:
            w1, h1 = w0, h0

        self.model.set(iter, 11, w1, 12, h1)

    def reset_iv_width(self, renderer=None):
        """Reconfigures the width of the iconview columns"""

        if not self.model.get_iter_first(): #just checking if model is empty
            return

        max_w = 10 + int(max(row[4]*row[11]*(1.-row[7]-row[8]) \
                             for row in self.model))
        if max_w != self.iv_col_width:
            self.iv_col_width = max_w
            self.celltxt.set_property('width', self.iv_col_width)
            self.celltxt.set_property('wrap-width', self.iv_col_width)
            self.iconview.set_item_width(self.iv_col_width + 12) #-1)
            self.on_window_size_request(self.window, None)

    def on_keypress_event(self, widget, event):
        """Keypress events in Main Window"""

        #keyname = Gdk.keyval_name(event.keyval)
        if event.keyval == 65535:   # Delete keystroke
            self.clear_selected()

    def close_application(self, widget, event=None, data=None):
        """Termination"""

        if self.rendering_thread:
            self.rendering_thread.quit = True
            self.rendering_thread.join()

        if os.path.isdir(self.tmp_dir):
            self.winux.remove_temp_dir(self.tmp_dir)

        if Gtk.main_level():
            Gtk.main_quit()
        else:
            sys.exit(0)
        return False

    def add_pdf_pages(self, filename,
                            firstpage=None, lastpage=None,
                            angle=0, crop=[0.,0.,0.,0.]):
        """Add pages of a pdf document to the model"""

        res = False
        # Check if the document has already been loaded
        pdfdoc = None
        for it_pdfdoc in self.pdfqueue:
            if self.winux.check_same_file(filename, it_pdfdoc) == True :
                pdfdoc = it_pdfdoc
                break

        if not pdfdoc:
            pdfdoc = PDF_Doc(filename, self.nfile, self.tmp_dir)
            self.import_directory = os.path.split(filename)[0]
            self.export_directory = self.import_directory
            if pdfdoc.nfile != 0 and pdfdoc != []:
                self.nfile = pdfdoc.nfile
                self.pdfqueue.append(pdfdoc)
            else:
                return res

        n_start = 1
        n_end = pdfdoc.npage
        if firstpage:
           n_start = min(n_end, max(1, firstpage))
        if lastpage:
           n_end = max(n_start, min(n_end, lastpage))

        for npage in range(n_start, n_end + 1):
            descriptor = ''.join([pdfdoc.shortname, '\n', _('page'), ' ', str(npage)])
            page = pdfdoc.document.get_page(npage-1)
            w, h = page.get_size()
            iter = self.model.append((descriptor,         # 0
                                      None,               # 1
                                      pdfdoc.nfile,       # 2
                                      npage,              # 3
                                      self.zoom_scale,    # 4
                                      pdfdoc.filename,    # 5
                                      angle,              # 6
                                      crop[0],crop[1],    # 7-8
                                      crop[2],crop[3],    # 9-10
                                      w,h,                # 11-12
                                      2.              ))  # 13 FIXME
            self.update_geometry(iter)
            res = True

        self.reset_iv_width()
        GObject.idle_add(self.retitle)
        if res:
            GObject.idle_add(self.render)
        return res

    def choose_export_pdf_name(self, widget=None, only_selected=False):
        """Handles choosing a name for exporting """

        chooser = Gtk.FileChooserDialog(title=_('Export ...'),
                                        action=Gtk.FileChooserAction.SAVE,
                                        buttons=(Gtk.STOCK_CANCEL,
                                                 Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_SAVE,
                                                 Gtk.ResponseType.OK))
        chooser.set_do_overwrite_confirmation(True)
        chooser.set_current_folder(self.export_directory)
        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name(_('PDF files'))
        filter_pdf.add_mime_type('application/pdf')
        filter_pdf.add_pattern('*.pdf')
        chooser.add_filter(filter_pdf)

        filter_all = Gtk.FileFilter()
        filter_all.set_name(_('All files'))
        filter_all.add_pattern('*')
        chooser.add_filter(filter_all)

        while True:
            response = chooser.run()
            if response == Gtk.ResponseType.OK:
                file_out = chooser.get_filename()
                (path, shortname) = os.path.split(file_out)
                (shortname, ext) = os.path.splitext(shortname)
                if ext.lower() != '.pdf':
                    file_out = file_out + '.pdf'
                try:
                    self.export_to_file(file_out, only_selected)
                    self.export_directory = path
                    self.set_unsaved(False)
                except Exception as e:
                    chooser.destroy()
                    error_msg_dlg = Gtk.MessageDialog(None,
                                                      Gtk.DialogFlags.MODAL,
                                                      Gtk.MessageType.WARNING,
                                                      Gtk.ButtonsType.CLOSE,
                                                      str(e))
                    response = error_msg_dlg.run()
                    if response == Gtk.ResponseType.OK:
                        error_msg_dlg.destroy()
                    return
            break
        chooser.destroy()

    def export_to_file(self, file_out, only_selected=False):
        """Export to file"""

        selection = self.iconview.get_selected_items()
        pdf_output = PdfFileWriter()
        pdf_input = []
        for pdfdoc in self.pdfqueue:
            pdfdoc_inp = PdfFileReader(open(pdfdoc.copyname, 'rb'))
            if pdfdoc_inp.getIsEncrypted():
                try: # Workaround for lp:#355479
                    stat = pdfdoc_inp.decrypt('')
                except:
                    stat = 0
                if (stat!=1):
                    errmsg = _('File %s is encrypted.\n'
                               'Support for encrypted files has not been implemented yet.\n'
                               'File export failed.') % pdfdoc.filename
                    raise Exception(errmsg)
                #FIXME
                #else
                #   ask for password and decrypt file
            pdf_input.append(pdfdoc_inp)

        for row in self.model:

            if only_selected and row.path not in selection:
                continue

            # add pages from input to output document
            nfile = row[2]
            npage = row[3]
            if npage == -1 :
                pdf_output.addBlankPage()
                continue
            current_page = copy(pdf_input[nfile-1].getPage(npage-1))
            angle = row[6]
            angle0 = current_page.get("/Rotate",0)
            crop = [row[7],row[8],row[9],row[10]]
            if angle != 0:
                current_page.rotateClockwise(angle)
            if crop != [0.,0.,0.,0.]:
                rotate_times = (((angle + angle0) % 360 + 45) / 90) % 4
                crop_init = crop
                if rotate_times != 0:
                    perm = [0,2,1,3]
                    for it in range(rotate_times):
                        perm.append(perm.pop(0))
                    perm.insert(1,perm.pop(2))
                    crop = [crop_init[perm[side]] for side in range(4)]
                #(x1, y1) = current_page.cropBox.lowerLeft
                #(x2, y2) = current_page.cropBox.upperRight
                (x1, y1) = [float(xy) for xy in current_page.mediaBox.lowerLeft]
                (x2, y2) = [float(xy) for xy in current_page.mediaBox.upperRight]
                x1_new = int(x1 + (x2-x1) * crop[0])
                x2_new = int(x2 - (x2-x1) * crop[1])
                y1_new = int(y1 + (y2-y1) * crop[3])
                y2_new = int(y2 - (y2-y1) * crop[2])
                #current_page.cropBox.lowerLeft = (x1_new, y1_new)
                #current_page.cropBox.upperRight = (x2_new, y2_new)
                current_page.mediaBox.lowerLeft = (x1_new, y1_new)
                current_page.mediaBox.upperRight = (x2_new, y2_new)

            pdf_output.addPage(current_page)

        # finally, write "output" to document-output.pdf
        pdf_output.write(open(file_out, 'wb'))

    def on_action_add_doc_activate(self, widget, data=None):
        """Import doc"""

        chooser = Gtk.FileChooserDialog(title=_('Import...'),
                                        action=Gtk.FileChooserAction.OPEN,
                                        buttons=(Gtk.STOCK_CANCEL,
                                                  Gtk.ResponseType.CANCEL,
                                                  Gtk.STOCK_OPEN,
                                                  Gtk.ResponseType.OK))
        if self.import_directory :
            chooser.set_current_folder(self.import_directory)
        chooser.set_select_multiple(True)

        filter_all = Gtk.FileFilter()
        filter_all.set_name(_('All files'))
        filter_all.add_pattern('*')
        chooser.add_filter(filter_all)

        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name(_('PDF files'))
        filter_pdf.add_mime_type('application/pdf')
        filter_pdf.add_pattern('*.pdf')
        chooser.add_filter(filter_pdf)
        chooser.set_filter(filter_pdf)

        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            for filename in chooser.get_filenames():
                #filename = str(filename,"utf-8")     Unsupported in python 3       # convert utf-8 to unicode for internal use
                if os.path.isfile(filename):
                    # FIXME
##                    f = Gio.File(filename)           # ££ python 3
##                    f_info = f.query_info('standard::content-type')
##                    mime_type = f_info.get_content_type()
##                    expected_mime_type = pdf_mime_type
##
##                    if mime_type == expected_mime_type :
                        self.add_pdf_pages(filename)
##                    elif mime_type[:34] == 'application/vnd.oasis.opendocument':
##                        print((_('OpenDocument not supported yet!')))
##                    elif mime_type[:5] == 'image':
##                        print((_('Image file not supported yet!')))
##                    else:
##                        print((_('File type not supported!')))
                else:
                    print((_('File %s does not exist') % filename))
        elif response == Gtk.RESPONSE_CANCEL:
            print((_('Closed, no files selected')))
        chooser.destroy()
        GObject.idle_add(self.retitle)

    def clear_selected(self, button=None):
        """Removes the selected elements in the IconView"""

        model = self.iconview.get_model()
        selection = self.iconview.get_selected_items()
        if selection:
            selection.sort(reverse=True)
            self.set_unsaved(True)
            for path in selection:
                iter = model.get_iter(path)
                model.remove(iter)
            path = selection[-1]
            self.iconview.select_path(path)
            if not self.iconview.path_is_selected(path):
                if len(model) > 0:	# select the last row
                    row = model[-1]
                    path = row.path
                    self.iconview.select_path(path)
            self.iconview.grab_focus()

    def add_blank_page(self, menu=None, num_blank_pages=1):
        action = ""
        if menu != None :
            name = Gtk.Buildable.get_name(menu)
            num_blank_pages = int(name[-1])
            action = name[0:5]
        model = self.iconview.get_model()
        selection = self.iconview.get_selected_items()
        if selection:
            selection.sort(reverse=True)
            self.set_unsaved(True)
            path = selection[0]
            iter = model.get_iter(path)
            descriptor = 'Blank'
            w, h = self.model.get(iter, 11, 12)

            row =(descriptor,         # 0
                  None,               # 1
                  1,                  # 2
                  -1,                 # 3
                  self.zoom_scale,    # 4
                  "",                 # 5
                  0,                  # 6
                  0,0,                # 7-8
                  0,0,                # 9-10
                  w,h,                # 11-12
                  2.              )  # 13 FIXME
            for i in range(num_blank_pages) :
                if action == "befor" :
                    self.model.insert_before(iter, row)
                else :
                    self.model.insert_after(iter, row)


    def iv_drag_begin(self, iconview, context):
        """Sets custom icon on drag begin for multiple items selected"""

        global shuffler_selection_a
        #if len(iconview.get_selected_items()) > 1:
        if len(shuffler_selection_a) > 0 :
            iconview.stop_emission('drag_begin')
##            context.set_icon_stock(Gtk.STOCK_DND_MULTIPLE, 0, 0)
            for a in shuffler_selection_a :
                iconview.select_path(a)

    def iv_dnd_get_data(self, iconview, context,
                        selection_data, target_id, etime):
        """Handles requests for data by drag and drop in iconview"""

        global shuffler_selection_a
        model = iconview.get_model()
        if len(shuffler_selection_a) > 1 :
            selection = shuffler_selection_a
        else :
            selection = self.iconview.get_selected_items()
        selection.sort(key=lambda x: x[0])
        data = []
        target_s =  str(selection_data.get_target())
        for path in selection:
            if target_s == 'MODEL_ROW_INTERN':
                data.append(str(path[0]))
            elif target_s == 'MODEL_ROW_EXTERN':
                iter = model.get_iter(path)
                nfile, npage, angle = model.get(iter, 2, 3, 6)
                crop = model.get(iter, 7, 8, 9, 10)
                pdfdoc = self.pdfqueue[nfile - 1]
                data.append('\n'.join([pdfdoc.filename,
                                       str(npage),
                                       str(angle)] +
                                       [str(side) for side in crop]))
        if data:
            print (repr(data))
            data = bytes('\n;\n'.join(data), "utf-8")
            print (repr(data))
            selection_data.set(selection_data.get_target(), 8, data)

    def iv_dnd_received_data(self, iconview, context, x, y,
                             selection_data, target_id, etime):
        """Handles received data by drag and drop in iconview"""

        model = iconview.get_model()
        data = selection_data.get_data().decode("utf-8")
        if data:
            data = data.split('\n;\n')
            drop_info = iconview.get_dest_item_at_pos(x, y)
            iter_to = None
            if drop_info:
                path, position = drop_info
                ref_to = Gtk.TreeRowReference.new(model,path)
            else:
                position = Gtk.IconViewDropPosition.DROP_RIGHT
                if len(model) > 0:  #find the iterator of the last row
                    row = model[-1]
                    path = row.path
                    ref_to = Gtk.TreeRowReference(model,path)
            if ref_to:
                before = (position == Gtk.IconViewDropPosition.DROP_LEFT
                          or position == Gtk.IconViewDropPosition.DROP_ABOVE)
                #if target_id == self.MODEL_ROW_INTERN:
                if str(selection_data.get_target()) == 'MODEL_ROW_INTERN':
                    if before:
                        data.sort(key=int)
                    else:
                        data.sort(key=int,reverse=True)
                    data2 = []
                    for data1 in data :
                        data2.append(Gtk.TreePath.new_from_string(data1))
                    ref_from_list = [Gtk.TreeRowReference.new(model,path)
                                     for path in data2]
                    for ref_from in ref_from_list:
                        path = ref_to.get_path()
                        iter_to = model.get_iter(path)
                        path = ref_from.get_path()
                        iter_from = model.get_iter(path)
                        row = model[iter_from]
                        row_data = []
                        for a in row :
                            row_data.append(a)

                        if before:
                            iter_new = model.insert_before(iter_to, row_data)
                        else:
                            iter_new = model.insert_after(iter_to, row_data)


                    if context.get_selected_action() == Gdk.DragAction.MOVE:
                        for ref_from in ref_from_list:
                            path = ref_from.get_path()
                            iter_from = model.get_iter(path)
                            model.remove(iter_from)



                #elif target_id == self.MODEL_ROW_EXTERN:
                elif selection_data.target == 'MODEL_ROW_EXTERN':
                    if not before:
                        data.reverse()
                    while data:
                        tmp = data.pop(0).split('\n')
                        filename = tmp[0]
                        npage, angle = [int(k) for k in tmp[1:3]]
                        crop = [float(side) for side in tmp[3:7]]
                        if self.add_pdf_pages(filename, npage, npage,
                                                        angle, crop):
                            if len(model) > 0:
                                path = ref_to.get_path()
                                iter_to = model.get_iter(path)
                                row = model[-1] #the last row
                                path = row.path
                                iter_from = model.get_iter(path)
                                if before:
                                    model.move_before(iter_from, iter_to)
                                else:
                                    model.move_after(iter_from, iter_to)
                                if context.action == Gdk.ACTION_MOVE:
                                    context.finish(True, True, etime)

    def iv_dnd_data_delete(self, widget, context):
        """Deletes dnd items after a successful move operation"""

        model = self.iconview.get_model()
        selection = self.iconview.get_selected_items()
        ref_del_list = [Gtk.TreeRowReference(model,path) for path in selection]
        for ref_del in ref_del_list:
            path = ref_del.get_path()
            iter = model.get_iter(path)
            model.remove(iter)

    def iv_dnd_motion(self, iconview, context, x, y, etime):
        """Handles the drag-motion signal in order to auto-scroll the view"""

        autoscroll_area = 40
        sw_vadj = self.sw.get_vadjustment()
        sw_height = self.sw.get_allocation().height
        if y -sw_vadj.get_value() < autoscroll_area:
            if not self.iv_auto_scroll_timer:
                self.iv_auto_scroll_direction = Gtk.DIR_UP
                self.iv_auto_scroll_timer = GObject.timeout_add(150,
                                                                self.iv_auto_scroll)
        elif y -sw_vadj.get_value() > sw_height - autoscroll_area:
            if not self.iv_auto_scroll_timer:
                self.iv_auto_scroll_direction = Gtk.DIR_DOWN
                self.iv_auto_scroll_timer = GObject.timeout_add(150,
                                                                self.iv_auto_scroll)
        elif self.iv_auto_scroll_timer:
            GObject.source_remove(self.iv_auto_scroll_timer)
            self.iv_auto_scroll_timer = None

    def iv_dnd_leave_end(self, widget, context, ignored=None):
        """Ends the auto-scroll during DND"""

        if self.iv_auto_scroll_timer:
            GObject.source_remove(self.iv_auto_scroll_timer)
            self.iv_auto_scroll_timer = None

    def iv_auto_scroll(self):
        """Timeout routine for auto-scroll"""

        sw_vadj = self.sw.get_vadjustment()
        sw_vpos = sw_vadj.get_value()
        if self.iv_auto_scroll_direction == Gtk.DIR_UP:
            sw_vpos -= sw_vadj.step_increment
            sw_vadj.set_value(max(sw_vpos, sw_vadj.lower))
        elif self.iv_auto_scroll_direction == Gtk.DIR_DOWN:
            sw_vpos += sw_vadj.step_increment
            sw_vadj.set_value(min(sw_vpos, sw_vadj.upper - sw_vadj.page_size))
        return True  #call me again

    def iv_button_press_event(self, iconview, event):
        """Manages mouse clicks on the iconview"""

        x = int(event.x)
        y = int(event.y)
        path = iconview.get_path_at_pos(x, y)
        if path == None :
            return
        #print event.button
        if event.button == 1:  # Left button
            global shuffler_selection_a
            shuffler_selection_a = []
            time = event.time
            selection = iconview.get_selected_items()
            if path:
                if path in selection:
                    # Record the selection
                    shuffler_selection_a = selection


        if event.button == 3:
            time = event.time
            selection = iconview.get_selected_items()
            if path:
                if path not in selection:
                    iconview.unselect_all()
                iconview.select_path(path)
                iconview.grab_focus()
                self.popup.popup(None, None, None, None, event.button, time)
            return 1
        elif event.state & Gdk.ModifierType.SHIFT_MASK :
            first_selection = self.selection_start
            last_selection = path[0]
            if last_selection > first_selection :
                step = 1
                last_selection += 1
            else :
                step = -1
                last_selection -= 1
            for a in range(first_selection,last_selection, step) :
                iconview.select_path(str(a))
                # TODO : File "D:\Mes Documents\en cours\PdfBooklet3\pdfshuffler_g3.py", line 923, in iv_button_press_event
                #  iconview.select_path(str(a))
                # TypeError: argument path: Expected Gtk.TreePath, but got str

            return True
        else :
            self.selection_start = path[0]





    def sw_dnd_received_data(self, scrolledwindow, context, x, y,
                             selection_data, target_id, etime):
        """Handles received data by drag and drop in scrolledwindow"""

        data = selection_data.data
        if target_id == self.MODEL_ROW_EXTERN:
            self.model
            if data:
                data = data.split('\n;\n')
            while data:
                tmp = data.pop(0).split('\n')
                filename = tmp[0]
                npage, angle = [int(k) for k in tmp[1:3]]
                crop = [float(side) for side in tmp[3:7]]
                if self.add_pdf_pages(filename, npage, npage, angle, crop):
                    if context.action == Gdk.ACTION_MOVE:
                        context.finish(True, True, etime)
        elif target_id == self.TEXT_URI_LIST:
            uri = data.strip()
            uri_splitted = uri.split() # we may have more than one file dropped
            for uri in uri_splitted:
                filename = self.get_file_path_from_dnd_dropped_uri(uri)
                if os.path.isfile(filename): # is it file?
                    self.add_pdf_pages(filename)

    def sw_button_press_event(self, scrolledwindow, event):
        """Unselects all items in iconview on mouse click in scrolledwindow"""

        if event.button == 1:
            self.iconview.unselect_all()

    def sw_scroll_event(self, scrolledwindow, event):
        """Manages mouse scroll events in scrolledwindow"""

        if event.state & Gdk.CONTROL_MASK:
            if event.direction == Gdk.SCROLL_UP:
                self.zoom_change(1)
                return 1
            elif event.direction == Gdk.SCROLL_DOWN:
                self.zoom_change(-1)
                return 1

    def zoom_set(self, level):
        """Sets the zoom level"""
        self.zoom_level = max(min(level, 5), -24)
        self.zoom_scale = 1.1 ** self.zoom_level
        for row in self.model:
            row[4] = self.zoom_scale
        self.reset_iv_width()

    def zoom_change(self, step=5):
        """Modifies the zoom level"""
        bar = self.uiXML.get_object('hscale1')
        bar.set_value(self.zoom_level + step)
        self.zoom_set(self.zoom_level + step)

    def zoom_in(self, widget=None):
        """Increases the zoom level by 5 steps"""
        self.zoom_change(5)

    def zoom_out(self, widget=None, step=5):
        """Reduces the zoom level by 5 steps"""
        self.zoom_change(-5)

    def zoom_bar(self,widget,a=None, b=None):
        """Modifies the zoom level with the slider"""
        zoom_scale = widget.get_value()
        self.zoom_set(zoom_scale)



    def get_file_path_from_dnd_dropped_uri(self, uri):
        """Extracts the path from an uri"""

        path = urllib.request.url2pathname(uri) # escape special chars
        path = path.strip('\r\n\x00')   # remove \r\n and NULL

        # get the path to file
        if path.startswith('file:\\\\\\'): # windows
            path = path[8:]  # 8 is len('file:///')
        elif path.startswith('file://'):   # nautilus, rox
            path = path[7:]  # 7 is len('file://')
        elif path.startswith('file:'):     # xffm
            path = path[5:]  # 5 is len('file:')
        return path

    def rotate_page_right(self, widget, data=None):
        self.rotate_page(90)

    def rotate_page_left(self, widget, data=None):
        self.rotate_page(-90)

    def rotate_page(self, angle):
        """Rotates the selected page in the IconView"""

        model = self.iconview.get_model()
        selection = self.iconview.get_selected_items()
        if len(selection) > 0:
            self.set_unsaved(True)
        rotate_times = (((-angle) % 360 + 45) / 90) % 4
        if rotate_times is not 0:
            for path in selection:
                iter = model.get_iter(path)
                nfile = model.get_value(iter, 2)
                npage = model.get_value(iter, 3)

                crop = [0.,0.,0.,0.]
                perm = [0,2,1,3]
                for it in range(int(rotate_times)):
                    perm.append(perm.pop(0))
                perm.insert(1,perm.pop(2))
                crop = [model.get_value(iter, 7 + perm[side]) for side in range(4)]
                for side in range(4):
                    model.set_value(iter, 7 + side, crop[side])

                new_angle = model.get_value(iter, 6) + int(angle)
                new_angle = new_angle % 360
                model.set_value(iter, 6, new_angle)
                self.update_geometry(iter)
        self.reset_iv_width()

    def crop_page_dialog(self, widget):
        """Opens a dialog box to define margins for page cropping"""

        sides = ('L', 'R', 'T', 'B')
        side_names = {'L':_('Left'), 'R':_('Right'),
                      'T':_('Top'), 'B':_('Bottom') }
        opposite_sides = {'L':'R', 'R':'L', 'T':'B', 'B':'T' }

        def set_crop_value(spinbutton, side):
           opp_side = opposite_sides[side]
           pos = sides.index(opp_side)
           adj = spin_list[pos].get_adjustment()
           adj.set_upper(99.0 - spinbutton.get_value())

        model = self.iconview.get_model()
        selection = self.iconview.get_selected_items()

        crop = [0.,0.,0.,0.]
        if selection:
            path = selection[0]
            pos = model.get_iter(path)
            crop = [model.get_value(pos, 7 + side) for side in range(4)]


        dialog = Gtk.Dialog(title=(_('Crop Selected Pages')),
                            parent=self.window,
                            flags=Gtk.DialogFlags.MODAL,
                            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                     Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_size_request(340, 250)
        dialog.set_default_response(Gtk.ResponseType.OK)

        frame = Gtk.Frame()
        frame.set_label(_('Crop Margins'))
        dialog.vbox.pack_start(frame, False, False, 20)

        vbox = Gtk.VBox(False, 0)
        frame.add(vbox)

        spin_list = []
        units = 2 * [_('% of width')] + 2 * [_('% of height')]
        for side in sides:
            hbox = Gtk.HBox(True, 0)
            vbox.pack_start(hbox, False, False, 5)

            label = Gtk.Label(side_names[side])
            label.set_alignment(0, 0.0)
            hbox.pack_start(label, True, True, 20)

            adj = Gtk.Adjustment(100.*crop.pop(0), 0.0, 99.0, 1.0, 5.0, 0.0)
##            spin = Gtk.SpinButton(adj, 0, 1)
            spin = Gtk.SpinButton()
            spin.set_adjustment(adj)
            spin.set_activates_default(True)
            spin.connect('value-changed', set_crop_value, side)
            spin_list.append(spin)
            hbox.pack_start(spin, False, False, 30)

            label = Gtk.Label(units.pop(0))
            label.set_alignment(0, 0.0)
            hbox.pack_start(label, True, True, 0)

        dialog.show_all()
        result = dialog.run()

        if result == Gtk.ResponseType.OK:
            modified = False
            crop = [spin.get_value()/100. for spin in spin_list]
            for path in selection:
                pos = model.get_iter(path)
                for it in range(4):
                    old_val = model.get_value(pos, 7 + it)
                    model.set_value(pos, 7 + it, crop[it])
                    if crop[it] != old_val:
                        modified = True
                self.update_geometry(pos)
            if modified:
                self.set_unsaved(True)
            self.reset_iv_width()
        elif result == Gtk.ResponseType.CANCEL:
            print((_('Dialog closed')))
        dialog.destroy()

    def about_dialog(self, widget, data=None):
        about_dialog = Gtk.AboutDialog()
        try:
            about_dialog.set_transient_for(self.window)
            about_dialog.set_modal(True)
        except:
            pass
        # FIXME
        about_dialog.set_name(APPNAME)
        about_dialog.set_version(VERSION)
        about_dialog.set_comments(_(
            '%s is a tool for rearranging and modifying PDF files. ' \
            'Developed using GTK+ and Python') % APPNAME)
        about_dialog.set_authors(['Konstantinos Poulios',])
        about_dialog.set_website_label(WEBSITE)
        about_dialog.set_logo_icon_name('pdfshuffler')
        about_dialog.set_license(LICENSE)
        about_dialog.connect('response', lambda w, *args: w.destroy())
        about_dialog.connect('delete_event', lambda w, *args: w.destroy())
        about_dialog.show_all()

    def toto(self) :
        print ("toto")


class PDF_Doc:
    """Class handling PDF documents"""

    def __init__(self, filename, nfile, tmp_dir):

        self.filename = os.path.abspath(filename)
        (self.path, self.shortname) = os.path.split(self.filename)
        (self.shortname, self.ext) = os.path.splitext(self.shortname)
##        f = Gio.File
##        mime_type = f.query_info('standard::content-type').get_content_type()
##        expected_mime_type = pdf_mime_type
##
##        if mime_type == expected_mime_type:
        if 1 == 1 :
            self.nfile = nfile + 1
            self.mtime = os.path.getmtime(filename)
            self.copyname = os.path.join(tmp_dir, '%02d_' % self.nfile +
                                                  self.shortname + '.pdf')
            shutil.copy(self.filename, self.copyname)
            self.document = Poppler.Document.new_from_file (file_prefix + self.copyname, None)
            self.npage = self.document.get_n_pages()
        else:
            self.nfile = 0
            self.npage = 0



class PDF_Renderer(threading.Thread, GObject.GObject):

    def __init__(self, model, pdfqueue, resample=1.):
        # print("resample", resample)
        threading.Thread.__init__(self)
        GObject.GObject.__init__(self)
        self.model = model
        self.pdfqueue = pdfqueue
        self.resample = resample
        self.quit = False

    def run(self):
        for idx, row in enumerate(self.model):
            if self.quit:
                return
            if not row[1]:
                try:
                    nfile = row[2]
                    npage = row[3]
                    pdfdoc = self.pdfqueue[nfile - 1]
                    page = pdfdoc.document.get_page(npage-1)
                    w, h = page.get_size()
                    thumbnail = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                   int(w/self.resample),
                                                   int(h/self.resample))
##                    thumbnail1 = cairo.image_surface_create()
##                    thumbnail = thumbnail1(1,
##                                                   int(w/self.resample),
##                                                   int(h/self.resample))


                    cr = cairo.Context(thumbnail)
                    if self.resample != 1.:
                        cr.scale(1./self.resample, 1./self.resample)
                    page.render(cr)
                    time.sleep(0.003)
                    GObject.idle_add(self.emit,'update_thumbnail',
                                     idx, thumbnail, self.resample,
                                     priority=GObject.PRIORITY_LOW)
                except Exception as e:
                    print(e)


class PdfShuffler_Linux_code :
    def __init__(self):

        global pdf_mime_type, file_prefix
        pdf_mime_type = "application/pdf"
        file_prefix = 'file://'

    def home_dir(self):
        return os.getenv('HOME')


    def remove_temp_dir(self, tmp_dir):
        shutil.rmtree(tmp_dir)

    def check_same_file(self, filename, it_pdfdoc):

        if os.path.isfile(it_pdfdoc.filename) and \
               os.path.samefile(filename, it_pdfdoc.filename) and \
               os.path.getmtime(filename) is it_pdfdoc.mtime:
            return True
        else :
            return False


class PdfShuffler_Windows_code :
    def __init__(self):
        global _winreg, pdf_mime_type, file_prefix

##        import winreg   python 27
        pdf_mime_type = ".pdf"
        file_prefix = 'file:///'



    def home_dir(self) :
        return ""           # python 3
        global _winreg
        regKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        myDocuments = _winreg.QueryValueEx(regKey, 'Personal')[0]
        return myDocuments

    def remove_temp_dir(self, tmp_dir):

        # ============= Python-poppler for Windows bug workaround ============
        # python-poppler does not "release" the file and only the files of previous sessions can be deleted
        # Get the list of all pdf-shuffler temporary dirs
        temp_dir_root = os.path.split(tmp_dir)[0]
        shuffler_dirs = glob.glob(temp_dir_root + "/tmp??????pdfshuffler")
        # delete if possible
        for directory in shuffler_dirs :
            try :
                shutil.rmtree(directory)
            except :
                pass

    def check_same_file(self, filename, it_pdfdoc) :
        # The samefile method does not exist in Windows versions of Python
           if os.path.isfile(it_pdfdoc.filename) and \
               filename == it_pdfdoc.filename and \
               os.path.getmtime(filename) is it_pdfdoc.mtime:
                return True
           else :
                return False

def main():
    """This function starts PdfShuffler"""
##    Gdk.threads_init()
##    GObject.threads_init()
##    Gdk.threads_enter()     # This line is necessary in Windows
    PdfShuffler()
    Gtk.main()

if __name__ == '__main__':

    main()

