from Edit import *


class EditPage(Edit):
    def __init__(self, directories, datafiles, sites, markdowns, master=None):
        self.font = ('Corbel', '14')
        self.widgets = [3, 1, 2]
        Edit.__init__(self, directories=directories, datafiles=datafiles, sites=sites, markdowns=markdowns, kind='grammar')
        self.site = sites['grammar']
        self.markdown = markdowns
        self.datafile = datafiles
        self.entry = self.site.root
        self.textbox = self.textboxes[0]
        self.configure_widgets()

    def configure_widgets(self):
        for i, heading in enumerate(self.headings):

            def handler(event, self=self, i=i):
                return self.scroll_headings(event, i)
            heading.bind('<Prior>', handler)
            heading.bind('<Next>', handler)
        self.headings[0].bind('<Return>', self.insert_chapter)
        self.headings[1].bind('<Return>', self.insert_heading)
        self.headings[2].bind('<Return>', self.load)
        self.textbox.bind('<Control-o>', self.refresh_site)
        self.textbox.bind('<Control-t>', self.table)
        self.radios[0].configure(text='Grammar', variable=self.kind, value='grammar', command=self.change_site)
        self.radios[1].configure(text='Story', variable=self.kind, value='story', command=self.change_site)

    def change_site(self, event=None):
        self.change_directory(self.choose(self.kind, self.directories))
        self.clear_interface()

    def refresh_site(self, event=None):
        self.site.refresh()
        self.load()
        self.information.set('Site Refreshed!')

        # TODO: Ensure headings scroll correct site when site is changed.
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

    def table(self, event=None):
        """
        Insert markdown for table, and place insertion point between them.
        """
        self.textboxes[0].insert(Tk.INSERT, '[t]\n[/t]')
        self.textboxes[0].mark_set(Tk.INSERT, Tk.INSERT + '-5c')
        return 'break'

    def insert_chapter(self, event):
        self.headings[1].focus_set()
        return 'break'

    def insert_heading(self, event=None):
        self.headings[2].focus_set()
        return 'break'

    @staticmethod
    def prepare_entry(entry, markdown=None):
        """
        Manipulate entry content to suit textboxes.
        Subroutine of self.load()
        Overrides parent method.
        :param entry (Page): A Page instance carrying text. Other Pages relative to this entry may also be accessed.
        :param markdown (Markdown): a Markdown instance to be applied to the contents of the entry. If None, the content is not changed.
        :param return (str[]):
        """
        text = re.sub('<a href="http://dictionary.tinellb.com/.*?">(.*?)</a>', r'<link>\1</link>', entry.content)
        try:
            return [markdown.to_markdown(text)]
        except AttributeError:  # no markdown
            return [text] if text else ['']

    # superceded by parent method
    def save2(self, event=None):
        self.entry.content = self.markdown.to_markup(str(self.textboxes[0].get(1.0, Tk.END)))
        while self.entry.content[-2:] == '\n\n':
            self.entry.content = self.entry.content[:-1]
        # remove duplicate linebreaks
        self.entry.content = re.sub(r'\n\n+', '\n', self.entry.content)
        # update datestamp and publish.
        self.entry.content = self.markdown.to_markup(self.markdown.to_markdown(self.entry.content))
        if self.entry.content == '\n':
            self.entry.delete()
            self.entry.remove()
        else:

            self.entry.publish(self.site.template)
        entry = str(self.site)
        if entry:
            with open(self.datafile, 'w') as data:
                data.write(str(self.site))
        self.site.update_json()
        self.textboxes[0].edit_modified(False)
        return 'break'

    @staticmethod
    def prepare_texts(entry, site, texts, markdown=None, replacelinks=None):
        """
        Modify entry with manipulated texts.
        Subroutine of self.save().
        Overrides
        :param entry (Page): the entry in the datafile to be modified.
        :param texts (str[]): the texts to be manipulated and inserted.
        :param markdown (Markdown): a Markdown instance to be applied to the texts. If None, the texts are not changed.
        :param return (Nothing):
        """
        try:
            text = ''.join(map(markdown.to_markup, texts))
        except AttributeError:  # no markdown
            text = ''.join(texts)
        links = set(re.sub(r'.*?<link>(.*?)</link>.*?', r'\1@', text.replace('\n', '')).split(r'@')[:-1])
        matriarch = entry.ancestors()[1].urlform
        for link in links:
            url = Page(link, markdown=site.markdown).urlform
            initial = re.sub(r'.*?(\w).*', r'\1', url)
            with ignored(KeyError):
                text = text.replace('<link>' + link + '</link>',
                '<a href="http://dictionary.tinellb.com/' + initial + '/' + url + '.html#' + matriarch + '">' + link + '</a>')
        entry.content = text

app = EditPage(directories={'grammar': 'c:/users/ryan/documents/tinellbianlanguages/grammar',
                            'story': 'c:/users/ryan/documents/tinellbianlanguages/thecoelacanthquartet'},
                    datafiles='data.txt',
                    sites={'grammar': Grammar(), 'story': Story()},
                    markdowns=Markdown('c:/users/ryan/documents/tinellbianlanguages/grammarstoryreplacements.html'))
app.master.title('Edit Page')
app.mainloop()
