from smeagol import *
import Tkinter as Tk
import tkFileDialog as fd
import tkMessageBox as mb

WidgetAmounts = namedtuple('WidgetAmounts', ['headings', 'textboxes', 'radios'])

class Editor(Tk.Frame, object):
    """
    Base class for DictionaryEditor and StoryEditor
    """

    def __init__(self, directories=None, datafiles=None, sites=None, markdowns=None, replacelinks=None, kind=None, widgets=WidgetAmounts(headings=3, textboxes=1, radios=2), font=('Corbel', '14')):
        """
        Initialise an instance of the Editor class.
        :param kind (str): i.e.: 'grammar', 'dictionary', 'story'.
        :param directory (str):
        :param widgets (WidgetAmounts): number of each of headings, textboxes, radiobuttons to create.
        """
        super(Editor, self).__init__(None)
        # initialise initial variables
        self.directories = directories
        self.datafiles = datafiles
        self.sites = sites
        self.markdowns = markdowns
        self.replacelinks = replacelinks
        self.kind = Tk.StringVar()
        self.kind.set(kind)
        self.font = font
        with ignored(TypeError):
            os.chdir(choose(self.kind, self.directories))

        # initialise instance variables
        self.buttonframe, self.textframe = Tk.Frame(self), Tk.Frame(self)
        self.headings, self.radios, self.texts = [], [], []
        self.buttons = self.load_button = self.save_button = self.label = self.entry = None
        self.save_text, self.language = Tk.StringVar(), Tk.StringVar()
        self.save_text.set('Save')
        self.translator = Translator()

        # headings
        self.headings = self.create_headings(self.buttonframe, widgets.headings)

        # radio buttons
        try:
            self.radios = self.create_radios(self.buttonframe, widgets.radios)
        except TypeError:
            if widgets.radios == 'languages':
                self.radios = self.create_radios(self.buttonframe, self.translator.number)

        # labels
        self.blanklabel = Tk.Label(self.buttonframe, height=1000) # enough height to push all other widgets to the top of the window.
        self.infolabel, self.information = self.create_label(self.buttonframe)

        # load and save buttons
        commands = self.load, self.save
        self.buttons = self.create_buttons(self.buttonframe, commands, self.save_text)
        self.load_button, self.save_button = self.buttons

        # textboxes
        try:
            font = self.font
        except AttributeError:
            font = ('Calibri', 17)
        self.textboxes = self.create_textboxes(self.textframe, widgets.textboxes, self.textbox_commands, self.font)

        # window
        self.top = self.winfo_toplevel()
        self.menu = self.create_menu(self.top)
        self.create_window()
        self.top.state('zoomed')
        self.clear_interface()

        # from old SiteEditor
        self.site = choose(self.kind, self.sites)
        self.markdown = markdowns
        self.datafile = datafiles
        self.entry = self.site.root
        self.grammar_radio, self.story_radio = self.radios
        self.heading = self.headings[0]
        self.edit_text = self.textboxes[0]
        self.textbox = self.textboxes[0]
        self.configure_widgets()

# TODO: abstract this method:
            # pass in commands as arguments
            # make recursive
    def create_menu(self, master):
        """
        Create a menu.

        :param master: (widget)
        :returns: (widget)
        """
        menubar = Tk.Menu(master)
        submenu = Tk.Menu(menubar, tearoff=0)
        submenu.add_command(label='Open', command=self.editor_open, underline=0)
        submenu.bind('<KeyPress-f>', self.editor_open)
        menubar.add_cascade(label='File', menu=submenu)
        return menubar

# TODO: Use this method to open a new Site
    def editor_open(self, event=None):
        while True:
            filename = fd.askopenfilename(filetypes=[('Sm\xe9agol File', '*.smg')], title='Open Site')
            if filename:
                try:
                    with open(filename) as site:
                        site = site.read().replace('\n', ' ')
                    self.directories = eval(site.split(',')[0])
                    self.sites = eval('Site(' + site + ')')
                    self.change_site()
                    break
                except (IOError, SyntaxError):
                    mb.showerror('Invalid File', 'Please select a valid *.smg file.')
            else:
                break
        return 'break'

    def enter_headings(self, event):
        level = self.headings.index(event.widget)
        if level <= 1:
            self.headings[level + 1].focus_set()
        else:
            self.load()
        return 'break'

    def configure_widgets(self):
        for i, heading in enumerate(self.headings):

            def handler(event, self=self, i=i):
                return self.scroll_headings(event, i)
            heading.bind('<Prior>', handler)
            heading.bind('<Next>', handler)
            heading.bind('<Return>', self.enter_headings)
            heading.bind('<Up>', self.scroll_radios)
            heading.bind('<Down>', self.scroll_radios)
        self.textbox.bind('<Control-t>', self.table)
        self.grammar_radio.configure(text='Grammar', variable=self.kind, value='grammar', command=self.change_site)
        self.story_radio.configure(text='Story', variable=self.kind, value='story', command=self.change_site)

    def scroll_radios(self, event):
        if self.kind.get() == 'grammar':
            self.story_radio.select()
        else:
            self.grammar_radio.select()
        self.change_site()

    def table(self, event=None):
        """
        Insert markdown for table, and place insertion point between them.
        """
        self.textbox.insert(Tk.INSERT, '[t]\n[/t]')
        self.textbox.mark_set(Tk.INSERT, Tk.INSERT + '-5c')
        return 'break'

    def scroll_headings(self, event, level):
        """
        Respond to PageUp / PageDown by changing headings, moving through the hierarchy.
        :param event (Event): which entry box received the KeyPress
        :param level (int): the level of the hierarchy that is being traversed.
        """
        heading = self.headings[level]
        # bring
        level += 1
        direction = 1 if event.keysym == 'Next' else -1
        # traverse hierarchy sideways
        if self.entry.level == level:
            with ignored(IndexError):
                self.entry = self.entry.sister(direction)
        # ascend hierarchy until correct level
        while self.entry.level > level:
            try:
                self.entry = self.entry.parent
            except AttributeError:
                break
        # descend hierarchy until correct level
        while self.entry.level < level:
            try:
                self.entry = self.entry.children[0]
            except IndexError:
                break
        for k in range(level - 1, 3):
            self.headings[k].delete(0, Tk.END)
        heading.insert(Tk.INSERT, self.entry.name)
        return 'break'


    def change_site(self, event=None):
        with ignored(TypeError):
            os.chdir(choose(self.kind, self.directories))
        self.site = choose(self.kind, self.sites)
        self.entry = self.site.root
        self.clear_interface()

    def create_window(self):
        """
        Place all widgets in GUI window.
        Stack the textboxes on the right-hand side, taking as much room as possible.
        Stack the heading boxes, the buttons, radiobuttons and a label in the top-left corner.
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

    def clear_interface(self):
        for heading in self.headings:
            heading.delete(0, Tk.END)
        for textbox in self.textboxes:
            textbox.delete(1.0, Tk.END)
        self.information.set('')
        self.go_to_heading()

    def configure_language_radios(self):
        for radio, (code, language) in zip(self.radios, self.translator.languages.items()):
            radio.configure(text=language().name, variable=self.language, value=code, command=self.change_language)
        self.language.set(self.translator.languages.keys()[0])
        self.translator = Translator(self.language.get())

    def change_language(self, event=None):
        """
        Change the entry language to whatever is in the StringVar 'self.language'
        """
        self.translator = Translator(self.language.get())
        return 'break'

    @staticmethod
    def select_all(event):
        event.widget.tag_add('sel', '1.0', 'end')
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
        return [Tk.Button(master, text='Load', command=commands[0]),
        Tk.Button(master, command=commands[1], textvariable=save_variable)]

    @staticmethod
    def create_label(master):
        textvariable = Tk.StringVar()
        return Tk.Label(master, textvariable=textvariable), textvariable

    @staticmethod
    def create_radios(master, number):
        radios = []
        for _ in range(number):
            radio = Tk.Radiobutton(master)
            radios.append(radio)
        return radios

    @staticmethod
    def create_textboxes(master, number, commands=None, font=None):
        if not commands:
            commands = []
        if not font:
            font = ('Courier New', '15')
        textboxes = []
        for _ in range(number):
            textbox = Tk.Text(master, height=1, width=1, wrap=Tk.WORD, undo=True, font=font)
            for (key, command) in commands:
                textbox.bind(key, command)
            textboxes.append(textbox)
        return textboxes

    @staticmethod
    def insert_characters(textbox, before, after=''):
        """
        Insert given text into a Text textbox, either around an insertion cursor or selected text, and move the cursor to the appropriate place.
        :param textbox (Tkinter Text): The Text into which the given text is to be inserted.
        :param before (str): The text to be inserted before the insertion counter, or before the selected text.
        :param after (str): The text to be inserted after the insertion cursor, or after the selected text.
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
        Insert markdown for tags, and place insertion point between them.
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

    def load(self, event=None):
        """
        Find entry, manipulate entry to fit boxes, place in boxes.
        """
        self.entry = self.find_entry(map(lambda x: x.get(), self.headings))
        markdown = choose(self.kind, self.markdowns)
        self.display(self.prepare_entry(self.entry, markdown, self.kind.get()))
        return 'break'

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
                self.initial_content()

    def find_entry(self, headings):
        """
        Find the current entry based on what is in the heading boxes.
        This is the default method - other Editor programs will override this.
        Subroutine of self.load().
        :param headings (str[]): the texts from the heading boxes
        :return (Page):
        """
        entry = site = choose(self.kind, self.sites)
        with ignored(KeyError):
            for heading in headings:
                entry = entry[heading]
        return entry if entry is not site else (site.root if site else None)

    def save(self, event=None):
        """
        Take text from box, manipulate to fit datafile, put in datafile, publish appropriate Pages, update json.
        """
        # prepare save
        markdown = choose(self.kind, self.markdowns)
        site = choose(self.kind, self.sites)
        for textbox in self.textboxes:
            textbox.edit_modified(False)
        self.save_text.set('Save')

        texts = map(self.get_text, self.textboxes)

        with ignored(AttributeError):
            self.paragraphs[self.current_paragraph] = self.prepare_paragraph(self.entry, texts, self.markdown, self.translator, self.current_paragraph - 1)
            texts = self.paragraphs
        if self.entry:
            self.prepare_texts(self.entry, site, texts, markdown, self.replacelinks, kind=self.kind.get())
        self.publish(self.entry, site)
        return 'break'

    @staticmethod
    def get_text(textbox):
        """
        Retrieves text from textbox.
        Default method - may be overriden by descendant classes.
        """
        return str(textbox.get(1.0, Tk.END + '-1c'))

    @staticmethod
    def prepare_texts(entry, site, texts, markdown=None, replacelinks=None, uid=None, kind=None):
        """
        Modify entry with manipulated texts.
        Subroutine of self.save().
        Overrides parent method.
        :param entry (Page): the entry in the datafile to be modified.
        :param texts (str[]): the texts to be manipulated and inserted.
        :param markdown (Markdown): a Markdown instance to be applied to the texts. If None, the texts are not changed.
        :param return (Nothing):
        """
        with conversion(markdown, 'to_markup') as converter:
            text = ''.join(map(converter, texts))
        if kind == 'grammar':
            links = set(re.sub(r'.*?<link>(.*?)</link>.*?', r'\1@', text.replace('\n', '')).split(r'@')[:-1])
            matriarch = entry.ancestors[1].urlform
            for link in links:
                url = Page(link, markdown=site.markdown).urlform
                initial = re.sub(r'.*?(\w).*', r'\1', url)
                with ignored(KeyError):
                    text = text.replace('<link>' + link + '</link>',
                    '<a href="http://dictionary.tinellb.com/' + initial + '/' + url + '.html#' + matriarch + '">' + link + '</a>')
        elif kind == 'story':
            paragraphs = text.splitlines()
            index = entry.elders.index(entry.ancestors[1])
            for uid, paragraph in enumerate(paragraphs[1:]):
                if index == 4:
                     paragraph = '&id=' + paragraphs[uid+1].replace(' | [r]', '&vlinks= | [r]')
                elif index == 3:
                    paragraph = '[t]&id=' + re.sub(r'(?= \| \[r\]<div class=\"literal\">)', '&vlinks=', paragraphs[uid+1][3:])
                else:
                    paragraph = '&id=' + paragraphs[uid+1] + '&vlinks='
                paragraphs[uid+1] = add_version_links(paragraph, index, entry, uid)
            text = '\n'.join(paragraphs)
        entry.content = text

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
        self.information.set(str(text.count(' ') + text.count('\n') - text.count('|')))

    def next_window(self, event):
        try:
            textbox = self.textboxes[(self.textboxes.index(event.widget) + 1)]
        except IndexError:
            textbox = self.textboxes[0]
        textbox.focus_set()
        self.update_wordcount(widget=textbox)
        return 'break'

    def previous_window(self, event):
        textbox = self.textboxes[(self.textboxes.index(event.widget) - 1)]
        textbox.focus_set()
        self.update_wordcount(widget=textbox)
        return 'break'

    @staticmethod
    def prepare_entry(entry, markdown=None, kind=None):
        """
        Manipulate entry content to suit textboxes.
        Default method, other Editors will override this.
        :param entry (Page): A Page instance carrying text. Other Pages relative to this entry may also be accessed.
        :param markdown (Markdown): a Markdown instance to be applied to the contents of the entry. If None, the content is not changed.
        :param kind (str): i.e.: which kind of links should be removed, 'grammar', 'story'
        :param return (str[]):
        :called by: Editor.load()
        """
        if kind == 'grammar':
            text = re.sub('<a href="http://dictionary.tinellb.com/.*?">(.*?)</a>', r'<link>\1</link>', entry.content)
        elif kind == 'story':
            text = remove_version_links(entry.content)
        else:
            text = entry.content
        with conversion(markdown, 'to_markdown') as converter:
            return [converter(text)]

    def refresh_markdown(self, event=None):
        try:
            self.markdown.refresh()
            self.information.set('Markdown Refreshed!')
        except AttributeError:
            self.information.set('No Markdown Found')
        return 'break'

    @property
    def textbox_commands(self):
        return [('<KeyPress>', self.edit_text_changed),
        ('<Control-a>', self.select_all),
        ('<Control-b>', self.bold),
        ('<Control-i>', self.italic),
        ('<Control-l>', self.load),
        ('<Control-k>', self.small_caps),
        ('<Control-m>', self.refresh_markdown),
        ('<Control-n>', self.add_link),
        ('<Control-s>', self.save),
        ('<Control-BackSpace>', self.backspace_word),
        ('<Control-Delete>', self.delete_word),
        ('<Alt-d>', self.go_to_heading),
        ('<Tab>', self.next_window),
        ('<Shift-Tab>', self.previous_window),
        ('<KeyPress-|>', self.insert_pipe)]


def choose(kind, variables):
    """
    Return appropriate variable from a dictionary, or returns the variable itself if its not a dictionary.
    :param kind (Tk.StringVar): which variable to return.
    :param variables (Object{str, various}): a dictionary of {kind, variable} pairs.
    :param variables (Object): a single variable.
    """
    try:
        return variables[kind.get()]
    except (TypeError, AttributeError, ValueError, KeyError):
        return variables

def remove_version_links(text):
    """
    Remove the version link information from a paragraph.
    :precondition: text is in Smeagol markdown
    :param text (str): the paragraph to be cleaned.
    :return (str):
    """
    return re.sub(r'<span class="version.*?</span>', '', text)

def add_version_links(paragraph, index, entry, uid):
    """
    Adds version link information to a paragraph and its cousins
    :param paragraph (str[]):
    :param index (int):
    :param entry (Page):
    :return (nothing):
    """
    links = ''
    anchor = '<span class="version-anchor" id="{0}"></span>'.format(str(uid))
    categories = [node.name for node in entry.elders]
    cousins = entry.cousins
    for i, (cousin, category) in enumerate(zip(cousins, categories)):
        if index != i:
            links += cousins[index].hyperlink(cousin, category, fragment='#'+str(uid)) + '&nbsp;'
    links = '<span class="version-links">{0}</span>'.format(links)
    return paragraph.replace('&id=', anchor).replace('&vlinks=', links)


if __name__ == '__main__':
    app = Editor(directories={'grammar': 'c:/users/ryan/documents/tinellbianlanguages/grammar',
                                'story': 'c:/users/ryan/documents/tinellbianlanguages/thecoelacanthquartet'},
                        datafiles='data.txt',
                        sites={'grammar': Grammar(), 'story': Story()},
                        markdowns=Markdown('c:/users/ryan/documents/tinellbianlanguages/grammarstoryreplacements.mkd'),
                        kind='grammar')
    app.master.title('Page Editor')
    app.mainloop()
