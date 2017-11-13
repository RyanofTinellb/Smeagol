from collections import namedtuple
from translation import *
import Tkinter as Tk

"""Site properties are named tuples:
    :var name: (str) The human-readable name of the property to be modified
    :var property: (str) The name of the property as used by Smeagol
    :var owner (str) If this property pertains to the 'site'
               (obj) A Links class, if the property pertains to
                    the editor
    :var check: (bool) Whether this property has a Checkbutton
    :var entry: (bool) Whether this property has a Textbox / Entry
    :var browse: (bool) Whether to have a browse button
                 (str) 'folder' if this property is to search for a
                        directory
                 ((str, str)) if this property is to search for a
                        file, this is the tuple used by
                        Tkinter's FileDialog"""

class PropertiesWindow(Tk.Toplevel, object):

    """
    Properties:
        - site destination
        - site name
        - site source
        - site template
        - site markdown
        - site searchjson
        - site leaf_level
        - editor links (x4)
    """
    def __init__(self, current_values, master=None):
        self.current_values = current_values
        super(PropertiesWindow, self).__init__(master)
        commands = dict(done=self.finish_window, cancel=self.cancel_window)
        self.property_frames = []
        for row, (current_value, property_) in enumerate(zip(current_values, editor_properties)):
            property_frame = PropertyFrame(self, row, current_value, commands, *property_)
            self.property_frames.append(property_frame)
        self.configure_buttons(row+1, commands)
        self.property_frames[0].entry.focus_set()

    def configure_buttons(self, row, commands):
        done_button = Tk.Button(self, text='OK', command=commands['done'])
        cancel_button = Tk.Button(self, text='Cancel', command=commands['cancel'])
        done_button.grid(row=row, column=3, sticky=Tk.E+Tk.W)
        cancel_button.grid(row=row, column=2, sticky=Tk.E)

    def finish_window(self, event=None):
        """
        Set values to site values and links values from the properties
            window, and then disable the window
        """
        self.site_values = {}
        self.link_values = []
        files = {}
        for value in self.new_values:
            if value['owner'] == 'site':
                self.site_values[value['property']] = value['value']
            elif value['owner'] == 'file':
                files[value['property']] = value['value']
            elif value['check'] == 1:
                if value['value'] == '':
                    self.link_values.append(value['owner']())
                else:
                    self.link_values.append(value['owner'](value['value']))
        files = Files(**files)
        self.site_values['files'] = files
        self.destroy()

    @property
    def new_values(self):
        for property_frame in self.property_frames:
            yield property_frame.get()

    def cancel_window(self, event=None):
        """
        Do nothing if cancel button pressed
        """
        self.destroy()

class PropertyFrame:
    """
    Wrapper class for one row of a PropertiesWindow
    """
    def __init__(self, master, row, defaults, commands=None, human_name='',
                property_name='', owner='site', check=False, entry=False, browse=False):
        """
        Create a row of the properties window

        :param master: (widget) the widget to which all the widgets of
            this frame belong.
        :param row: (int) the row of the window onto which to place
            this frame.
        :param defaults: ((int, str)), current state of checkbox and textbox
        :param commands: ({str:method}) the 'done' and 'cancel' commands
            for the outer window.
        :param human_name: (str) the human-readable name of the property
        :param property_name: (str) the Smeagol name of the property
        :param check: (bool) whether to have a checkboxes
        :param entry: (bool) whether to have a textbox/entry
        :param browse: (bool) Whether to have a browse button
                       (str) 'folder' if this property is to search for a
                            directory
                       ((str, str)) if this property is to search for a
                            file. This is the tuple used by
                            Tkinter's FileDialog
        """
        self.owner = owner
        self.property = property_name
        self.checkvar, self.entryvar = Tk.IntVar(), Tk.StringVar()
        self.entry = self.check = self.button = self.label = None
        defaults = dict(zip(['check', 'text'], defaults))
        if check:
            self.checkvar.set(defaults['check'])
            self.check = Tk.Checkbutton(master, variable=self.checkvar)
            self.check.grid(row=row, column=0)
        self.label = Tk.Label(master, text=human_name)
        self.label.grid(row=row, column=1, sticky=Tk.W)
        if entry:
            self.entryvar.set(defaults['text'])
            self.entry = Tk.Entry(master, width=50, textvariable=self.entryvar)
            self.entry.bind('<Return>', commands['done'])
            self.entry.bind('<Escape>', commands['cancel'])
            self.entry.grid(row=row, column=2)
        if browse:
            if browse == 'folder':
                self.browse = self.browse_folder
            else:
                self.browse = self.file_browser(browse)
            self.button = Tk.Button(master, text='Browse...', command=self.browse)
            self.button.grid(row=row, column=3)

    def browse_folder(self):
        """
        Allow the user to browse for a folder
        """
        filename = fd.askdirectory()
        self.insert(filename)
        self.entry.focus_set()

    def file_browser(self, filetype):
        def browse_file():
            """
            Allow the user to browse for a file of a given filetype

            :param filetype: (str()) The usual tuple passed to a Tk.FileDialog
            """
            filename = fd.askopenfilename(filetypes=[filetype], title='Select File')
            self.insert(filename)
            if filename:
                with ignored(AttributeError):
                    self.check.select()
            self.entry.focus_set()
        return browse_file

    def insert(self, text=None):
        """
        Insert text into the appropriate textbox
        """
        if text:
            self.entry.delete(0, Tk.END)
            self.entry.insert(Tk.INSERT, text)

    def get(self):
        return dict(owner=self.owner, property=self.property,
                check=self.checkvar.get(), value=self.entryvar.get())

Property = namedtuple('Property', ['name', 'property', 'owner', 'check', 'textbox', 'browse'])
editor_properties = [Property('Destination', 'destination', 'site', False, True, 'folder'),
    Property('Name', 'name', 'site', False, True,  False),
    Property('Source', 'source', 'file', False, True, ('Data File', '*.txt')),
    Property('Template', 'template', 'file', False, True, ('HTML Template', '*.html')),
    Property('URL/JSON Markdown', 'markdown', 'file', False, True, ('Markdown File', '*.mkd')),
    Property('Searchterms File', 'searchjson', 'file', False, True, ('JSON File', '*.json')),
    Property('Leaf Level', 'leaf_level', 'site', False, True, False),
    Property('Version Links', 'internalstory', InternalStory, True, False, False),
    Property('Links within the Dictionary', 'internaldictionary', InternalDictionary, True, False, False),
    Property('Links to external grammar site', 'externalgrammar', ExternalGrammar, True, True, ('Grammar Links File', '*.txt')),
    Property('Links to external dictionary site', 'externaldictionary', ExternalDictionary, True, False, False)]
