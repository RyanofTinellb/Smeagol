from Smeagol import Page
from Translation import Markdown
import re

class d2gReplace():
    """
    Replace given words in parts of speech with URLs.
    :param genre (str): either 'd2g' or 'g2d', to signify which way the hyperlinks go.
    :param filename (str): filename to do replacements in.
    """
    def __init__(self, filename=None):
        self.languages, self.words, self.urls = [], [], []
        self.filename = filename
        for language in ['High Lulani']:
            for word, url in [
                    ('noun', 'highlulani/morphology/nouns.html'),
                    ('verb', 'highlulani/morphology/verbs.html'),
                    ('adverb', 'highlulani/morphology/adverbs.html'),
                    ('adposition', 'highlulani/morphology/adpositions.html'),
                    ('element', 'highlulani/apocrypha/elements.html'),
                    ('numeral', 'highlulani/apocrypha/numbers.html'),
                    ('conjunction', 'highlulani/morphology/conjunctions.html'),
                    ('pronoun', 'highlulani/morphology/nouns.html#pronouns'),
                    ('coordinating', 'highlulani/morphology/conjunctions.html#coordinatingconjunctions'),
                    ('intransitive', 'highlulani/morphology/verbs.html#transitivity'),
                    ('suffix', 'highlulani/morphology/suffixes.html'),
                    ('proper', 'highlulani/morphology/nouns.html#propernouns'),
                    ('auxiliary', 'highlulani/morphology/auxiliaries.html')
                    ]:
                    self.languages.append(language)
                    self.words.append(word)
                    self.urls.append('http://grammar.tinellb.com/' + url)

    def replace(self, text):
        """
        Replaces appropriate words with links in text.
        :precondition: text is a dictionary entry in Dictionary markdown.
        """
        for language, word, url in zip(self.languages, self.words, self.urls):
            page = ''
            url = r'<a href=\"{0}\">{1}</a>'.format(url, word)
            for line in text.splitlines():
                if line.startswith('[3]'):
                    current_language = line[len('[3]'):]
                elif word in line and url not in line and current_language == language:
                    line = re.sub(r'(\[6\].*?)\b' + word + r'\b(.*?{{)', r'\1' + url + r'\2', line)
                page += line + '\n'
            text = page
        return text

    def replace_all(self):
        """
        Replaces all appropriate words in a textfile with hyperlinks to grammar.tinellb.com.
        :precondition: text is a dictionary file in Smeagol markup.
        """
        if self.filename is None:
            raise TypeError('Please supply a filename')
        with open(self.filename) as source:
            text = source.read()
        for language, word, url in zip(self.languages, self.words, self.urls):
            page = ''
            url = r'<a href="{0}">{1}</a>'.format(url, word)
            for line in text.splitlines():
                if line.startswith('[3]'):
                    current_language = line[len('[3]'):]
                elif word in line and url not in line and current_language == language:
                    line = re.sub(r'(\[6\].*?)\b' + word + r'\b(.*?<div )', r'\1' + url + r'\2', line)
                page += line + '\n'
            text = page
        with open(self.filename, 'w') as destination:
            destination.write(text)

class g2dReplace():
    def __init__(self, filename=None):
        self.filename = filename

    def replace(self, text):
        """
        Replaces appropriate words in text with links to dictionary.tinellb.com.
        :precondition: text is a grammar page with text in GrammarStory markdown.
        """


    def replace_all(self):
        """
        Replaces all appropriate words in a textfile with hyperlinks to grammar.tinellb.com.
        :precondition: text is a grammar text in Smeagol-type markup. <strong> tags surround links.
        """
        with open(self.filename) as source:
            page = source.read()
        chunk = section = page[page.find('[1]High Lulani'):page.find('[1]Appendices')]
        links = set(re.sub(r'.*?<strong>(.*?)</strong>.*?', r'\1@', section.replace('\n', '')).split(r'@')[:-1])
        for link in links:
            url = Page(link, markdown=Markdown('c:/users/ryan/documents/tinellbianlanguages/replacements.html')).urlform
            initial = re.sub(r'.*?(\w).*', r'\1', url)
            try:
                section = section.replace('<strong>' + link + '</strong>',
                '<a href="http://dictionary.tinellb.com/' + initial + '/' + url + '.html">' + link + '</a>')
            except KeyError:
                pass
        with open(self.filename, 'w') as destination:
            destination.write(page.replace(chunk, section))
