import urwid
import urwid.raw_display
import urwid.web_display

def TextField(keyword, label, width, default_value=None):
    """Returns an Urwid Edit object"""
    edit_obj = urwid.Edit(('important', label.ljust(width)), default_value)
    wrapped_obj = urwid.AttrWrap(edit_obj, 'editbx', 'editfc')
    return wrapped_obj

def ChoicesGroup(self, choices, default_value=None):
    """Returns a horizontal Urwid GridFlow with radio choices on one line."""
    rb_group = []
    
    for txt in choices:
        if default_value == None:
           is_default = "first True"
        else:
           is_default = True if txt == default_value else False
        radio_button = urwid.AttrWrap(urwid.RadioButton(rb_group,
                txt, is_default, on_state_change=self.radioSelect), 'buttn','buttnf')
    wrapped_choices = urwid.Padding(urwid.GridFlow(rb_group, 13, 3, 1, 
                'left'), left=4, right=3, min_width=13)
    return wrapped_choices
 
def TextLabel(text):
    """Returns an Urwid text object"""
    return urwid.Text(text)

def HorizontalGroup(objects, cell_width, align="left"):
    """Returns a padded Urwid GridFlow object that is left aligned"""
    return urwid.Padding(urwid.GridFlow(objects, cell_width, 1, 0, align), 
                 left=0,right=0,min_width=61)

def Columns(objects):
    """Returns a padded Urwid Columns object that is left aligned.
       Objects is a list of widgets. Widgets may be optionally specified
       as a tuple with ('weight', weight, widget) or (width, widget).
       Tuples without a widget have a weight of 1."""
    return urwid.Padding(urwid.Columns(objects, 1), 
                 left=0,right=0,min_width=61)

