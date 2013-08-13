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

#Need to define fields in order so it will render correctly
fields = ["hostname", "domain", "mgmt_if","dhcp_start","dhcp_end","blank",
          "blank","ext_if","blank","ext_dhcp","ext_ip","ext_netmask",
          "ext_gateway","ext_dns"]
DEFAULTS = {
  "dhcp_start" : { "label"  : "DHCP Pool Start",
                   "tooltip": "Used for defining Floating IP range",
                   "value"  : "10.0.0.201"},
  "dhcp_end"   : { "label"  : "DHCP Pool End",
                   "tooltip": "Used for defining Floating IP range",
                   "value"  : "10.0.0.254"},
  "mgmt_if"    : { "label"  : "Management Interface",
                   "tooltip": "This is the INTERNAL network for provisioning",
                   "value"  : "eth0"},
  "ext_if"     : { "label"  : "External Interface",
                   "tooltip": "This is the EXTERNAL network for Internet access",
                   "value"  : "eth1"},
  "ext_dhcp"   : { "label"  : "Use automatic DHCP config for external network",
                   "tooltip": "",
                   "value"  : "radio"},
  "ext_ip"     : { "label"  : "External IP",
                   "tooltip": "Manual IP address for external network (example 192.168.1.2)",
                   "value"  : ""},
  "ext_netmask": { "label"  : "External Netmask",
                   "tooltip": "Manual netmask for external network (example 255.255.255.0)",
                   "value"  : "255.255.255.0"},
  "ext_gateway": { "label"  : "External Gateway",
                   "tooltip": "Manual gateway to access Internet (example 192.168.1.1)",
                   "value"  : ""},
  "ext_dns"    : { "label"  : "External DNS",
                   "tooltip": "DNS server to handle DNS requests (example 8.8.8.8)",
                   "value"  : ""},
  "domain"     : { "label"  : "Domain",
                   "tooltip": "Domain suffix to user for all nodes in your cluster",
                   "value"  : "local"},
  "hostname"   : { "label"  : "Hostname",
                   "tooltip": "Hostname to use for Fuel master node",
                   "value"  : "fuel-pm"}
}
YAMLTREE = "cobbler_common"



class network(urwid.WidgetWrap):
  def __init__(self, parent):
    self.name="Network"
    self.priority=20
    self.visible=True
    self.netsettings = dict()
    self.getNetwork()
    self.gateway=self.get_default_gateway_linux()
    self.activeiface = sorted(self.netsettings.keys())[0]
    self.extdhcp=True
    self.parent = parent
    self.screen = self.screenUI()
     
  def check(self, args):
     
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

  def radioSelectIface(self, current, state, user_data=None):
    """Update network details and display information"""
    ### This makes no sense, but urwid returns the previous object.
    ### The previous object has True state, which is wrong.. 
    ### Somewhere in current.group a RadioButton is set to True.
    ### Our quest is to find it.
    for rb in current.group:
       if rb.get_label() == current.get_label():
         continue
       if rb.base_widget.state == True:
         self.activeiface = rb.base_widget.get_label()
         break
    self.gateway=self.get_default_gateway_linux()
    self.getNetwork()
    self.setNetworkDetails()
    return 

  def radioSelectExtIf(self, current, state, user_data=None):
    """Update network details and display information"""
    ### This makes no sense, but urwid returns the previous object.
    ### The previous object has True state, which is wrong.. 
    ### Somewhere in current.group a RadioButton is set to True.
    ### Our quest is to find it.
    for rb in current.group:
       if rb.get_label() == current.get_label():
         continue
       if rb.base_widget.state == True:
         if rb.base_widget.get_label() == "Yes":
           self.extdhcp=True
         else:
           self.extdhcp=False
         break
    self.setExtIfaceFields(self.extdhcp)
    return 

  def setNetworkDetails(self):
    self.net_text1.set_text("Current network settings for %s" % self.activeiface)
    self.net_text2.set_text("IP address:       %s" % self.netsettings[self.activeiface]['addr'])
    self.net_text3.set_text("Netmask:          %s" % self.netsettings[self.activeiface]['netmask'])
    self.net_text4.set_text("Default gateway:  %s" % (self.gateway))

  def setExtIfaceFields(self, enabled=True):
    ###TODO: Define ext iface fields as disabled and then toggle
    pass
  def screenUI(self):
    #Define your text labels, text fields, and buttons first
    text1 = urwid.Text("Master node network settings")

    #Current network settings
    self.net_text1 = TextLabel("")
    self.net_text2 = TextLabel("")
    self.net_text3 = TextLabel("")
    self.net_text4 = TextLabel("")
    self.setNetworkDetails()
    self.net_choices = ChoicesGroup(self, sorted(self.netsettings.keys()), fn=self.radioSelectIface)

    self.edits = []
    toolbar = self.parent.footer
    for key in fields:
    #for key, values in DEFAULTS.items():
       #Example: key = hostname, label = Hostname, value = fuel-pm
       if key == "blank":
         self.edits.append(blank)
       elif DEFAULTS[key]["value"] == "radio":
         label = TextLabel(DEFAULTS[key]["label"])
         choices = ChoicesGroup(self,["Yes", "No"],
                    default_value="Yes", fn=self.radioSelectExtIf)
         self.edits.append(Columns([label,choices]))
       else:
         caption = DEFAULTS[key]["label"]
         default = DEFAULTS[key]["value"]
         tooltip = DEFAULTS[key]["tooltip"]
         self.edits.append(TextField(key, caption, 23, default, tooltip, toolbar))


    #Button to check
    button_check = Button("Check", self.check)
    #Button to apply (and check again)
    button_apply = Button("Apply", self.apply)

    #Wrap buttons into Columns so it doesn't expand and look ugly
    check_col = Columns([button_check, button_apply,('weight',7,blank)])

    self.listbox_content = [text1, blank, blank]
    self.listbox_content.extend([self.net_text1, self.net_text2, self.net_text3, 
                                 self.net_text4, self.net_choices,blank])
    self.listbox_content.extend(self.edits)
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
    
