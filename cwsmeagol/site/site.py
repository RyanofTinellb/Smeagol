import os
import json
from page import Page
from cwsmeagol.translation import Markdown, Translator
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
            template = ''
        self.template_file, self.template = self.template, template

    def load_site(self):
        if self.source:
            with open(self.source) as source:
                self.tree = json.load(source)
        else:
            self.tree = dict(
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
            return missing_attribute(Site, self, attr)

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
        self.current = Page(self.tree, [])
        return self

    def next(self):
        try:
            self.current.next()
        except IndexError:
            self.__iter__()
            raise StopIteration
        return self.current.find()

    def __getitem__(self, entry):
        page = Page(self.tree, [])
        count = 0
        try:
            while page.name != entry != count:
                page.next()
                count += 1
        except IndexError:
            raise KeyError(entry)
        return page

    @property
    def root(self):
        return self[0]

    def refresh_flatnames(self):
        for page in self:
            page.refresh_flatname()

    def refresh_hyperlinks(self):
        for page in self:
            page.refresh_hyperlink()

    def publish(self):
        errors = 0
        errorstring = ''
        for page in self:
            try:
                dump(page.publish(template=self.template), page.link)
            except:
                errorstring += 'Error in {0}\n'.format(page.name)
                errors += 1
        self.update_searchindex()
        self.update_source()
        return '{0}{1} error{2}\n{3}'.format(
                errorstring,
                errors,
                '' if errors == 1 else 's',
                '-' * 10
            )

    def update_source(self):
        dump(self.tree, self.source)

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
            analysis = page.analysis
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
