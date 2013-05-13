import urwid
import urwid.raw_display
import urwid.web_display
import sys
import operator
import os
import sys

# set up logging
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('fuelmenu.loader')

class Loader:

    def __init__(self, parent):
        self.modlist = []
        self.choices = []
        self.child = None
        self.children = []
        self.childpage = None
        self.parent = parent
    def load_modules(self, module_dir):
        if not module_dir in sys.path:
            sys.path.append(module_dir)

        modules = [os.path.splitext(f)[0] for f in os.listdir(module_dir)
                   if f.endswith('.py')]
        
        for module in modules:
            log.info('loading module %s', module)
            try:
                imported = __import__(module)
                pass
                #imported = process(module)
            except ImportError as e:
                log.error('module could not be imported: %s', e)
                continue

            clsobj = getattr(imported, module, None)
            modobj = clsobj(self.parent)

            # add the module to the list
            self.modlist.append(modobj)
        # sort modules
        self.modlist.sort(key=operator.attrgetter('priority'))
        for module in self.modlist:
            self.choices.append(module.name)
        return (self.modlist,self.choices)


version="2.1.1"
#choices= u"Status,Networking,OpenStack Setup,Terminal,Save & Quit".split(',')
class FuelSetup():

    def __init__(self):
        self.frame = None
        self.screen = None
        self.main()
        self.choices = []

    def menu(self, title, choices):
        body = [urwid.Text(title), urwid.Divider()]
        for c in choices:
            button = urwid.Button(c)
            urwid.connect_signal(button, 'click', self.menu_chosen, c)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))
    
    def menu_chosen(self, button, choice):
        size = self.screen.get_cols_rows()
        self.screen.draw_screen(size, self.frame.render(size))

        self.footer.set_text([u'You chose ', choice, u''])
        #self.child = self.children[self.choices.index(choice)]
        #self.childpage = self.child.screenUI()
        self.setChildScreen(name=choice)
        response = urwid.Text([u'You chose ', choice, u'\n'])
        done = urwid.Button(u'Ok')
        urwid.connect_signal(done, 'click', self.exit_program)
        self.frame.original_widget = urwid.Filler(urwid.Pile([response,
            urwid.AttrMap(done, None, focus_map='reversed')]))
    

    def setChildScreen(self, name=None):
        if name is None:
            child = self.children[0]
        else:
            log.info(name, self.choices.index(name))
            child = self.children[int(self.choices.index(name))]
        self.childpage = child.screenUI()
        self.childfill = urwid.Filler(self.childpage, 'middle', 20)
        self.childbox = urwid.BoxAdapter(self.childfill, 20)
        self.cols = urwid.Columns([
                ('fixed', 20, urwid.Pile([
                    urwid.AttrMap(self.menubox, 'bright'),
                    urwid.Divider(" ")])),
                ('weight', 3, urwid.Pile([
                    urwid.Divider(" "),
                    self.childbox,
                    urwid.Divider(" ")]))
                ], 3)
        self.listwalker[:] = [self.cols]

         

    def main(self):
    
        text_header = (u"Fuel %s setup "
            u"UP / DOWN / PAGE UP / PAGE DOWN scroll.  F8 exits."
            % version)
        text_footer = (u"Status messages go here.")
        text_columns1 = [('important', u"Columns"),
            u" are used to share horizontal screen space.  "
            u"This one splits the space into two parts with "
            u"three characters between each column.  The "
            u"contents of each column is a single widget."]
    #    text_columns1 = [('important', u"Columns"),
    #        u" are used to share horizontal screen space.  "
    #        u"This one splits the space into two parts with "
    #        u"three characters between each column.  The "
    #        u"contents of each column is a single widget."]
        text_columns2 = [u"When you need to put more than one "
            u"widget into a column you can use a ",('important',
            u"Pile"), u" to combine two or more widgets."]
        text_weight = u"Weight %d"
        text_fixed_9 = u"<Fixed 9>" # should be 9 columns wide
        text_fixed_14 = u"<--Fixed 14-->" # should be 14 columns wide
        text_edit_cap1 = ('editcp', u"This is a caption.  Edit here: ")
        text_edit_text1 = u"editable stuff"
        text_edit_cap2 = ('editcp', u"This one supports newlines: ")
        text_edit_text2 = (u"line one starts them all\n"
            u"== line 2 == with some more text to edit.. words.. whee..\n"
            u"LINE III, the line to end lines one and two, unless you "
            u"change something.")
    
    
        radio_button_group = []
    
        blank = urwid.Divider()
        listbox_content = [
            blank,
            urwid.Columns([
                #urwid.Padding(menu(u'Topics', choices), left=1, right=1,
                #    min_width=20),
                urwid.Pile([
                    #urwid.Padding(urwid.Text(text_columns1)),
                    urwid.Text(text_columns1),
                    urwid.Divider("~")]),
                urwid.Pile([
                    urwid.Divider("~"),
                    urwid.Text(text_columns2),
                    urwid.Divider("_")])
                ], 3),
            blank,
            urwid.Columns([
                ('weight', 2, urwid.AttrWrap(urwid.Text(
                    text_weight % 2), 'reverse')),
                ('fixed', 9, urwid.Text(text_fixed_9)),
                ('weight', 3, urwid.AttrWrap(urwid.Text(
                    text_weight % 2), 'reverse')),
                ('fixed', 14, urwid.Text(text_fixed_14)),
                ], 0, min_width=8),
            blank,
            urwid.AttrWrap(urwid.Edit(text_edit_cap1, text_edit_text1),
                'editbx', 'editfc'),
            blank,
            urwid.AttrWrap(urwid.Edit(text_edit_cap2, text_edit_text2,
                multiline=True ), 'editbx', 'editfc'),
            blank,
    
            ]
        #Prepare for child screen
        loader = Loader(self)
        self.children, self.choices = loader.load_modules(module_dir="./modules")
        if len(self.children) == 0:
          import sys
          sys.exit(1)




        #End prep
        menufill = urwid.Filler(self.menu(u'Menu', self.choices), 'top', 20)
        self.menubox = urwid.BoxAdapter(menufill, 40)


        child = self.children[0]
        self.childpage = child.screenUI()
        #childpage = urwid.ListBox(urwid.SimpleListWalker(listbox_content))
        #childpage = urwid.Text(text_fixed_14)
        self.childfill = urwid.Filler(self.childpage, 'middle', 20)
        self.childbox = urwid.BoxAdapter(self.childfill, 20)
        self.cols = urwid.Columns([
                ('fixed', 20, urwid.Pile([
                    urwid.AttrMap(self.menubox, 'bright'),
                    urwid.Divider(" ")])),
                ('weight', 3, urwid.Pile([
                    urwid.Divider(" "),
                    self.childbox,
                    urwid.Divider(" ")]))
                ], 3)
    
        self.header = urwid.AttrWrap(urwid.Text(text_header), 'header')
        self.footer = urwid.AttrWrap(urwid.Text(text_footer), 'footer')
        self.listwalker = urwid.SimpleListWalker([self.cols])
        self.listbox = urwid.ListBox(self.listwalker)
        #listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))
    
        #frame = urwid.Frame(urwid.AttrWrap(cols, 'background'), header=header, footer=footer)
        #frame = urwid.Frame(urwid.AttrWrap(cols, 'body'), header=header, footer=footer)
        self.frame = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'), header=self.header, footer=self.footer)
    
        palette = [
            ('body','black','light gray', 'standout'),
            ('reverse','light gray','black'),
            ('header','white','dark red', 'bold'),
            ('important','dark blue','light gray',('standout','underline')),
            ('editfc','white', 'dark blue', 'bold'),
            ('editbx','light gray', 'dark blue'),
            ('editcp','black','light gray', 'standout'),
            ('bright','dark gray','light gray', ('bold','standout')),
            ('buttn','black','dark cyan'),
            ('buttnf','white','dark blue','bold'),
            ]
    
    
        # use appropriate Screen class
        if urwid.web_display.is_web_request():
            self.screen = urwid.web_display.Screen()
        else:
            self.screen = urwid.raw_display.Screen()
    
        def unhandled(key):
            if key == 'f8':
                raise urwid.ExitMainLoop()
    
        urwid.MainLoop(self.frame, palette, self.screen,
            unhandled_input=unhandled).run()
    
    def exit_program(self, button):
        raise urwid.ExitMainLoop()


def setup():
    urwid.web_display.set_preferences("Fuel Setup")
    # try to handle short web requests quickly
    if urwid.web_display.handle_short_request():
         return
    fm = FuelSetup()
    

if '__main__'==__name__ or urwid.web_display.is_web_request():
    setup()

