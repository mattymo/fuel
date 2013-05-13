#!/usr/bin/env python

import urwid
import urwid.raw_display
import urwid.web_display

DEFAULTS = {
  "dhcp_start" : "10.0.0.201",
  "dhcp_end"   : "10.0.0.254",
  "mgmt_if"    : "eth0",
  "ext_if"     : "eth1",
  "domain"     : "local",
  "hostname"   : "fuel-pm"
}
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

  def screenUI(self):
    #Define your text labels, text fields, and buttons first
    text1 = urwid.Text("Master node network settings")
    edit1_cap = "Hostname: "
    edit1_def = DEFAULTS["hostname"]
    edit1 = urwid.AttrWrap(urwid.Edit(('important', edit1_cap.ljust(23)), edit1_def),
                'editbx', 'editfc')
    edit2_cap = "Domain: "
    edit2_def =  DEFAULTS["domain"]
    edit2 = urwid.AttrWrap(urwid.Edit(('important', edit2_cap.ljust(23)), edit2_def),
                'editbx', 'editfc')
    edit3_cap = "Management interface: "
    edit3_def =  DEFAULTS["mgmt_if"]
    edit3 = urwid.AttrWrap(urwid.Edit(('important', edit3_cap.ljust(23)), edit3_def),
                'editbx', 'editfc')
    edit4_cap = "External interface: "
    edit4_def =  DEFAULTS["ext_if"]
    edit4 = urwid.AttrWrap(urwid.Edit(('important', edit4_cap.ljust(23)), edit4_def),
                'editbx', 'editfc')
    edit5_cap = "DHCP pool start: "
    edit5_def =  DEFAULTS["dhcp_start"]
    edit5 = urwid.AttrWrap(urwid.Edit(('important', edit5_cap.ljust(23)), edit5_def),
                'editbx', 'editfc')
    edit6_cap = "DHCP pool end: "
    edit6_def =  DEFAULTS["dhcp_end"]
    edit6 = urwid.AttrWrap(urwid.Edit(('important', edit6_cap.ljust(23)), edit6_def),
                'editbx', 'editfc')

    button_check = urwid.Button("Check", self.check)
   

    #Add listeners 
    
    #Build all of these into a list
    listbox_content = [ text1, blank, blank, edit1, edit2, \
                        edit3, edit4, edit5, edit6 ]
   
    #Add everything into a ListBox and return it
    screen = urwid.ListBox(urwid.SimpleListWalker(listbox_content))
    return screen
    
