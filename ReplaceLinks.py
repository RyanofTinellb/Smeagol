import re

class ReplaceLinks():
    """
    Replace given words in parts of speech with URLs.
    :param filename (str): filename to do replacements in.
    :param language (str):
    :param word (str): word to be replaced.
    :param url (str): link with which to replace word.
    """
    def __init__(self, filename):
        self.languages, self.words, self.urls = [], [], []
        for language in ['High Lulani']:
            for word, url in [
                    ('noun', 'http://grammar.tinellb.com/highlulani/morphology/nouns.html'),
                    ('verb', 'http://grammar.tinellb.com/highlulani/morphology/verbs.html'),
                    ('adverb', 'http://grammar.tinellb.com/highlulani/morphology/adverbs.html'),
                    ('adposition', 'http://grammar.tinellb.com/highlulani/morphology/adpositions.html'),
                    ('element', 'http://grammar.tinellb.com/highlulani/apocrypha/elements.html'),
                    ('numeral', 'http://grammar.tinellb.com/highlulani/apocrypha/numbers.html'),
                    ('conjunction', 'http://grammar.tinellb.com/highlulani/morphology/conjunctions.html'),
                    ]:
                    self.languages.append(language)
                    self.words.append(word)
                    self.urls.append(url)

    def replace(self, text):
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

    """Completely wrong order -- FIX!"""
    def replace_all(self):
        with open(self.filename) as text:
            text = text.read().splitlines()
        for language, word, url in zip(self.languages, self.words, self.urls):
            page = ''
            url = '<a href="{0}">{1}</a>'.format(url, word)
            for line in text:
                if line.startswith('[3]'):
                    current_language = line[len('[3]'):-1]
                    newline = line
                for language, word, url in zip(languages, words, urls):
                    if word in line and url not in line and current_language == language:
                        newline = re.sub(r'(\[6\].*?)\b' + word + r'\b(.*?<div)', r'\1' + url + r'\2', line)
                page += newline
            text = page
        with open(self.filename, 'w') as text:
            text.write(text)
