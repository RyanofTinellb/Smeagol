from default_editor import *
import story_editor

class SiteEditor(Editor):
    def __init__(self, directories, datafiles, sites, markdowns, master=None):
        self.font = ('Corbel', '14')
        self.widgets = WidgetAmounts(headings=3, textboxes=1, radios=2)
        super(SiteEditor, self).__init__(directories=directories, datafiles=datafiles, sites=sites, markdowns=markdowns, kind='grammar')
        self.site = sites['grammar']
        self.markdown = markdowns
        self.datafile = datafiles
        self.entry = self.site.root

        # rename for readability
        self.grammar_radio, self.story_radio = self.radios
        self.textbox = self.textboxes[0]
        self.configure_widgets()

    def configure_widgets(self):
        for i, heading in enumerate(self.headings):

            def handler(event, self=self, i=i):
                return self.scroll_headings(event, i)
            heading.bind('<Prior>', handler)
            heading.bind('<Next>', handler)
            heading.bind('<Return>', self.enter_headings)
            heading.bind('<Up>', self.scroll_radios)
            heading.bind('<Down>', self.scroll_radios)
        self.textbox.bind('<Control-o>', self.refresh_site)
        self.textbox.bind('<Control-t>', self.table)
        self.grammar_radio.configure(text='Grammar', variable=self.kind, value='grammar', command=self.change_site)
        self.story_radio.configure(text='Story', variable=self.kind, value='story', command=self.change_site)

    def change_site(self, event=None):
        with ignored(TypeError):
            os.chdir(choose(self.kind, self.directories))
        self.site = choose(self.kind, self.sites)
        self.entry = self.site.root
        self.clear_interface()

    def refresh_site(self, event=None):
        self.site.refresh()
        self.load()
        self.information.set('Site Refreshed!')

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

    def enter_headings(self, event):
        level = self.headings.index(event.widget)
        if level <= 1:
            self.headings[level + 1].focus_set()
        else:
            self.load()
        return 'break'

    @staticmethod
    def prepare_entry(entry, markdown=None, kind=None):
        """
        Manipulate entry content to suit textboxes.
        Overrides parent method.
        :param entry (Page): A Page instance carrying text. Other Pages relative to this entry may also be accessed.
        :param markdown (Markdown): a Markdown instance to be applied to the contents of the entry. If None, the content is not changed.
        :param kind (str): i.e.: which kind of links should be removed, 'grammar', 'story'
        :param return (str[]):
        :called by: Editor.load()
        """
        if kind == 'grammar':
            text = re.sub('<a href="http://dictionary.tinellb.com/.*?">(.*?)</a>', r'<link>\1</link>', entry.content)
        elif kind == 'story':
            text = EditStory.remove_version_links(entry.content)
        else:
            text = entry.content
        with conversion(markdown, 'to_markdown') as converter:
            return [converter(text)]

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
                paragraphs[uid+1] = EditStory.add_version_links(paragraph, index, entry, uid)
            text = '\n'.join(paragraphs)
        entry.content = text
        with open('c:/users/ryan/desktop/data.txt', 'w') as f:
            f.write(text)

app = EditPage(directories={'grammar': 'c:/users/ryan/documents/tinellbianlanguages/grammar',
                            'story': 'c:/users/ryan/documents/tinellbianlanguages/thecoelacanthquartet'},
                    datafiles='data.txt',
                    sites={'grammar': Grammar(), 'story': Story()},
                    markdowns=Markdown('c:/users/ryan/documents/tinellbianlanguages/grammarstoryreplacements.html'))
app.master.title('Editor Page')
app.mainloop()
