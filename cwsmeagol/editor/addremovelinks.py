class AddRemoveLinks:
    def __init__(self, link_adders):
        """
        Allow for the removal of all links, and addition of specific
            links to Smeagol pages

        :param link_adders: (obj[]) a list of link adder instances
        """
        self.link_adders = link_adders
        self.details = dict(map(self.get_details, link_adders))

    @staticmethod
    def get_details(adder):
        adder_name = adder.name
        try:
            adder_filename = adder.filename
        except AttributeError:
            adder_filename = ''
        return (adder_name, adder_filename)

    def add_links(self, text, entry, site):
        for link_adder in self.link_adders:
            text = link_adder.add_links(text, entry, site)
        return text

    def remove_links(self, text):
        # external links to the dictionary - leaves as links
        text = re.sub('<a href="http://dictionary.tinellb.com/.*?">(.*?)</a>', r'<link>\1</link>', text)
        # version links - removes entire span
        text = re.sub(r'<span class="version.*?</span>', '', text)
        # internal links
        text = re.sub(r'<a href=\"(?!http).*?\">(.*?)</a>', r'<link>\1</link>', text)
        # protect phonology links from subsequent line
        text = re.sub(r'<a( href=\"http://grammar.*?phonology.*?</a>)', r'<b\1', text)
        # external links to the grammar guide, except phonology
        text = re.sub(r'<a href=\"http://grammar.*?\">(.*?)</a>', r'\1', text)
        # un-protect phonology
        text = re.sub(r'<b( href=\"http://grammar.*?phonology.*?</a>)', r'<a\1', text)
        return text

class ExternalDictionary:
    def add_links(self, text, entry, site):
        """
        Replaces text of the form <link>Blah</link> with a hyperlink to the
            dictionary entry 'Blah' on the Tinellbian languages dictionary site.
        """
        links = set(re.sub(r'.*?<link>(.*?)</link>.*?', r'\1@', text.replace('\n', '')).split(r'@')[:-1])
        if entry is not site.root:
            language = urlform(entry.ancestors[1].name)
        for link in links:
            url = urlform(link, site.markdown)
            initial = re.sub(r'.*?(\w).*', r'\1', url)
            with ignored(KeyError):
                if entry is not site.root:
                    text = text.replace('<link>' + link + '</link>',
                        '<a href="http://dictionary.tinellb.com/' + initial +
                            '/' + url + '.html#' + language + '">' + link + '</a>')
                else:
                    text = text.replace('<link>' + link + '</link>',
                        '<a href="' + url + '/index.html">' + link + '</a>')
        return text

    @property
    def name(self):
        return 'externaldictionary'

class InternalStory:
    def add_links(self, text, entry, site):
        """
        Add version links to the each paragraph of the text

        :param entry: (Page)
        :param text: (str)
        :return: (str)
        """
        if entry.name is None:
            return ''
        paragraphs = text.splitlines()
        version = entry.elders.index(entry.ancestors[1])
        for uid, paragraph in enumerate(paragraphs[1:], start=1):
            if paragraph == '<span class="stars">*&nbsp;&nbsp;&nbsp;&nbsp;*&nbsp;&nbsp;&nbsp;&nbsp;*</span>':
                pass
            elif version == 4:
                 paragraph = '&id=' + paragraphs[uid].replace(' | [r]', '&vlinks= | [r]')
            elif version == 3:
                paragraph = '[t]&id=' + re.sub(r'(?= \| \[r\]<div class=\"literal\">)', '&vlinks=', paragraphs[uid][3:])
            else:
                paragraph = '&id=' + paragraphs[uid] + '&vlinks='
            paragraphs[uid] = self._version_links(paragraph, version, entry, uid)
        return '\n'.join(paragraphs)

    @staticmethod
    def _version_links(paragraph, index, entry, uid):
        """
        Adds version link information to a paragraph and its cousins

        :param paragraph (str[]):
        :param index (int):
        :param entry (Page):
        :return (nothing):
        """
        links = ''
        anchor = '<span class="version-anchor" aria-hidden="true" id="{0}"></span>'.format(str(uid))
        categories = [node.name for node in entry.elders]
        cousins = entry.cousins
        for i, (cousin, category) in enumerate(zip(cousins, categories)):
            if index != i and cousin.name is not None:
                links += cousins[index].hyperlink(cousin, category, fragment='#'+str(uid)) + '&nbsp;'
        links = '<span class="version-links" aria-hidden="true">{0}</span>'.format(links)
        return paragraph.replace('&id=', anchor).replace('&vlinks=', links)

    @property
    def name(self):
        return 'internalstory'

class InternalDictionary:
    """
    Replace particular words in parts of speech with links to grammar.tinellb.com
    """
    def add_links(self, text, entry, site):
        links = set(re.sub(r'.*?<link>(.*?)</link>.*?', r'\1>', text.replace('\n', '')).split(r'>')[:-1])
        for link in links:
            with ignored(KeyError):
                lower_link = re.sub(r'^&#x294;', r'&rsquo;', link).lower()
                text = text.replace('<link>' + link + '</link>', entry.hyperlink(site[lower_link], link))
        return text

    @property
    def name(self):
        return 'internaldictionary'

class ExternalGrammar:
    """
    Replace given words in parts of speech with external URLs.
    :param filename (str): filename to get replacements from.
    """
    def __init__(self, filename):
        self.languages, self.words, self.urls = [], [], []
        self.filename = filename
        with open(filename) as replacements:
            replacements = replacements.read()
        for line in replacements.splitlines():
            if line.startswith('&'):
                site = line[1:]
            elif line.startswith('#'):
                language = line[1:]
                site += urlform(language)
            else:
                word, url = line.split()
                self.languages.append(language)
                self.words.append(word)
                self.urls.append(site + url)

    def add_links(self, text, entry, site):
        """
        Add links to text, from
        :precondition: text is a dictionary entry in Smeagol markdown.
        """
        current_language = ''
        for language, word, url in zip(self.languages, self.words, self.urls):
            page = ''
            url = r'<a href="{0}">{1}</a>'.format(url, word)
            for line in text.splitlines():
                if line.startswith('[3]'):
                    current_language = line[len('[3]'):]
                elif word in line and url not in line and current_language == language:
                    line = re.sub(r'(\[6\].*?)\b' + word + r'\b(.*?<)', r'\1' + url + r'\2', line)
                page += line + '\n'
            text = page
        return text

    @property
    def name(self):
        return 'externalgrammar'
