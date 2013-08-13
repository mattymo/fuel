#!/usr/bin/env python

import urwid
import urwid.raw_display
import urwid.web_display
import logging
import sys
import copy
import socket, struct
sys.path.append("/home/mmosesohn/git/fuel/iso/fuelmenu")
from settings import *
from urwidwrapper import *
log = logging.getLogger('fuelmenu.mirrors')
log.info("test")
blank = urwid.Divider()


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



class cobbler(urwid.WidgetWrap):
  def __init__(self, parent):
    self.name="Network"
    self.priority=20
    self.visible=True
    self.netsettings = dict()
    self.getNetwork()
    self.gateway=self.get_default_gateway_linux()
    self.activeiface = self.netsettings.keys()[0]
    self.screen = self.screenUI()
    self.parent = parent
     
  def check(self, args):
    #TODO: Ensure all params are filled out and sensible
    return True

  def apply(self, args):
    # set up logging
    import logging
    log = logging.getLogger('fuelmenu.cobbler')
    if not self.check(args):
        log.error("Check failed. Not applying")
        return False
    newsettings = dict()
    newsettings['common'] = { YAMLTREE : { "domain" : DEFAULTS['domain']['value']}}
    for key, widget in self.edits.items():
        text = widget.original_widget.get_edit_text()
        newsettings['common'][YAMLTREE][key] = text
    log.warning(str(newsettings))
    Settings().write(newsettings, tree=YAMLTREE)
    logging.warning('And this, too')

       
  def getNetwork(self):
    """Uses netifaces module to get addr, broadcast, netmask about
       network interfaces"""
    import netifaces
    for iface in netifaces.interfaces():
      if 'lo' in iface or 'vir' in iface:
      #if 'lo' in iface or 'vir' in iface or 'vbox' in iface:
        continue
      #print netifaces.ifaddresses(iface)
      #print iface, netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
      self.netsettings.update({iface: netifaces.ifaddresses(iface)[netifaces.AF_INET][0]})
    
  
  def get_default_gateway_linux(self):
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

  def radioSelect(self, obj, anotherarg):
    self.activeiface = obj.get_label()
    self.gateway=self.get_default_gateway_linux()
    self.getNetwork()
    screen=self.screenUI()
    self.listbox_content = self.listbox_content[:3]
    self.listbox_content.extend([self.net_text1, self.net_text1, self.net_text2, self.net_text3,
                                 self.net_text4, self.net_choices,blank])
    self.listbox_content.extend(self.edits.values())
    #self.listbox_content.append(blank)
    #self.listbox_content.append(check_col)

    self.listwalker[:]=self.listbox_content
    #self.parent.listwalker[:]=[self.parent.cols]
    return 

  def screenUI(self):
    #Define your text labels, text fields, and buttons first
    text1 = urwid.Text("Master node network settings")

    #Current network settings
    self.net_text1 = TextLabel("Current network settings for %s" % self.activeiface)
    self.net_text2 = TextLabel("IP address: %s" % self.netsettings[self.activeiface]['addr'])
    self.net_text3 = TextLabel("Netmask: %s" % self.netsettings[self.activeiface]['netmask'])
    self.net_text4 = TextLabel("Default gateway: %s" % (self.gateway))
    self.net_choices = ChoicesGroup(self, self.netsettings.keys(),self.activeiface)

    self.edits = dict()
    for key, values in DEFAULTS.items():
       #Example: key = hostname, label = Hostname, value = fuel-pm
       caption = values["label"]
       default = values["value"]
       self.edits[key] = TextField(key, caption, 23, default)

    #Button to check
    button_check = urwid.Button("Check", self.check)
    #Button to apply (and check again)
    button_apply = urwid.Button("Apply", self.apply)
    #Wrap into Columns so it doesn't expand and look ugly
    check_col = Columns([button_check, button_apply,('weight',7,blank)])

    #self.listbox_content.extend([net_text1, net_text2, net_text3, net_text4])
    self.listbox_content = [text1, blank, blank]
    self.listbox_content.extend([self.net_text1, self.net_text2, self.net_text3, 
                                 self.net_text4, self.net_choices,blank])
    self.listbox_content.extend(self.edits.values())
    self.listbox_content.append(blank)   
    self.listbox_content.append(check_col)   

    #Add listeners 
    
    #Build all of these into a list
    #self.listbox_content = [ text1, blank, blank, edit1, edit2, \
    #                    edit3, edit4, edit5, edit6, button_check ]
   
    #Add everything into a ListBox and return it
    self.listwalker=urwid.SimpleListWalker(self.listbox_content)
    screen = urwid.ListBox(self.listwalker)
    return screen
    
