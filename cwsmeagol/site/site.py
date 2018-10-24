import os
import json
import node
import page
from cwsmeagol.translation import *
from cwsmeagol.utils import *

class Site(object):
    def __init__(self, destination=None, name=None, files=None):
        self.name = name
        self.files = files or dict(
            source='', template_file='', searchindex=''
        )
        self.setup_template()
        self.destination = destination
        self.change_destination()
        self.load_site()

    def setup_template(self):
        try:
            with open(self.template) as template:
                template = template.read()
        except IOError:
            template = None
        self.template_file, self.template = self.template, template

    def load_site(self):
        if self.source:
            with open(self.source) as source:
                self.root = json.load(source)
        else:
            self.root = dict(
                date=str(datetime.today()),
                text='',
                hyperlink='index.html',
                children=[],
                name=self.name)

    def __repr__(self):
        return ('Site(destination="{0}", '
                'name="{1}", '
                'source="{2}", '
                'template="{3}", '
                'searchindex="{4}"').format(
                self.destination,
                self.name,
                self.source,
                self.template_file,
                self.searchindex)

    def __getattr__(self, attr):
        if attr in {'source', 'template', 'template_file', 'searchindex'}:
            return self.files[attr]
        else:
            raise AttributeError("{0} instance has no attribute '{1}'".format(
                    self.__class__.__name__, attr))

    def __setattr__(self, attr, value):
        if attr in {'source', 'template', 'template_file', 'searchindex'}:
            self.files[attr] = value
        else:
            super(Site, self).__setattr__(attr, value)

    def change_destination(self):
        if self.destination:
            destination = self.destination
            with ignored(os.error):
                os.makedirs(destination)
            try:
                os.chdir(destination)
            except os.error:
                win32api.MessageBox(0, ('That does not seem to be a valid'
                        ' destination. Please try again.'),
                    'Unable to Create Destination')
                return
            os.chdir(destination)

    def __iter__(self):
        self.current = None
        return self

    def next(self):
        if self.current is None:
            self.current = []
            return self.root
        try:
            node.next(self.root, self.current)
        except IndexError:
            self.current = None
            raise StopIteration
        return node.find(self.root, self.current)

    def __getitem__(self, page):
        location = []
        count = 0
        try:
            while node.find(self.root, location)['name'] != page != count:
                node.next(self.root, location)
                count += 1
        except IndexError:
            raise KeyError(page)
        return node.find(self.root, location)

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
        with open(self.source, 'w') as source:
            json.dump(self.root, source, indent=2)

    def update_searchindex(self):
        if self.searchindex:
            with open(self.searchindex, 'w') as searchindex:
                json.dump(self.analyse(), searchindex, indent=2)

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
            new_words = analysis['words']
            sentences += analysis['sentences']
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
        return dict(terms=words,
                    sentences=sentences,
                    urls=urls,
                    names=names)
