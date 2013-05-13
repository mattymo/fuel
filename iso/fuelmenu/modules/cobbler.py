#!/usr/bin/env python

import urwid
import urwid.raw_display
import urwid.web_display
import sys
if not "./../" in sys.path:
    sys.path.append("./../")
import settings
DEFAULTS = {
  "dhcp_start" : { "label"  : "DHCP Pool Start",
                   "value"  : "10.0.0.201"},
  "dhcp_end"   : { "label"  : "DHCP Pool End",
                   "value"  : "10.0.0.254"},
  "mgmt_if"    : { "label"  : "Management Interface",
                   "value"  : "eth0"},
  "ext_if"     : { "label"  : "External Interface",
                   "value"  : "eth1"},
  "domain"     : { "label"  : "Domain",
                   "value"  : "local"},
  "hostname"   : { "label"  : "Hostname",
                   "value"  : "fuel-pm"}
}
YAMLTREE = "cobbler_common"

blank = urwid.Divider()


class cobbler():
  def __init__(self, parent):
    self.name="Network"
    self.priority=20
    self.visible=True
    self.screen = self.screenUI()
    self.parent = parent
  def check(self):
    #TODO: Ensure all params are filled out and sensible
    return True

  def applychanges(self, button):
    # set up logging
    import logging
#    logging.basicConfig(filename="/home/mmosesohn/git/fuel/iso/fuelmenu/fuelmenu.log",level=logging.DEBUG)
#    logging.debug('This message should appear on the console')
#    logging.info('So should this')
#    logging.warning('And this, too')
#    logging.warning("test")
#    self.parent.footer.set_text(u"applying")
    log = logging.getLogger('fuelmenu.cobbler')
    newsettings = dict()
    for key, widget in self.edits.items():
        text = widget.original_widget.get_edit_text()
        newsettings['common'][YAMLTREE][key] = text
    settings.Settings().write(newsettings, tree=YAMLTREE)
#    for item in self.listbox_content:
#       if isinstance(item, urwid.AttrMap):
#         item = item.original_widget
#       if not isinstance(item, urwid.Edit):
#         log.info("Skipping item: %s " % str(item))
#       else:
#         log.critical("Keeping item: %s " % str(item))
#       self.parent.footer.set_text((str(item)))
#    log.debug("test")
#    import logging
#    logging.basicConfig(filename='example.log',level=logging.DEBUG)
#    logging.debug('This message should go to the log file')
#    logging.info('So should this')
#    logging.warning('And this, too')

       

  def screenUI(self):
    #Define your text labels, text fields, and buttons first
    text1 = urwid.Text("Master node network settings")
    self.listbox_content = [text1, blank, blank]
    self.edits = dict()
    for key, values in DEFAULTS.items():
       label = values["label"]
       value = values["value"]
       #Example: key = hostname, label = Hostname, value = fuel-pm
       caption = label
       default = value
       self.edits[key] = urwid.AttrMap(urwid.Edit(('important', 
                caption.ljust(23)), default), 'editbx', 'editfc')
#    edit1_cap = "Hostname: "
#    edit1_def = DEFAULTS["hostname"]["value"]
#    edit1 = urwid.AttrMap(urwid.Edit(('important', edit1_cap.ljust(23)), edit1_def),
#                'editbx', 'editfc')
#    edit2_cap = "Domain: "
#    edit2_def =  DEFAULTS["domain"]["value"]
#    edit2 = urwid.AttrMap(urwid.Edit(('important', edit2_cap.ljust(23)), edit2_def),
#                'editbx', 'editfc')
#    edit3_cap = "Management interface: "
#    edit3_def =  DEFAULTS["mgmt_if"]["value"]
#    edit3 = urwid.AttrMap(urwid.Edit(('important', edit3_cap.ljust(23)), edit3_def),
#                'editbx', 'editfc')
#    edit4_cap = "External interface: "
#    edit4_def =  DEFAULTS["ext_if"]["value"]
#    edit4 = urwid.AttrMap(urwid.Edit(('important', edit4_cap.ljust(23)), edit4_def),
#                'editbx', 'editfc')
#    edit5_cap = "DHCP pool start: "
#    edit5_def =  DEFAULTS["dhcp_start"]["value"]
#    edit5 = urwid.AttrMap(urwid.Edit(('important', edit5_cap.ljust(23)), edit5_def),
#                'editbx', 'editfc')
#    edit6_cap = "DHCP pool end: "
#    edit6_def =  DEFAULTS["dhcp_end"]["value"]
#    edit6 = urwid.AttrMap(urwid.Edit(('important', edit6_cap.ljust(23)), edit6_def),
#                'editbx', 'editfc')
    #print self.edits.items()
    button_check = urwid.Button("Check", self.applychanges)
    self.listbox_content.extend(self.edits.values())
    self.listbox_content.append(button_check)   

    #Add listeners 
    
    #Build all of these into a list
    #self.listbox_content = [ text1, blank, blank, edit1, edit2, \
    #                    edit3, edit4, edit5, edit6, button_check ]
   
    #Add everything into a ListBox and return it
    screen = urwid.ListBox(urwid.SimpleListWalker(self.listbox_content))
    return screen
    
