import re

class ReplaceLinks():
    """
    Replace given words in parts of speech with URLs.
    :param filename (str): filename to do replacements in.
    :param language (str):
    :param word (str): word to be replaced.
    :param url (str): link with which to replace word.
    """
    def __init__(self, filename, language, word, url):
        url = '<a href="{0}">{1}</a>'.format(url, word)
        page = ''
        with open(filename) as text:
            for line in text:
                if line.startswith('[3]'):
                    current_language = line[len('[3]'):-1]
                    page += line
                elif word in line and url not in line and current_language == language:
                    page += re.sub(r'(\[6\].*?)\b' + word + r'\b(.*?<div)', r'\1' + url + r'\2', line)
                else:
                    page += line
        with open(filename, 'w') as text:
            text.write(page)


ReplaceLinks('c:/users/ryan/documents/tinellbianlanguages/dictionary/data.txt',
             'High Lulani',
             'noun',
             'http://grammar.tinellb.com/highlulani/morphology/nouns.html')
