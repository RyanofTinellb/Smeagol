import os
import json
from .page import Page
from smeagol.translation import Markdown, Translator
from smeagol.utils import *

def increment(lst, by):
    lst = [x + by for x in lst]
    return lst

markdown = Markdown()

class Site:
    def __init__(self, destination=None, name=None, files=None):
        self.name = name
        self.files = files or dict(
            source='', template_file='', wordlist='',
            wholepage=dict(file='', template=''),
            search=dict(index='', template='', page='', template404='', page404='')
        )
        self.setup_templates()
        self.destination = destination
        self.change_destination()
        self.load_site()

    def setup_templates(self):
        templates = (
            (self.template_file, 'template', TemplateFileNotFoundError),
            (self.wholepage_template, 'wholepage', WholepageTemplateFileNotFoundError),
            (self.search_template, 'search', SearchTemplateFileNotFoundError),
            (self.search_template404, 'search404', Search404TemplateFileNotFoundError)
        )
        for template in templates:
            self._template(*template)

    def _template(self, filename, attr, Error):
        template = ''
        if filename:
            try:
                with open(filename, encoding='utf-8') as template:
                    template = template.read()
            except FileNotFoundError:
                raise Error
        setattr(self, attr, template)

    def refresh_template(self, new_template):
        if new_template and self.template_file:
            with ignored(IOError):
                with open(self.template_file, 'w', encoding='utf-8') as template:
                    template.write(new_template)
        self.template = new_template

    def load_site(self):
        tree = dict(name=self.name)
        if self.source:
            try:
                with open(self.source, encoding='utf-8') as source:
                    tree = json.load(source)
            except FileNotFoundError:
                raise SourceFileNotFoundError
        self.tree = tree

    def __repr__(self):
        return (f'Site(destination="{self.destination}", '
                f'name="{self.name}", '
                f'source="{self.source}", '
                f'template="{self.template_file}", '
                f'searchindex="{self.searchindex})"')

    def __getattr__(self, attr):
        if attr in {'source', 'template_file', 'wordlist'}:
            try:
                return self.files[attr]
            except KeyError:
                self.files[attr] = ''
                return ''
        elif attr.startswith('wholepage_') or attr.startswith('search_'):
            attr, sub = attr.split('_')
            while True:
                try:
                    return self.files[attr][sub]
                except KeyError:
                    try:
                        self.files[attr][sub] = ''
                    except KeyError:
                        self.files[attr] = {sub: ''}
                else:
                    break
        else:
            return getattr(super(Site, self), attr)

    def __setattr__(self, attr, value):
        if attr in {'source', 'template_file', 'wordlist'}:
            self.files[attr] = value
        elif attr.startswith('wholepage_') or attr.startswith('search_'):
            attr, sub = attr.split('_')
            self.files[attr][sub] = value
        elif attr == 'destination':
            super(Site, self).__setattr__(attr, value)
            self.change_destination()
        else:
            super(Site, self).__setattr__(attr, value)

    def change_destination(self):
        if self.destination:
            destination = self.destination
            with ignored(os.error):
                os.makedirs(self.destination)
            os.chdir(self.destination)

    def __iter__(self):
        self.current = None
        return self

    def __next__(self):
        # changed this behaviour because it's better with Page objects
        # may need to change back if something needs the node object
            # itself.
        try:
            self.current = self.current.next()
        except AttributeError:
            self.current = Page(self.tree, [])
        except IndexError:
            self.__iter__()
            raise StopIteration
        return self.current
    
    @property
    def all_pages(self):
        node = self.root
        while True:
            yield node
            try:
                node = node.next()
            except IndexError:
                return

    def __getitem__(self, entry):
        page = Page(self.tree, [])
        count = 0
        try:
            while page.name != entry != count:
                page = page.successor
                count += 1
        except IndexError:
            raise KeyError(entry)
        return page

    @property
    def root(self):
        return self[0]

    def refresh_flatnames(self):
        for page in self.all_pages:
            page.refresh_flatname()

    def remove_flatnames(self):
        for page in self.all_pages:
            page.remove_flatname()

    def publish(self):
        pages = 0
        errors = 0
        errorstring = ''
        for page in self.all_pages:
            try:
                page.publish(template=self.template)
            except Exception as err:
                errorstring += f'{err} Error in {page.name}\n'
                errors += 1
            else:
                pages += 1
        self.update_searchindex()
        self.update_source()
        return '{4} page{5} printed to {6}\n{0}{1} error{2}\n{3}'.format(
                errorstring,
                errors,
                '' if errors == 1 else 's',
                '-' * 10,
                pages,
                '' if pages == 1 else 's',
                os.getcwd()
            )

    def update_source(self):
        dump(self.tree, self.source)

    def update_searchindex(self):
        dump(self.analysis, self.search_index)

    @property
    def analysis(self):
        words = {}
        sentences = []
        urls = []
        names = []
        for page_number, entry in enumerate(self.all_pages):
            base = len(sentences)
            analysis = entry.analysis
            new_words = analysis['words']
            sentences += analysis['sentences']
            urls.append(entry.link)
            names.append(buyCaps(entry.name))
            for word, line_numbers in new_words.items():
                line_numbers = increment(line_numbers, by=base)
                locations = {str(page_number): line_numbers}
                try:
                    words[word].update(locations)
                except KeyError:
                    words[word] = locations
        return dict(terms=words,
                    sentences=sentences,
                    urls=urls,
                    names=names)
