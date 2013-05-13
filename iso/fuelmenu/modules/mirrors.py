#!/usr/bin/env python

import urwid
import urwid.raw_display
import urwid.web_display
import logging
import sys
import copy
#from fuelmenu import settings
log = logging.getLogger('fuelmenu.mirrors')
log.info("test")
blank = urwid.Divider()

DEFAULTS = {
"custom_mirror" : "http://mirror.your-company-name.com/",
"parent_proxy"  : "",
"port"          : "3128"
}
class mirrors(urwid.WidgetWrap):
  def __init__(self, parent):
    self.name="Repo Mirrors"
    self.priority=25
    self.visible=True
    self.parent = parent
    self.screen = self.screenUI()
    self.listbox_content = []
    self.settings = copy.deepcopy(DEFAULTS)

  def apply(self, args):
    if not check:
        log.error("Check failed. Not applying")
        return False
    conf = settings()
    conf.write(module="mirrors",values=self.settings)
    
  def check(self, args):
    log = logging.getLogger('fuelmenu.mirrors')
    
    customurl = self.edit1.get_edit_text()
    self.parent.footer.set_text("Checking %s" % customurl)
    log.info("Checking %s" % customurl)
    if self.repochoice == "Default":
      self.parent.footer.set_text("")
      pass
    else:
      #Ensure host can connect
      import subprocess
      reachable = subprocess.call(["curl","-o","/dev/null","--silent","--head","--write-out","'%{http_code}\n'",customurl])
      error_msg = None
      if reachable == 0:
         pass
      elif reachable == 1 or reachable == 3:
         error_msg = u"Unrecognized protocol. Did you spell it right?"
      elif reachable == 6:
         error_msg = u"Couldn't resolve host."
      elif reachable == 7:
         error_msg = u"Couldn't connect to host."
      elif reachable == 6:
         error_msg = u"Couldn't resolve host."
      if error_msg is not None:
         self.parent.footer.set_text("Could not reach custom mirror. Error: %s" % (customurl, reachable))
         return False

      #Ensure valid page with 2XX or 3XX return code
      status_code = subprocess.check_output(["curl","-o","/dev/null","--silent","--head","--write-out","'%{http_code}'",customurl])
      import re
      regexp = re.compile(r'[23]\d\d')
      if regexp.search(status_code) is not None:
         error_msg = "URL not reachable on server. Error %s" % status_code
         log.error("Could not reach custom url %s. Error code: %s" % (customurl, reachable))
         self.parent.footer.set_text("Could not reach custom url %s. Error code: %s" % (customurl, reachable))
         return False
    return True

  def radioSelect(self, obj, anotherarg):
      self.repochoice = obj.get_label()
      pass

  def screenUI(self):
    #Define your text labels, text fields, and buttons first
    text1 = urwid.Text(u"Choose repo mirrors to use.\n"
     u"Note: Refer to Fuel documentation on how to set up a custom mirror.")
    choice_list = [u"Default", u"Custom"]
    self.rb_group = []
    self.repochoice = choice_list[0]
    self.choices = urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.RadioButton(self.rb_group,
                txt, on_state_change=self.radioSelect), 'buttn','buttnf')
                for txt in choice_list],
            13, 3, 1, 'left') ,
            left=4, right=3, min_width=13)
 
    edit1_cap = "Custom URL: "
    edit1_def = DEFAULTS["custom_mirror"]
    self.edit1 = urwid.AttrWrap(urwid.Edit(('important', edit1_cap.ljust(15)), edit1_def),
                'editbx', 'editfc')
    edit2_cap = "Squid parent proxy: "
    edit2_def = DEFAULTS["parent_proxy"]
    self.edit2 = urwid.AttrWrap(urwid.Edit(('important', edit2_cap), edit2_def),
                'editbx', 'editfc')
    edit3_cap = "Port: "
    edit3_def = DEFAULTS["port"]
    self.edit3 = urwid.AttrWrap(urwid.Edit(('important', edit3_cap), edit3_def),
                'editbx', 'editfc')
    self.proxyedits = urwid.Padding(urwid.GridFlow([self.edit2, self.edit3],
                      61, 2, 0, 'left'),
                      left=0, right=0, min_width=70)
                       
    #Disable wrapper
    #self.edit1 = urwid.WidgetDisable(self.edit1_real)
    button_check = urwid.Button("Check", self.check)
   

    #Add listeners 
    
    #Build all of these into a list
    self.listbox_content = [ text1, blank, blank, self.choices, blank, self.edit1, blank, self.proxyedits, button_check ]
   
    #Add everything into a ListBox and return it
    self.myscreen = urwid.ListBox(urwid.SimpleListWalker(self.listbox_content))
    return self.myscreen
    
