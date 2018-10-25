import os
import json
import node
import page
from cwsmeagol.translation import Markdown, Translator
from cwsmeagol.utils import *

def dump(dictionary, filename):
    if filename:
        with open(filename, 'w') as f:
            json.dump(dictionary, f, indent=2)

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

    def publish(self):
        errors = 0
        errorstring = ''
        for node in self:
            try:
                page.publish(self.root, self.current, self.template)
            except:
                errorstring += 'Error in ' + node['name'] + '\n'
                errors += 1
        self.update_searchindex()
        self.update_source()
        return '{2}{0} error{3}\n{1}'.format(
                errors,
                '-' * 10,
                errorstring,
                '' if errors == 1 else 's'
            )

    def update_source(self):
        dump(self.root, self.source)

    def update_searchindex(self):
        dump(self.analysis, self.searchindex)

    @property
    def analysis(self):
        words = {}
        sentences = []
        urls = []
        names = []
        markdown = Markdown()
        for page_number, entry in enumerate(self):
            # line numbers in each Page are incremented by the current total number of sentences
            base = len(sentences)
            # analyse the Page
            analysis = page.analyse('['.join(entry['text']))
            # add results to appropriate lists and dictionaries
            new_words = analysis['words']
            sentences += analysis['sentences']
            urls.append(entry['hyperlink'])
            names.append(buyCaps(entry['name']))
            for word, line_numbers in new_words.iteritems():
                # increment line numbers by base
                # use str(page_number) because search.js relies on that
                locations = {str(page_number):
                        [line_number + base for line_number in line_numbers]}
                try:
                    words[word].update(locations)
                except KeyError:
                    words[word] = locations
        return dict(terms=words,
                    sentences=sentences,
                    urls=urls,
                    names=names)
