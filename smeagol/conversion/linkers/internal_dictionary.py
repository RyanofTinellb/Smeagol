import re
from smeagol.utilities import filesystem as fs
from smeagol.conversion.translator import Translator

class InternalDictionary:
    def __init__(self, resource=None, wordlist=None, translator=None):
        self.adder = {'InternalDictionary': resource}
        self.translator = translator or Translator()
        self.wordlist_file = wordlist
        self.wordlist_setup()

    def add_links(self, text, entry):
        """
        Add links of the form
            '<a href="../b/blah.html#highlulani">blah</a>'
        """
        self.language = 'also'
        lang = '1]'  # language marker
        output = []
        regex = r'<{0}>(.*?)</{0}>'.format('[bl]ink')
        for line in text.split('['):
            if lang in line:
                self.language = re.sub(lang + '(.*?)\n', r'\1', line)
            output.append(re.sub(regex, self._link, line))
        return '['.join(output)

    def _link(self, text):
        word = text.group(1).split(':')
        tr = self.translator
        language = utils.urlform(self.language if len(
            word) == 1 else tr.select(word[0]))
        link = utils.urlform(utils.sellCaps(word[-1]))
        initial = utils.page_initial(link)
        return '<a href="../{0}/{1}.html#{2}">{3}</a>'.format(
            initial, link, language, word[-1])

    def remove_links(self, text, entry):
        self.language = 'also'
        lang = '1]'  # language marker
        output = []
        regex = r'<a href="(?:\w+\.html|\.\./.*?)#(.*?)">(.*?)</a>'
        for line in text.split('['):
            if lang in line:
                self.language = re.sub(lang + '(.*?)\n', r'\1', line)
            output.append(re.sub(regex, self._unlink, line))
        return '['.join(output)

    def _unlink(self, regex):
        tr = self.translator
        language, link = [regex.group(x) for x in range(1, 3)]
        tag = 'link' if not self.wordlist or link in self.wordlist else 'bink'
        if language == utils.urlform(self.language):
            return r'<{0}>{1}</{0}>'.format(tag, link)
        return r'<{0}>{1}:{2}</{0}>'.format(tag, tr.encode(language), link)

    def wordlist_setup(self):
        wordlist = fs.load_json(self.wordlist_file)
        self.wordlist = [word['t'] for word in wordlist]

    def refresh(self, text=''):
        self.wordlist_setup()
