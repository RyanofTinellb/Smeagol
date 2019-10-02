import json
import os

from ..translation import Markdown, Translator
from .templates import Templates
from .files import Files
from ..utils import *

from .page import Page

markdown = Markdown()

class Site:
    def __init__(self, destination=None, name=None, files=None):
        self.destination = destination
        self.name = name
        self.files = files or Files()
        if isinstance(self.files, dict):
            self.files = Files(self.files)
        self.load_site()
        self.setup_templates()
    
    def setup_templates(self):
        templates = (
            (self.template_file, 'template', TemplateFileNotFoundError),
            (self.wholepage_template, 'wholepage',
                WholepageTemplateFileNotFoundError),
            (self.search_template, 'search', SearchTemplateFileNotFoundError),
            (self.search_template404, 'search404',
                Search404TemplateFileNotFoundError)
        )
        for name, text in Templates(templates, self.sections).items():
            setattr(self, name, text)

    def load_site(self):
        if self.source:
            try:
                with open(self.source, encoding='utf-8') as source:
                    tree = json.load(source)
            except FileNotFoundError:
                raise SourceFileNotFoundError
        self.tree = tree

    def __getattr__(self, attr):
        if attr == 'files':
            return
        try:
            return getattr(self.files, attr)
        except AttributeError:
            return getattr(super(), attr)
    
    def __setattr__(self, attr, value):
        if attr == 'destination':
            setattr(Site, attr, value)
            self.change_destination()
        else:
            setattr(Site, attr, value)

    def change_destination(self):
        if self.destination:
            destination = self.destination
            with ignored(os.error):
                os.makedirs(self.destination)
            os.chdir(self.destination)

    def __iter__(self):
        return self.iterator

    @property
    def iterator(self):
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
        for page in self:
            page.refresh_flatname()

    def remove_flatnames(self):
        for page in self:
            page.flatname = ''

    def publish(self):
        pages = 0
        errors = 0
        errorstring = ''
        for page in self:
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
    
    @asynca
    def save_wholepage(self):
        contents = map(lambda x: x.wholepage, self)
        contents = '\n'.join(filter(None, contents))
        
        root = self.root
        root.update_date()
        
        page = root.html(self.wholepage)
        page = page.replace('{whole-contents}', contents)
        page = re.sub(r'<li class="normal">(.*?)</li>',
                        r'<li><a href="index.html">\1</a></li>', page)
        dumps(page, self.wholepage_file)

    @asynca
    def save_search_pages(self):
        for template in (
                (self.search, self.search_page),
                (self.search404, self.search_page404)):
            self._search(*template)

    def _search(self, template, filename):
        page = re.sub('{(.*?): (.*?)}', self.root.section_replace, template)
        page = re.sub(
            r'<li class="normal">(.*?)</li>',
            r'<li><a href="index.html">\1</a></li>',
            page
        )
        if filename is self.search_page404:
            page = re.sub(r'(href|src)="/*', r'\1="/', page)
        dumps(page, filename)

    @property
    def analysis(self):
        words = {}
        sentences = []
        urls = []
        names = []
        for page_number, entry in enumerate(self):
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
