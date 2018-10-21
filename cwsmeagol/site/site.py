import os
from page import Page
from cwsmeagol.editor.files import Files
from text_analysis import Analysis
from cwsmeagol.translation import *
from cwsmeagol.utils import *

class Site(object):
    """
    A hierarchy of Pages
    """
    def __init__(self, destination=None, name=None, files=None):
        """
        :param destination (str): the full path where the Site is to be located
        :param name (str): human-readable name of the Site
        :param files (Files):
        """
        # initialize attributes and utility classes
        self.name = name
        self.files = files or Files()
        self.destination = destination
        self.change_destination()
        self.create_site()

    def create_site(self):
        self.current = None
        self.length = 0
        if not self.files.source:
            self.root = Page(self.name)
            return

        with open(self.files.source) as source:
            source = source.read().split('-' * 50)

        # create page on appropriate level of hierarchy, with name taken from the source file
        node = self.root = Page(self.name, content=source[0])
        for page in source[1:]:
            previous = node
            level = int(page[0])
            name = re.search(r'(?<=\]).*', page).group(0)
            while level != node.level + 1:
                # climb back up the hierarchy to the appropriate level
                node = node.parent
            node = self.add_node(name, node, page[2:])
            self.length += 1

    def __repr__(self):
        return ('Site(destination="{0}", '
                'name="{1}", '
                'source="{2}", '
                'template="{3}", '
                'searchjson="{4}"').format(
                self.destination,
                self.name,
                self.files.source,
                self.files.template_file,
                self.files.searchjson)

    @property
    def source(self):
        return self.files.source

    @property
    def template(self):
        return self.files.template

    @property
    def searchjson(self):
        return self.files.searchjson

    def change_destination(self):
        if self.destination:
            destination = self.destination
            with ignored(os.error):
                os.makedirs(destination)
            try:
                os.chdir(destination)
            except os.error:
                win32api.MessageBox(0, 'That does not seem to be a valid destination. Please try again.', 'Unable to Create destination')
                return
            os.chdir(destination)

    def __str__(self):
        """
        Join each non-empty page, and remove the first character
        :rtype: str
        :class: Site
        """
        return ''.join([str(page) for page in self if page.content])

    def __len__(self):
        """
        :return: the number of pages in the Site
        :rtype: int
        :class: Site
        """
        return self.length

    def __iter__(self):
        """
        :class: Site
        """
        return self

    def next(self):
        """
        Set the next Page as the current Page
        :return: new current Page
        :rtype: Page
        :class: Site
        """
        if self.current is None:
            self.current = self.root
            return self.root
        try:
            self.current = self.current.next_node
        except IndexError:
            self.current = None
            raise StopIteration
        return self.current

    def previous(self):
        """
        Set the previous Page as the current Page, assuming the old Page has an instance variable 'previous'
        :return: new current Page
        :rtype: Page
        :class: Site
        """
        self.current = self.current.previous
        return self.current

    def reset(self):
        """
        Reset the iterator
        :class: Site
        """
        self.current = None

    def __getitem__(self, page):
        """
        Search the Site for a particular page
        :param page (str): the name of the page being searched for
        :param page (int): the index number of the page being searched for, where 0 is the root
        :rtype: Page
        :class: Site
        """
        node = self.root
        try:
            page = int(page)
            for _ in range(page):
                node = node.next_node
        # 'item' is a string
        except ValueError:
            while node.name != page and page != '':
                try:
                    node = node.next_node
                except IndexError:
                    raise KeyError(page)
        return node

    def add_node(self, name, parent, content):
        """
        Add a Page to the appropriate location in the Site, and return that Page
        If another Page exists at the same point with the same name, a '2' is appended to the name
        :param name (str): human-readable name of the Page
        :param parent (Page): the parent node of the new Page
        :param content (str): the content of the Page, including the header line
        :return (Page): the Page that was added
        :class: Site
        """
        child = Page(name, parent, content)
        if child not in parent.children:
            parent.children.append(child)
        else:
            return self.add_node(name + '2', parent, content)
        return child

    def publish(self):
        """
        Create / modify all .html files, and create search JSON file.
        :class: Site
        """
        errors = 0
        errorstring = ''
        for page in self:
            try:
                page.publish(self.template)
            except:
                errorstring += 'Error in ' + page.name + '\n'
                errors += 1
        self.update_json()
        self.modify_source()
        return '{2}{0} error{3}\n{1}'.format(
                errors,
                '-' * 10,
                errorstring,
                '' if errors == 1 else 's'
            )

    def modify_source(self):
        """
        Write the Site's contents to the sourcefile.
        """
        if str(self) != '':
            with open(self.source, 'w') as source:
                source.write(str(self))

    def update_json(self):
        if self.searchjson:
            with open(self.searchjson, 'w') as f:
                f.write(str(self.analyse()))

    def analyse(self):
        """
        Analyse the Site for searchable content
        :rtype: Analysis
        :class: Site
        """
        words = {}
        sentences = []
        urls = []
        names = []
        markdown = Markdown()
        for page_number, entry in enumerate(self):
            # line numbers in each Page are incremented by the current total number of sentences
            base = len(sentences)
            # analyse the Page
            analysis = entry.analyse(markdown)
            # add results to appropriate lists and dictionaries
            new_words = analysis.words
            sentences += analysis.sentences
            urls.append(entry.link(extend=False))
            names.append(buyCaps(entry.name))
            for word in new_words:
                # increment line numbers by base
                # use str(page_number) because search.js relies on that
                locations = {str(page_number): map(lambda x: x + base, new_words[word])}
                try:
                    words[word].update(locations)
                except KeyError:
                    words[word] = locations
        return Analysis(words, sentences, urls, names)
