from collections import OrderedDict, namedtuple
from itertools import chain
from smeagol import *
from translation import *
import webbrowser as web
import Tkinter as Tk
import tkFileDialog as fd
import tkMessageBox as mb


WidgetAmounts = namedtuple('WidgetAmounts', ['headings', 'textboxes', 'radios'])

"""
Site properties are named tuples:
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
                        Tkinter's FileDialog
"""
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


class Editor(Tk.Frame, object):
    """
    Base class for DictionaryEditor and StoryEditor
    """
    def __init__(self, site=None, markdown=None, links=None,
        widgets=WidgetAmounts(headings=3, textboxes=1, radios='languages'),
        font=('Corbel', '14')):
        """
        Initialise an instance of the Editor class.
        :param directory (str):
        :param widgets (WidgetAmounts): number of each of headings, textboxes,
            radiobuttons to create.
        """
        super(Editor, self).__init__(None)
        self.site = site
        self.markdown = markdown
        self.links = links
        self.widgets = widgets
        self.font = font

        self.buttonframe, self.textframe = Tk.Frame(self), Tk.Frame(self)
        self.headings, self.radios, self.texts = [], [], []
        self.buttons = self.load_button = self.save_button = self.label = None
        self.save_text, self.language = Tk.StringVar(), Tk.StringVar()
        self.save_text.set('Save')
        self.translator = Translator()
        self.entry = self.site.root
        self.root = self.site.root
        self.top = self.winfo_toplevel()

        self.create_widgets()
        self.configure_widgets()
        self.place_widgets()
        self.top.state('zoomed')
        self.go_to_heading()

    def create_widgets(self):
        self.menu = self.create_menu(self.top, self.menu_commands)
        self.headings = self.create_headings(self.buttonframe,
                self.widgets.headings)
        self.radios = self.create_radios(self.buttonframe, self.widgets.radios)
        self.labels = self.create_labels(self.buttonframe)
        self.buttons = self.create_buttons(self.buttonframe,
                self.button_commands, self.save_text)
        self.textboxes = self.create_textboxes(self.textframe,
                self.widgets.textboxes, self.font)

    def create_menu(self, master, menus=None):
        """
        Create a menu.

        :param master: (widget)
        :param menus: ((str, options=[])[]) A list of tuples of the form
                (label, options)
            :param label: (str): The name of the menu that the user will see.
            :param options: ((str, method)[]) A list of tuples of the form
                    (label, command)
                :param label: (str): The name of the menubutton that the user
                    will see. The letter following an underscore will be
                :param command: (method) The function to be run when this
                    option is selected from the menu.
        :returns: (widget)
        """
        if menus is None:
            menus = []
        menubar = Tk.Menu(master)
        for menu in menus:
            submenu = Tk.Menu(menubar, tearoff=0)
            label, options = menu
            menubar.add_cascade(label=label, menu=submenu)
            for option in options:
                label, command = option
                underline = label.find('_')
                underline = 0 if underline == -1 else underline
                label = label.replace('_', '')
                submenu.add_command(label=label, command=command,
                    underline=underline)
                submenu.bind('<KeyPress-{0}>'.format(label[underline]), command)
        return menubar

    @staticmethod
    def create_headings(master, number, commands=None):
        if not commands:
            commands = []
        headings = []
        for _ in range(number):
            heading = Tk.Entry(master)
            for (key, command) in commands:
                heading.bind(key, command)
            headings.append(heading)
        return headings

    @staticmethod
    def create_buttons(master, commands, save_variable):
        """
        Create a Load and a Save button.
        :param master (widget): which widget window to place the buttons in.
        :param commands (function(,)): pointer to the 'load' and 'save' methods.
        :param save_variable (Tk.StringVar): the textvariable for the 'save' button.
        """
        load_button = Tk.Button(master, text='Load', command=commands[0])
        save_button = Tk.Button(master, command=commands[1],
        textvariable=save_variable)
        return load_button, save_button

    def create_labels(self, master):
        information = Tk.StringVar()
        info_label = Tk.Label(master=master, textvariable=information)
        # blanklabel has enough height to push all other widgets to the top
        #   of the window.
        blank_label = Tk.Label(master=master, height=1000)
        return info_label, information, blank_label

    def create_radios(self, master, number):
        radios = []
        try:
            number = int(number)
        except ValueError:
            number = self.translator.number
        for _ in range(number):
            radio = Tk.Radiobutton(master)
            radios.append(radio)
        return tuple(radios)

    @staticmethod
    def create_textboxes(master, number, font=None):
        if font is None:
            font = self.font
        textboxes = []
        for _ in range(number):
            textbox = Tk.Text(master, height=1, width=1, wrap=Tk.WORD,
                    undo=True, font=font)
            textboxes.append(textbox)
        return tuple(textboxes)

    def configure_widgets(self):
        self.heading = self.headings[0]
        self.textbox = self.textboxes[0]
        self.infolabel, self.information, self.blanklabel = self.labels
        self.load_button, self.save_button = self.buttons
        self.configure_headings(self.heading_commands)
        self.configure_radios(self.radio_settings)
        self.configure_textboxes(self.textbox_commands)

    def configure_headings(self, commands=None):
        if commands:
            for heading in self.headings:
                for command in commands:
                    keys, command = command
                    for key in keys:
                        heading.bind(key, command)

    def configure_radios(self, settings=None):
        if settings:
            settings = zip(self.radios, settings)
            for radio, (code, language) in settings:
                radio.configure(text=language().name, variable=self.language,
                        value=code, command=self.change_language)
            self.language.set(self.translator.languages.keys()[0])
            self.translator = Translator(self.language.get())

    def configure_textboxes(self, commands=None):
        if commands:
            for textbox in self.textboxes:
                for (key, command) in commands:
                    textbox.bind(key, command)

    def place_widgets(self):
        """
        Place all widgets in GUI window.
        Stack the textboxes on the right-hand side, taking as much
            room as possible.
        Stack the heading boxes, the buttons, radiobuttons and a
            label in the top-left corner.
        """
        self.top['menu'] = self.menu
        self.pack(expand=True, fill=Tk.BOTH)
        self.buttonframe.pack(side=Tk.LEFT)
        self.textframe.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        row = 0
        for heading in self.headings:
            heading.grid(row=row, column=0, columnspan=2, sticky=Tk.N)
            row += 1
        for i, button in enumerate(self.buttons):
            button.grid(row=row, column=i)
        row += 1
        for radio in self.radios:
            radio.grid(row=row, column=0, columnspan=2)
            row += 1
        for textbox in self.textboxes:
            textbox.pack(side=Tk.TOP, expand=True, fill=Tk.BOTH)
            row += 1
        self.infolabel.grid(row=row, column=0, columnspan=2)
        self.blanklabel.grid(row=row+1, column=0, columnspan=2)

    def scroll_headings(self, event):
        """
        Respond to PageUp / PageDown by changing headings, moving
            through the hierarchy.
        :param event (Event): which entry box received the KeyPress
        :param level (int): the level of the hierarchy that is being
            traversed.
        """
        heading = event.widget
        level = self.headings.index(heading) + self.root.level + 1
        direction = 1 if event.keysym == 'Next' else -1
        # ascend hierarchy until correct level
        while self.entry.level > level:
            try:
                self.entry = self.entry.parent
            except AttributeError:
                break
        # traverse hierarchy sideways
        if self.entry.level == level:
            with ignored(IndexError):
                self.entry = self.entry.sister(direction)
        # descend hierarchy until correct level
        while self.entry.level < level:
            try:
                self.entry = self.entry.children[0]
            except IndexError:
                break
        for heading_ in self.headings[level - self.root.level - 1:]:
            heading_.delete(0, Tk.END)
        heading.insert(Tk.INSERT, self.entry.name)
        return 'break'

    def enter_headings(self, event):
        """
        Go to the next heading, or load the entry
        """
        level = self.headings.index(event.widget)
        try:
            self.headings[level + 1].focus_set()
        except IndexError:
            self.load()
        return 'break'

    def go_to_heading(self, event=None):
        """
        Move focus to the heading textbox, and select all the text therein
        """
        with ignored(IndexError):
            heading = self.headings[0]
            heading.focus_set()
            heading.select_range(0, Tk.END)
        return 'break'

    def change_language(self, event=None):
        """
        Change the entry language to whatever is in the StringVar 'self.language'
        """
        self.translator = Translator(self.language.get())
        return 'break'

    def previous_window(self, event):
        textbox = self.textboxes[(self.textboxes.index(event.widget) - 1)]
        textbox.focus_set()
        self.update_wordcount(widget=textbox)
        return 'break'

    def next_window(self, event):
        try:
            textbox = self.textboxes[(self.textboxes.index(event.widget) + 1)]
        except IndexError:
            textbox = self.textboxes[0]
        textbox.focus_set()
        self.update_wordcount(widget=textbox)
        return 'break'

    def site_open(self, event=None):
        """
        Loop until a valid file is passed back, or user cancels
        """
        filename = fd.askopenfilename(filetypes=[('Sm\xe9agol File', '*.smg')], title='Open Site')
        if filename:
            try:
                with open(filename) as site:
                    sections = site.read().split('#')
                for section in sections:
                    try:
                        header, config = section.split('\n', 1)
                    except ValueError:
                        continue
                    if header == 'site':
                        self.site = self.make_site_from_config(config)
                        self.reset()
                    elif header == 'editor':
                        self.links = self.get_linkadder_from_config(config)
                    else:
                        raise SyntaxError
            except SyntaxError:
                self.site_open()
        return 'break'

    def make_site_from_config(self, config):
        details = {}
        properties = config.splitlines()
        for property_ in properties:
            with ignored(ValueError):
                key, value = property_.split(': ')
                details[key] = value
        files = dict(source='source', template='template', markdown='markdown',
                     searchjson='searchjson')
        for file_ in files.keys():
            with ignored(KeyError):
                files[file_] = details.pop(file_)
        details['files'] = Files(**files)
        return Site(**details)

    def get_linkadder_from_config(self, config):
        """
        Create an AddRemoveLinks instance based on a given configuration file

        :param config: (str) The appropriate section of a configuration file
        """
        properties = config.splitlines()
        possible_adders = filter(lambda x: x.owner not in ['site', 'file'], editor_properties)
        link_adders = []
        for property_ in properties:
            config_adder = property_.split(': ')
            link_adders.append(self.create_linkadder(possible_adders, config_adder))
        return AddRemoveLinks(link_adders)

    def create_linkadder(self, possible_adders, config_adder):
        """
        Create an instance of a Link Adder

        :param possible_adders: (Property[]) the editor properties that
            correspond to LinkAdders
        :param config_adder: (tuple) a (key, value) pair from a config. file
        """
        try:
            key, value = config_adder
        except ValueError:
            (key, ), value = config_adder, None
        adder = filter(lambda x: x.property == key, possible_adders)
        adder = adder[0].owner() if value is None else adder[0].owner(value)
        return adder

    def reset(self, event=None):
        """
        Reset the program.
        """
        self.entry = self.root = self.site.root
        self.clear_interface()

    def clear_interface(self):
        for heading in self.headings:
            heading.delete(0, Tk.END)
        for textbox in self.textboxes:
            textbox.delete(1.0, Tk.END)
        self.information.set('')
        self.go_to_heading()

    def site_save(self, event=None):
        filename = fd.asksaveasfilename(
                filetypes=[('Sm\xe9agol File', '*.smg')],
                title='Save Site', defaultextension='.smg')
        if filename:
            details = self.editor_configuration
            with open(filename, 'w') as site:
                site.write(details)
        return 'break'

    @property
    def editor_configuration(self):
        site_config = editor_config = ''
        details = self.site.details
        adders = self.links.details
        for property_ in editor_properties:
            if property_.owner in ['site', 'file']:
                site_config += '{0}: {1}\n'.format(property_.property,
                        details[property_.property])
            elif property_.property in adders.keys():
                if adders[property_.property] != '':
                    editor_config += '{0}: {1}\n'.format(property_.property, adders[property_.property])
                else:
                    editor_config += property_.property + '\n'
        return '#site\n{0}\n#editor\n{1}'.format(site_config, editor_config)

    def site_properties(self, event=None):
        """
        Pass current site details to a new Properties Window, and then
            re-create the Site with the new values and renew the Links
        """
        properties_window = PropertiesWindow(self.current_properties())
        self.wait_window(properties_window)
        self.site = Site(**properties_window.site_values)
        self.links = AddRemoveLinks(properties_window.link_values)
        self.entry = self.site.root

    def current_properties(self):
        """
        Match detail dictionaries with properties list, and return current
                properties to place in properties window
        """
        current = []

        details = self.site.details
        details.update(self.links.details)

        for property_ in editor_properties:
            try:
                current.append((1, details[property_.property]))
            except KeyError:
                current.append((0, ''))
        return current

    def site_publish(self, event=None):
        """
        Publish every page in the Site using the Site's own method
        """
        for _ in self.site.publish():
            pass

    def load(self, event=None):
        """
        Find entry, manipulate entry to fit boxes, place in boxes.
        """
        self.entry = self.find_entry(map(lambda x: x.get(), self.headings))
        texts = self.prepare_entry(self.entry)
        self.display(texts)
        self.save_text.set('Save')
        return 'break'

    def find_entry(self, headings):
        """
        Find the current entry based on what is in the heading boxes.
        This is the default method - other Editor programs may override this.
        Subroutine of self.load().
        :param headings (str[]): the texts from the heading boxes
        :return (Page):
        """
        entry = self.site.root
        with ignored(KeyError):
            for heading in headings:
                entry = entry[heading]
        return entry

    def prepare_entry(self, entry):
        """
        Manipulate text taken from a single Page to suit a textbox.

        Default method, other Editors will override this.
        :param entry (Page): A Page instance carrying text.
        :param return (str):
        :called by: Editor.load()
        """
        text = entry.content
        text = remove_datestamp(text)
        with conversion(self.links, 'remove_links') as converter:
            text = converter(text)
        with conversion(self.markdown, 'to_markdown') as converter:
            text = converter(text)
        return [text]

    def display(self, texts):
        for text, textbox in zip(texts, self.textboxes):
            textbox.delete(1.0, Tk.END)
            textbox.insert(1.0, text)
            textbox.edit_modified(False)
        else:   # set focus on final textbox
            textbox.focus_set()
            self.update_wordcount(widget=textbox)
        with ignored(AttributeError):
            if self.entry.content == '':
                self.initial_content

    def save(self, event=None):
        """
        Take text from box, manipulate to fit datafile, put in datafile, publish appropriate Pages.
        """
        for textbox in self.textboxes:
            textbox.edit_modified(False)
        self.save_text.set('Save')
        texts = map(self.get_text, self.textboxes)
        if self.entry:
            self.prepare_texts(texts)
        self.publish(self.entry, self.site)
        return 'break'

    @staticmethod
    def get_text(textbox):
        """
        Retrieves text from textbox.
        Default method - may be overriden by descendant classes.
        """
        return str(textbox.get(1.0, Tk.END + '-1c'))

    def prepare_texts(self, texts):
        """
        Modify entry with manipulated texts.
        Subroutine of self.save().
        Overrides parent method.
        :param texts (str[]): the texts to be manipulated and inserted.
        :param return (Nothing):
        """
        text = ''.join(texts)
        if not text:
            self.entry.delete_htmlfile()
            self.entry.remove_from_hierarchy()
            self.reset()
        else:
            text = self.convert_texts(text, self.entry)
            # remove duplicate linebreaks
            text = re.sub(r'\n\n+', '\n', text)
            self.entry.content = text

    def convert_texts(self, text, entry):
        """
        Run conversions over text
        """
        with conversion(self.markdown, 'to_markup') as converter:
            text = converter(text)
        with conversion(self.links, 'add_links') as converter:
            text = converter(text, entry, self.site)
        text = add_datestamp(text)
        return text

    @staticmethod
    def publish(entry, site):
        """
        Put entry contents into datafile, publish appropriate Pages.
        This is the default method - other Editor programs may override this.
        Subroutine of self.save()
        :param entry (Page):
        :return (nothing):
        """
        if entry:
            entry.publish(site.template)
        if site:
            site.modify_source()
            site.update_json()

    def edit_text_changed(self, event):
        """
        Notify the user that the edittext has been changed.
        Activates after each keypress.
        Deactivates after a save or a load action.
        """
        self.update_wordcount(event)
        if event.widget.edit_modified():
            self.save_text.set('*Save')

    def update_wordcount(self, event=None, widget=None):
        if event is not None:
            widget = event.widget
        text = widget.get(1.0, Tk.END)
        self.information.set(str(text.count(' ') + text.count('\n') - text.count(' | ')))

    @staticmethod
    def select_all(event):
        event.widget.tag_add('sel', '1.0', 'end')
        return 'break'

    @staticmethod
    def insert_characters(textbox, before, after=''):
        """
        Insert given text into a Text textbox, either around an
        insertion cursor or selected text, and move the cursor
        to the appropriate place.
        :param textbox (Tkinter Text): The Text into which the
        given text is to be inserted.
        :param before (str): The text to be inserted before the
        insertion counter, or before the selected text.
        :param after (str): The text to be inserted after the
        insertion cursor, or after the selected text.
        """
        try:
            text = textbox.get(Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.delete(Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.insert(Tk.INSERT, before + text + after)
        except Tk.TclError:
            textbox.insert(Tk.INSERT, before + after)
            textbox.mark_set(Tk.INSERT, Tk.INSERT + '-{0}c'.format(len(after)))

    def insert_formatting(self, event, tag):
        """
        Insert markdown for tags, and place insertion point between
        them.
        """
        with conversion(self.markdown, 'find_formatting') as converter:
            self.insert_characters(event.widget, *converter(tag))

    def bold(self, event):
        """
        Insert markdown for bold tags, and place insertion point between them.
        """
        self.insert_formatting(event, 'strong')
        return 'break'

    def italic(self, event):
        """
        Insert markdown for italic tags, and place insertion point between them.
        """
        self.insert_formatting(event, 'em')
        return 'break'

    def small_caps(self, event):
        """
        Insert markdown for small-caps tags, and place insertion point between them.
        """
        self.insert_formatting(event, 'small-caps')
        return 'break'

    def add_link(self, event):
        self.insert_formatting(event, 'link')
        return 'break'

    def insert_pipe(self, event):
        self.insert_characters(event.widget, ' | ')
        return 'break'

    def backspace_word(self, event):
        widget = event.widget
        get = widget.get
        delete = widget.delete
        if get(Tk.INSERT + '-1c') in '.,;:?! ':
            delete(Tk.INSERT + '-2c wordstart', Tk.INSERT)
        elif get(Tk.INSERT) in ' ':
            delete(Tk.INSERT + '-1c wordstart -1c', Tk.INSERT)
        else:
            delete(Tk.INSERT + '-1c wordstart', Tk.INSERT)
        self.update_wordcount(event)
        return 'break'

    def delete_word(self, event):
        widget = event.widget
        get = widget.get
        delete = widget.delete
        if get(Tk.INSERT + '-1c') in ' .,;:?!\n' or widget.compare(Tk.INSERT, '==', '1.0'):
            delete(Tk.INSERT, Tk.INSERT + ' wordend +1c')
        elif get(Tk.INSERT) == ' ':
            delete(Tk.INSERT, Tk.INSERT + '+1c wordend')
        elif get(Tk.INSERT) in '.,;:?!':
            delete(Tk.INSERT, Tk.INSERT + '+1c')
        else:
            delete(Tk.INSERT, Tk.INSERT + ' wordend')
        self.update_wordcount(event)
        return 'break'

    def markdown_open(self, event=None):
        web.open_new_tab(self.markdown.filename)

    def markdown_load(self, event=None):
        filename = fd.askopenfilename(
        filetypes=[('Sm\xe9agol Markdown File', '*.mkd')],
        title='Load Markdown')
        if filename:
            try:
                texts = map(self.get_text, self.textboxes)
                texts = map(self.markdown.to_markup, texts)
                self.markdown = Markdown(filename)
                texts = map(self.markdown.to_markdown, texts)
                for text, textbox in zip(texts, self.textboxes):
                    textbox.delete(1.0, Tk.END)
                    textbox.insert(1.0, text)
            except IndexError:
                mb.showerror('Invalid File', 'Please select a valid *.mkd file.')

    def markdown_refresh(self, event=None):
        try:
            texts = map(self.get, self.textboxes)
            texts = map(self.markdown.to_markup, texts)
            self.markdown.refresh()
            texts = map(self.markdown.to_markdown, texts)
            for text, textbox in texts, self.textboxes:
                textbox.delete(1.0, Tk.END)
                textbox.insert(1.0, text)
            self.information.set('Markdown Refreshed!')
        except AttributeError:
            self.information.set('No Markdown Found')
        return 'break'

    @property
    def menu_commands(self):
        return [('Site', [('Open', self.site_open),
                        ('Save', self.site_save),
                        ('P_roperties', self.site_properties),
                        ('Publish All', self.site_publish)]),
                ('Markdown', [('Load', self.markdown_load),
                              ('Refresh', self.markdown_refresh),
                              ('Open as _Html', self.markdown_open)]
                              )]

    @property
    def heading_commands(self):
        return [(['<Prior>', '<Next>'], self.scroll_headings),
                (['<Return>'], self.enter_headings)]

    @property
    def radio_settings(self):
        if self.widgets.radios == 'languages':
            return self.translator.languages.items()

    @property
    def button_commands(self):
        return self.load, self.save

    @property
    def textbox_commands(self):
        return [('<KeyPress>', self.edit_text_changed),
        ('<Control-a>', self.select_all),
        ('<Control-b>', self.bold),
        ('<Control-i>', self.italic),
        ('<Control-l>', self.load),
        ('<Control-k>', self.small_caps),
        ('<Control-m>', self.markdown_refresh),
        ('<Control-n>', self.add_link),
        ('<Control-o>', self.site_open),
        ('<Control-s>', self.save),
        ('<Control-BackSpace>', self.backspace_word),
        ('<Control-Delete>', self.delete_word),
        ('<Alt-d>', self.go_to_heading),
        ('<Tab>', self.next_window),
        ('<Shift-Tab>', self.previous_window),
        ('<KeyPress-|>', self.insert_pipe)]

    @property
    def initial_content(self):
        """
        Return the content to be placed in a textbox if the page is new
        """
        level = str(self.entry.level)
        name = self.entry.name
        return '{0}]{1}\n'.format(level, name)

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


if __name__ == '__main__':
    markdown = Markdown('c:/users/ryan/documents/tinellbianlanguages/'
                                        'grammarstoryreplacements.mkd')
    links = AddRemoveLinks([ExternalDictionary()])
    app = Editor(site=Grammar(), markdown=markdown, links=links)
    app.master.title('Page Editor')
    app.mainloop()
