from smeagol_page import Page
from text_analysis import Analysis
from translation import *
import os

class Site:
    """
    A hierarchy of Pages

    Includes an override method for __setattr__()
    """
    def __init__(self, destination, name, source, template, markdown, searchjson, leaf_level):
        """
        :param destination (str): the full path where the Site is to be located
        :param name (str): human-readable name of the Site
        :param source (str): filename and extension of the source file, relative to destination
        :param template (str): filename and extension of the template for ordinary pages, relative to destination
        :param markdown (str): filename and extension of the markdown file, relative to destination
        :param leaf_level (int): the level of the lowermost pages in the hierarchy, where the root is at 0.

        :attribute template (Template): the template for ordinary pages
        :attribute markdown (Markdown): the conversion between markup and markdown for Page names.
        :attribute current (Page):
        :attribute root (Page): the root of the hierarchy
        """
        self.choose_dir(destination)
        # initialize attributes and utility classes
        self.details = dict(destination=destination,
                            name=name,
                            source=source,
                            template=template,
                            markdown=markdown,
                            searchjson=searchjson,
                            leaf_level=str(leaf_level))
        self.destination = destination
        self.name = name
        self.source = source
        self.template = template
        self.markdown = markdown
        self.searchjson = searchjson
        try:
            self.leaf_level = int(leaf_level)
        except ValueError:
            self.leaf_level = 1
        self.current = None
        self.length = 0

        # break source text into pages, with the splits on square brackets before numbers <= leaf_level
        with open(source) as source:
            source = source.read()
        split = re.compile(r'\[(?=[{0}])'.format(''.join(map(lambda x: str(x + 1), range(self.leaf_level)))))
        source = split.split(source)

        # create page on appropriate level of hierarchy, with name taken from the source file
        node = self.root = Page(name, content=source[0][1:], leaf_level=self.leaf_level, markdown=self.markdown)
        for page in source[1:]:
            previous = node
            level, name = re.split('[]\n]', page, 2)[:2]
            level = int(level)
            while level != node.level + 1:
                # climb back up the hierarchy to the appropriate level
                node = node.parent
            node = self.add_node(name, node, page, previous)
            self.length += 1

    def __setattr__(self, name, value):
        if name == 'template':
            with open(value) as template:
                self.__dict__[name] = template.read()
                self.__dict__[name + '_file'] = value
        elif name == 'markdown':
            self.__dict__[name] = Markdown(value)
        else:
            self.__dict__[name] = value

    def __repr__(self):
        return ('Site(destination="{0}", '
                'name="{1}", '
                'source="{2}", '
                'template="{3}", '
                'markdown="{4}", '
                'searchjson="{5}", '
                'leaf_level={6})').format(
                self.destination,
                self.name,
                self.source,
                self.template_file,
                self.markdown.filename,
                self.searchjson,
                str(self.leaf_level))

    def refresh(self):
        self.current = None
        self.length = 0
        node = self.root = Page(name, leaf_level=self.leaf_level, markdown=self.markdown)

        # break source text into pages, with the splits on square brackets before numbers <= leaf_level
        with open(self.source) as source:
            source = source.read()
        split = re.compile(r'\[(?=[{0}])'.format(''.join(map(lambda x: str(x + 1), range(self.leaf_level)))))
        source = split.split(source)

        # create page on appropriate level of hierarchy, with name taken from the self.source file
        # ignore first (empty) page
        for page in source[1:]:
            previous = node
            level, name = re.split('[]\n]', page, 2)[:2]
            level = int(level)
            while level != node.level + 1:
                # climb back up the hierarchy to the appropriate level
                node = node.parent
            node = self.add_node(name, node, page, previous)
            self.length += 1

    @staticmethod
    def choose_dir(destination):
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
        return ''.join([str(page) for page in self if str(page)])

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
            while node.name != page:
                try:
                    node = node.next_node
                except IndexError:
                    raise KeyError(page)
        return node

    def add_node(self, name, parent, content, previous):
        """
        Add a Page to the appropriate location in the Site, and return that Page
        If another Page exists at the same point with the same name, a '2' is appended to the name
        :param name (str): human-readable name of the Page
        :param parent (Page): the parent node of the new Page
        :param content (str): the content of the Page, including the header line
        :param previous (Page): the previous Page in the Site
        :return (Page): the Page that was added
        :class: Site
        """
        child = Page(name, parent, content, self.leaf_level, previous, self.markdown)
        if child not in parent.children:
            parent.children.append(child)
        else:
            return self.add_node(name + '2', parent, content, previous)
        return child

    def publish(self):
        """
        Create / modify all .html files, and create search JSON file.
        :class: Site
        """
        length = len(self)
        chunk = 3 if length > 1000 else 50
        progress = 1
        self.reset()
        for i, page in enumerate(self):
            page.publish(self.template)
            if i == int(progress * chunk * length / 100):
                yield str(progress * chunk) + '% Done'
                progress += 1
        self.update_json()
        self.modify_source()

    def modify_source(self):
        """
        Write the Site's contents to the sourcefile.
        """
        with open(self.source, 'w') as source:
            source.write(str(self))

    def update_json(self):
        with open(self.searchjson, 'w') as f:
            f.write(str(self.analyse()))

    def analyse(self):
        """
        Analyse the Site for searchable content
        :rtype: Analysis
        :class: Site
        """
        words, sentences, urls, names = {}, [], [], []
        for page_number, entry in enumerate(self):
            # line numbers in each Page are incremented by the current total number of sentences
            base = len(sentences)
            # analyse the Page
            analysis = entry.analyse(self.markdown)
            # add results to appropriate lists and dictionaries
            new_words = analysis.words
            sentences += analysis.sentences
            urls.append(entry.link(False))
            names.append(entry.name)
            for word in new_words:
                # increment line numbers by base
                # use str(page_number) because search.js relies on that
                locations = {str(page_number): map(lambda x: x + base, new_words[word])}
                try:
                    words[word].update(locations)
                except KeyError:
                    words[word] = locations
        return Analysis(words, sentences, urls, names)
