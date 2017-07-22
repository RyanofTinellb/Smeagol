import Tkinter as Tk
import os
import thread
from Smeagol import *
from Translation import *


class EditPage(Tk.Frame):
    def __init__(self, directories, datafiles, sites, markdowns, master=None):
        Tk.Frame.__init__(self, master)
        self.sitename = Tk.StringVar()
        self.sitename.set('grammar')
        self.directories = directories
        os.chdir(self.decide(directories))
        self.datafiles = datafiles
        self.datafile = self.decide(datafiles)
        self.sites = sites
        self.site = self.decide(sites)
        self.markdowns = markdowns
        self.markdown = self.decide(markdowns)
        self.entry = self.site.root
        self.headings = []
        self.grammar_button = None
        self.story_button = None
        self.load_button = None
        self.save_button = None
        self.save_text = Tk.StringVar()
        self.save_text.set('Save')
        self.number_of_words = Tk.StringVar()
        self.edit_text = Tk.Text(self, height=24, width=114, font=('Corbel', '14'), wrap=Tk.WORD, undo=True)
        self.word_count = Tk.Label(self, textvariable=self.number_of_words)
        self.grammar_button = Tk.Radiobutton(self, text='Grammar', variable=self.sitename, value='grammar',
                                             command=self.change_site)
        self.story_button = Tk.Radiobutton(self, text='Story', variable=self.sitename, value='story',
                                           command=self.change_site)
        self.grid()
        self.top = self.winfo_toplevel()
        self.top.state('zoomed')
        self.create_widgets()

    def create_widgets(self):
        for i in range(3):
            heading = Tk.Entry(self, width=20)
            heading.grid(sticky=Tk.NE, row=i, column=1)

            def handler(event, self=self, i=i):
                return self.scroll_headings(event, i)
            heading.bind('<Prior>', handler)
            heading.bind('<Next>', handler)
            self.headings.append(heading)
        self.headings[0].bind('<Return>', self.insert_chapter)
        self.headings[1].bind('<Return>', self.insert_heading)
        self.headings[2].bind('<Return>', self.load)
        self.load_button = Tk.Button(self, text='Load', width=10, command=self.load)
        self.load_button.grid(row=0, column=2, sticky=Tk.NW)
        self.save_button = Tk.Button(self, textvariable=self.save_text, width=10, command=self.save)
        self.save_button.grid(row=1, column=2, sticky=Tk.NW)
        self.word_count.grid(row=2, column=6)
        self.grammar_button.grid(row=2, column=2, sticky=Tk.W)
        self.story_button.grid(row=2, column=3, sticky=Tk.W)
        self.grammar_button.select()
        self.edit_text.bind('<KeyPress>', self.edit_text_changed)
        self.edit_text.bind('<Control-BackSpace>', self.backspace_word)
        self.edit_text.bind('<Control-Delete>', self.delete_word)
        self.edit_text.bind('<Control-a>', self.select_all)
        self.edit_text.bind('<Control-b>', self.bold)
        self.edit_text.bind('<Control-i>', self.italic)
        self.edit_text.bind('<Control-k>', self.small_caps)
        self.edit_text.bind('<Control-m>', self.refresh_markdown)
        self.edit_text.bind('<Control-r>', self.load)
        self.edit_text.bind('<Control-s>', self.save)
        self.edit_text.bind('<Control-t>', self.table)
        self.edit_text.bind('<KeyPress-|>', self.insert_pipe)
        self.edit_text.grid(column=2, columnspan=150)
        self.number_of_words.set('')
        self.headings[0].focus_set()

    def decide(self, variable):
        try:
            return variable[self.sitename.get()]
        except (TypeError, AttributeError, ValueError):
            return variable

    def refresh_markdown(self, event=None):
        """
        Re-open replacements page.
        """
        self.markdown.refresh()
        self.number_of_words.set('Markdown Refreshed!')
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
            try:
                self.entry = self.entry.sister(direction)
            except IndexError:
                pass
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

    def select_all(self, event=None):
        self.edit_text.tag_add('sel', '1.0', 'end')
        return 'break'

    def change_site(self, event=None):
        site = self.sitename.get()
        if self.site is None or site != self.sitename:
            for heading in self.headings:
                heading.delete(0, Tk.END)
            self.edit_text.delete(1.0, Tk.END)
            os.chdir(self.decide(self.directories))
            self.datafile = self.decide(self.datafiles)
            self.site = self.decide(self.sites)
            self.markdown = self.decide(self.markdowns)
            self.entry = self.site.root
            self.headings[0].focus_set()
        return 'break'

    def insert_pipe(self, event=None):
        self.edit_text.insert(Tk.INSERT, ' | ')
        return 'break'

    def table(self, event=None):
        """
        Insert markdown for table, and place insertion point between them.
        """
        self.edit_text.insert(Tk.INSERT, '[t]\n[/t]')
        self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + '-5c')
        return 'break'

    def bold(self, event=None):
        """
        Insert markdown for bold tags, and place insertion point between them.
        """
        self.edit_text.insert(Tk.INSERT, '[[]]')
        self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + '-2c')
        return 'break'

    def italic(self, event=None):
        """
        Insert markdown for italic tags, and place insertion point between them.
        """
        self.edit_text.insert(Tk.INSERT, '(())')
        self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + '-2c')
        return 'break'

    def small_caps(self, event=None):
        """
        Insert markdown for small-cap tags, and place insertion point between them.
        """
        self.edit_text.insert(Tk.INSERT, '<<>>')
        self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + '-2c')
        return 'break'

    def insert_chapter(self, event):
        self.headings[1].focus_set()
        return 'break'

    def insert_heading(self, event=None):
        self.headings[2].focus_set()
        return 'break'

    def delete_word(self, event=None):
        if self.edit_text.get(Tk.INSERT + '-1c') in ' .,;:?!':
            self.edit_text.delete(Tk.INSERT, Tk.INSERT + ' wordend +1c')
        elif self.edit_text.get(Tk.INSERT) == ' ':
            self.edit_text.delete(Tk.INSERT, Tk.INSERT + '+1c wordend')
        elif self.edit_text.get(Tk.INSERT) in '.,;:?!':
            self.edit_text.delete(Tk.INSERT, Tk.INSERT + '+1c')
        else:
            self.edit_text.delete(Tk.INSERT, Tk.INSERT + ' wordend')
        self.update_wordcount()
        return 'break'

    def backspace_word(self, event=None):
        if self.edit_text.get(Tk.INSERT + '-1c') in '.,;:?!':
            self.edit_text.delete(Tk.INSERT + '-1c wordstart', Tk.INSERT)
        else:
            self.edit_text.delete(Tk.INSERT + '-1c wordstart -1c', Tk.INSERT)
        self.update_wordcount()
        return 'break'

    def update_wordcount(self, event=None):
        text = self.edit_text.get(1.0, Tk.END)
        self.number_of_words.set(str(text.count(' ') + text.count('\n')))

    def edit_text_changed(self, event=None):
        self.update_wordcount()
        if self.edit_text.edit_modified():
            self.save_text.set('*Save')

    def load(self, event=None):
        # descend hierarchy in correct direction
        self.entry = self.site
        for heading in self.headings:
            try:
                self.entry = self.entry[heading.get()]
            except KeyError:
                pass
        self.edit_text.delete(1.0, Tk.END)
        if self.entry is not self.site:
            entry = self.markdown.to_markdown(self.entry.content)
            self.edit_text.insert(1.0, entry)
            self.edit_text.focus_set()
            self.edit_text.edit_modified(False)
            self.save_text.set('Save')
        else:
            self.entry = self.site.root
            self.edit_text.insert(1.0, 'That page does not exist. Create a new page by appending to an old one.')
            self.headings[1].focus_set()
        self.update_wordcount()
        return 'break'

    def save(self, event=None):
        self.save_text.set('Save')
        self.update_wordcount()
        self.entry.content = self.markdown.to_markup(str(self.edit_text.get(1.0, Tk.END)))
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
        return 'break'

app = EditPage(directories={'grammar': 'c:/users/ryan/documents/tinellbianlanguages/grammar',
                            'story': 'c:/users/ryan/documents/tinellbianlanguages/thecoelacanthquartet'},
                    datafiles='data.txt',
                    sites={'grammar': Grammar(), 'story': Story()},
                    markdowns=Markdown('../grammarstoryreplacements.html'))
app.master.title('Edit Page')
app.mainloop()
