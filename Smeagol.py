import os
import re
import win32api

import Translation


class Site:
    def __init__(self, name, leaf_level=3, directory='c:/users/ryan/documents/tinellbianlanguages/'):
        os.chdir(directory + Page(name).url_form())
        self.source_file = 'data.txt'
        self.template_file = 'style.css'
        self.leaf_level = leaf_level
        self.current = None
        self.name = name
        self.root = node = Page(name, leaf_level=self.leaf_level)
        split = r'\[(?=[' + "".join(map(lambda x: str(x + 1), range(leaf_level))) + r'])'
        with open(self.source_file, 'r') as source:
            source = source.read()
        source = re.split(split, source)
        for page in source:
            previous = node
            try:
                level, heading = re.split('[]\n]', page, 2)[:2]
                level = int(level)
            except ValueError:
                continue
            while level != node.generation() + 1:
                node = node.parent
            node = self.add_node(heading, node, page, previous)

    def __str__(self):
        return ''.join([str(page) for page in self if str(page)])[1:]

    def __len__(self):
        counter = 0
        node = self.root
        while True:
            try:
                node = node.next_node()
                counter += 1
            except IndexError:
                return counter

    def __iter__(self):
        return self

    def __next__(self):
        self.next()

    def next(self):
        if self.current is None:
            self.current = self.root
            return self.root
        try:
            self.current = self.current.next_node()
        except IndexError:
            self.current = None
            raise StopIteration
        return self.current

    def reset(self):
        self.current = None

    def __getitem__(self, page):
        node = self.root
        try:
            page = int(page)
            for _ in range(page):
                node = node.next_node()
        # 'item' is a string
        except ValueError:
            while node.name != page:
                try:
                    node = node.next_node()
                except IndexError:
                    raise KeyError(page)
        return node

    def add_node(self, name, parent, content, previous):
        child = Page(name, parent, content, self.leaf_level, previous)
        if child not in parent.children:
            parent.children.append(child)
        else:
            self.add_node(name + '2', parent, content)
        return child

    def find_node(self, item):
        return self.find_node_iter(item, self.root)

    def find_node_iter(self, item, node):
        if len(item) == 0:
            return node
        else:
            for child in node.children:
                if child.url_form() == item[0]:
                    node = child
                    break
            else:
                raise IndexError('No such node "' + item[0].capitalize() + '" in ' + node.name)
            return self.find_node_iter(item[1:], node)

    def publish(self, destination=None, template=None, main_template=None):
        if destination:
            if re.search(r'[/\\]$', destination) is not None:
                destination += "/"
            destination += self.root.url_form()
        else:
            destination = 'c:/users/ryan/documents/tinellbianlanguages/' + self.root.url_form()
        try:
            os.makedirs(destination)
        except os.error:
            pass
        try:
            os.chdir(destination)
        except os.error:
            win32api.MessageBox(0, 'That does not seem to be a valid directory. Please try again.',
                                'Unable to Create Directory')
            return
        if template is None:
            template = Template('template.html')
        if main_template is None:
            main_template = Template('main_template.html')
        self.root.publish(main_template)
        self.previous = self.current
        self.next()
        for entry in self:
            entry.publish(template)
        analysis = self.analyse()
        string = str(analysis)
        with open('searching.json', 'w') as f:
            f.write(string)

    def analyse(self, markdown=None):
        if markdown is None:
            markdown = Translation.Markdown()
        wordlist = {}
        lines = []
        pages = []
        names = []
        for number, entry in enumerate(self):
            analysis = entry.analyse(markdown)
            words = analysis.wordlist
            line_number = len(lines)
            lines += analysis.lines
            names.append(entry.name)
            pages.append(entry.link(False))
            for word in words:
                line_numbers = map(lambda x: x + line_number, words[word])
                locations = {str(number): line_numbers}
                try:
                    wordlist[word].update(locations)
                except KeyError:
                    wordlist[word] = locations
        return Analysis(wordlist, lines, pages, names)


class Page:
    def __init__(self, name, parent=None, content="", leaf_level=3, previous=None):
        self.parent = parent
        self.name = name
        self.children = []
        self.leaf_level = leaf_level
        self.content = content
        self.previous = previous

    def __str__(self):
        return '[' + self.content

    def __eq__(self, other):
        try:
            if self.name == other.name:
                parent, other = self.parent, other.parent
                while True:
                    return parent == other
            else:
                return False
        except AttributeError:
            return self is other is None

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        alphabet = " aeiyuow'pbtdcjkgmnqlrfvszxh"
        try:
            if self.name == other.name:
                return False
        except AttributeError:
            return self is None is not other
        if self.flat_name().name == other.flat_name().name:
            return self.flat_name().score < other.flat_name().score
        for s, t in zip(self.flat_name().name, other.flat_name().name):
            if s != t:
                try:
                    return alphabet.index(s) < alphabet.index(t)
                except ValueError:
                    continue
        else:
            return len(self.flat_name().name) < len(other.flat_name().name)

    def __gt__(self, other):
        return not self <= other

    def __le__(self, other):
        return self < other or self.name == other.name

    def __ge__(self, other):
        return not self < other

    def flat_name(self):
        return self.FlatName(self.name)

    class FlatName:
        """
        'flattens' the name to only include letters aiu'pbtdcjkgmnqlrfsxh
        minigolf scoring rules: smallest number wins.
        """
        def __init__(self, name):
            alphabet = "aiu'pbtdcjkgmnqlrfsxh"
            score = 2
            double_letter = re.compile('([' + alphabet + r'])\1')
            self.score = 0
            self.name = Translation.Markdown().to_markdown(name)
            if re.match(r'\\-[aiu]', self.name):
                self.name = self.name.replace(r'\-', "'", 1)
                self.score = score ** 15
            elif self.name.startswith(r'\-'):
                self.name = self.name.replace(r'\-', "", 1)
                self.score = score ** 15
            while True:
                try:
                    index = re.search(double_letter, self.name).start()
                except AttributeError:
                    break
                self.name = re.sub(double_letter, r'\1', self.name, 1)
                self.score += score ** index

    def __getitem__(self, entry):
        try:
            entry = int(entry)
            return self.children[entry]
        except ValueError:
            for child in self.children:
                if child.name == entry:
                    return child
            else:
                raise KeyError('No such page ' + entry + 'in ' + self.name)

    def __hash__(self):
        return hash(self.name)

    def insert(self, index=None):
        try:
            self.parent.children.insert(index, self)
        except TypeError:
            for index, page in enumerate(self.parent.children):
                number = index
                if self <= page:
                    self.parent.children.insert(number, self)
                    break
            else:
                self.parent.children.append(self)
            return self

    def site(self):
        sites = {'Grammar': Grammar,
                 'Dictionary': Dictionary,
                 'The Coelacanth Quartet': Story}
        return sites[self.root().name]

    def delete(self):
        """Delete target node and all of its descendants"""
        self.parent.children.remove(self)

    def has_children(self):
        return len(self.children) > 0

    def root(self):
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    def elders(self):
        """Return the first generation of the current hierarchy"""
        return self.root().children

    def ancestors(self):
        node = self
        ancestry = []
        while node.parent is not None:
            node = node.parent
            ancestry.insert(0, node)
        return ancestry

    def generation(self):
        """
        Gives the generation number of the Page, with the root at zero.
        :rtype: int
        """
        return len(self.ancestors())

    def is_leaf(self):
        """
        Return True iff this page has no sub-pages.
        :return:
        :rtype: bool
        """
        return self.generation() == self.leaf_level

    def sister(self, index):
        children = self.parent.children
        node_order = children.index(self)
        if len(children) > node_order + index >= 0:
            return children[node_order + index]
        else:
            raise IndexError('No such sister')

    def previous_sister(self):
        return self.sister(-1)

    def next_sister(self):
        return self.sister(1)

    def next_node(self):
        if self.has_children():
            return self.children[0]
        else:
            try:
                next_node = self.next_sister()
            except IndexError:
                next_node = self.next_node_iter(self.parent)
        return next_node

    def next_node_iter(self, node):
        if node.parent is None:
            raise IndexError('No more nodes')
        try:
            right = node.next_sister()
            return right
        except IndexError:
            right = self.next_node_iter(node.parent)
        return right

    def descendants(self):
        descendants = set(self.children)
        for child in self.children:
            descendants.update(child.descendants())
        return descendants

    def cousins(self):
        node = self
        indices = []
        while node.parent is not None:
            indices.insert(0, node.parent.children.index(node))
            node = node.parent
        indices.pop(0)
        cousins = []
        for child in node.children:
            cousin = child
            for index in indices:
                try:
                    cousin = cousin.children[index]
                except IndexError:
                    cousin = Page(child.name + r' cousin')
            cousins.append(cousin)
        return cousins

    def family(self):
        """
        Return all ancestors (including self) and children of same.
        :rtype: set(Page[])
        """
        family = set([])
        for ancestor in self.ancestors():
            family.update(ancestor.children)
        family.update(self.descendants())
        return family

    def url_form(self, extend=False):
        """
        Return the name of the Page in a form suitable for URLs.
        :param extend: True iff '(/index).html' extension is required.
        :type: bool

        :return:
        :rtype: str
        """
        name = self.name.lower()
        name = re.sub(r'&#x294;', "''", name)
        name = re.sub(r'&x2019;|&rsquo;', "'", name)
        name = re.sub(r'<(div|ipa).*?\1>', '', name)
        name = re.sub(r"<.*?>|[/.; ]", "", name)
        extension = '.html' if self.is_leaf() else '/index.html'
        return name + extension if extend else name

    def folder(self):
        """
        Return the folder in which the Page should appear.
        If the Page is in the first generation,
        :rtype: int
        """
        if self.generation():
            text = "/".join([i.url_form() for i in self.ancestors()[1:]]) + '/'
            text += self.url_form() + '/' if not self.is_leaf() else ''
            return text if self.generation() != 1 else self.url_form() + '/'
        else:
            return ''

    def link(self, extend=True):
        """Return a link to this node of the form 'highlulani/morphology/index.html'"""
        if extend:
            return self.folder() + (self.url_form(True) if self.is_leaf() else 'index.html')
        else:
            return self.folder() + (self.url_form(False) if self.is_leaf() else 'index')

    def hyperlink(self, destination, template="{0}", just_href=False):
        """
        Create a hyperlink
        Source and destination must be within the same website
        :param just_href: Put anchor tags around the link?
        :type: bool
        :param template: The form of the hyperlink. Use $
        :type: str
        :param destination: the page being linked to
        :type: Node
        :return:
        """
        # returns plain text (i.e.: not a hyperlink) if source and destination are the same
        if self == destination:
            return template.format(destination.name)
        # @variable (int) change: accounts for the fact that an internal node has one less level than expected
        change = int(not self.is_leaf())
        # @variable (str) href: a hyperlink reference of the form '../../phonology/consonants/index.html'
        # @variable (str) link: a hyperlink of the form '<a href="../../phonology/consonants/index.html>Consonants</a>'
        try:
            extension = ".html" if destination.is_leaf() else "/index.html"
            self_ancestors = self.ancestors() + [self]
            destination_ancestors = destination.ancestors() + [destination]
            ancestor_list = zip(self_ancestors, destination_ancestors)
            direct = destination in self_ancestors
            # @variable (int) common: the number of nodes common to both source and destination ancestries
            try:
                common = [i != j for i, j in ancestor_list].index(True)
            except ValueError:
                common = len(ancestor_list)
            # @variable (int) up: the number of levels the common ancestor is above the source
            # @variable (str) down: the hyperlink address from the common ancestor to the descendant
            if destination == self.root():
                up = self.generation() + change - 1
                down = "index"
                extension = ".html"
            else:
                up = self.generation() + change - (destination.generation() if direct else common)
                down = destination.url_form() if direct else \
                    "/".join([node.url_form() for node in destination_ancestors[common:]])
            href = 'href="{0}"'.format((up * '../') + down + extension)
            link = '<a {0}>{1}</a>'.format(href, template.format(destination.name))
        except AttributeError:  # destination is a string
            up = self.generation() + change - 1
            href = 'href="{0}"'.format((up * '../') + destination)
            link = '<a {0}>{1}</a>'.format(href, template.format(destination))
        return href if just_href else link

    def change_to_heading(self, text):
        """
        Transform '3]Blah' -->\n '<h2 id="blah">Blah</h2>
        :param: text
        :type: str
        :return:
        """
        try:
            level, name = text.split(']')
        except ValueError:
            return text[1:]
        level = int(level) - self.generation() + 1
        url_id = Page(name).url_form()
        return '<h{0} id="{1}">{2}</h{0}>\n'.format(str(level), url_id, name)

    def title(self):
        ancestry = [re.sub(r'[[<].*?[]>]', '', ancestor.name) for ancestor in self.ancestors()]
        ancestry.reverse()
        return re.sub(r'[[<].*?[]>]', '', self.name) + " &lt; " + " &lt; ".join(ancestry)

    def contents(self):
        """
        Construct the main contents of a page
        :rtype: str
        """
        mode = ContentsMode()
        output = ''
        content = self.content.replace(' | ', '\n')
        for line in content.split('['):
            if line == '':
                continue
            if re.match(r'\d\]', line):
                heading, rest = line.split('\n', 1)
                line = self.change_to_heading(heading)
                line += '<p>{0}</p>'.format('</p><p>'.join(rest.splitlines())) if rest else ''
            else:
                try:
                    category, text = line.split(']', 1)
                    mode.set(category)
                    try:
                        line = mode.replacements[category] + text
                    except KeyError:
                        raise KeyError('{0}]{1}'.format(category, line))
                    if not mode.table():
                        line = line.replace('</tr><tr><td>', '<' + mode.delimiter() + '>')
                    line = re.sub('\n$', '</' + mode.delimiter() + '>', line)
                    line = '</d>\n<d>'.replace('d', mode.delimiter()).join(line.splitlines())
                except ValueError:
                    raise ValueError(line + ': ' + self.name)
            output += line
        return output

    def stylesheet_and_icon(self):
        output = ('<link rel="stylesheet" type="text/css" $style$>\n'
                  '<link rel="icon" type="image/png" $icon$>\n')
        output = output.replace('$style$', self.hyperlink('style.css', just_href=True))
        output = output.replace('$icon$', self.hyperlink('favicon.png', just_href=True))
        return output

    def toc(self):
        if self.is_leaf():
            return ''
        elif self.generation():
            return "".join(['<p>{0}</p>'.format(self.hyperlink(child)) for child in self.children])
        else:  # self is root
            links = ''
            level = 0
            for page in self.site()():
                if not page.generation():
                    continue
                old_level = level
                level = page.generation()
                if level > old_level:
                    links += '<ul class=\"level-{0}\">'.format(str(level))
                elif level < old_level:
                    links += (old_level - level) * '</ul>\n'
                links += '<li>{0}</li>\n'.format(self.hyperlink(page))
            links += (level - 1) * '</ul>\n'
            return links

    def links(self):
        output = ('<ul><li>' + self.hyperlink(self.root()) + '</li>\n'
                  '$links$\n'
                  '<li class="up-arrow">' + self.hyperlink(self.parent, 'Go up one level &uarr;') + '</li>\n'
                  '<li class="link">' + self.hyperlink('search.html', 'Search') + '</li>\n'
                  '<li class="link">$out$</li>\n'
                  '<li class="link">$out$</li>\n'
                  '</ul>\n')
        for item, link in (['Grammar', 'grammar'],
                           ['Dictionary', 'dictionary'],
                           ['The Coelacanth Quartet', 'coelacanthquartet']):
            if item != self.root().name:
                output = output.replace('$out$', '<a href=\"http://{0}.tinellb.com\">{1}</a>'.format(link, item), 1)
        return output

    def family_links(self):
        links = ''
        level = 0
        family = self.family()
        for page in self.site()():
            if page in family:
                old_level = level
                level = page.generation()
                if level > old_level:
                    links += '<ul class=\"level-{0}\">'.format(str(level))
                elif level < old_level:
                    links += (old_level - level) * '</ul>\n'
                if page == self:
                    links += '<li class="normal">{0}</li>\n'.format(self.hyperlink(page))
                else:
                    links += '<li>{0}</li>\n'.format(self.hyperlink(page))
        links += (level) * '</ul>\n'
        return self.links().replace('$links$', links)

    def cousin_links(self):
        links = ''
        level = 0
        family = self.family()
        for page in self.site()():
            if page in family:
                old_level = level
                level = page.generation()
                if level > old_level:
                    links += '<ul class="level-{0}">'.format(str(level))
                elif level < old_level:
                    links += (old_level - level) * '</ul>\n'
                if page == self:
                    links += '<li class="normal">{0}</li>\n'.format(self.hyperlink(page))
                else:
                    links += '<li>{0}</li>\n'.format(self.hyperlink(page))
        links += (level + 1) * '</ul>\n' + '<p>Other Versions:</p><ul class="level-1">'
        categories = [node.name for node in self.elders()]
        cousins = self.cousins()
        for cousin, category in zip(cousins, categories):
            if cousin is not self:
                links += '<li>{0}</li>\n'.format(self.hyperlink(cousin, category))
        links += '</ul><ul>'
        return self.links().replace('$links$', links)

    def elder_links(self):
        links = '<ul>'
        for elder in self.elders():
            links += '<li{0}>{1}</li>'.format(
                (' class="normal"' if elder in [self, self.parent] else ''), self.hyperlink(elder))
        return self.links().replace('$links$', links + '</ul>')

    def nav_footer(self):
        output = ''
        if self.previous:
            output += '<div>\n{0}\n</div>\n'.format(self.hyperlink(self.previous, '&larr; Previous page'))
        else:
            output += '<div>\n{0}\n</div>\n'.format(self.hyperlink(self.root(), '&uarr; Return to Menu'))
        try:
            output += '<div>\n{0}\n</div>\n'.format(self.hyperlink(self.next_node(), 'Next page &rarr;'))
        except IndexError:
            output += '<div>\n{0}\n</div>\n'.format(self.hyperlink(self.root(), 'Return to Menu &uarr;'))
        return output

    def publish(self, template=None):
        if template is None:
            if self.generation():
                template = Template()
            else:
                template = Template('main_template.html')
        try:
            page = template.template
        except AttributeError:
            # template is a string
            page = template
        for (section, function) in [
            ('{title}', self.title),
            ('{stylesheet}', self.stylesheet_and_icon),
            ('{content}', self.contents),
            ('{toc}', self.toc),
            ('{family-links}', self.family_links),
            ('{cousin-links}', self.cousin_links),
            ('{elder-links}', self.elder_links),
            ('{nav-footer}', self.nav_footer)
        ]:
            if page.count(section):
                page = page.replace(section, function())
        try:
            os.makedirs(self.folder())
        except os.error:
            pass
        with open(self.link(), "w") as f:
            page = re.sub('\x05\x05.*?\x06\x06', '', page)
            page = re.sub('\x05.*?\x06', '', page)
            f.write(page.replace(chr(7), ''))

    def remove(self):
        os.remove(self.link())

    def analyse(self, markdown=None):
        wordlist = {}
        if markdown is None:
            markdown = Translation.Markdown()
        content = self.content[2:]
        """remove tags, and items between some tags"""
        content = re.sub(r'\[\d\]|<(ipa|high-lulani)>.*?</\1>|<.*?>', ' ', content)
        """change punctuation to paragraph marks, so that splitlines works"""
        content = re.sub(r'[!?.]', '\n', content)
        """remove hidden text"""
        content = re.sub(r'\x05.*?\x06\x06', '', content)
        content = re.sub(r'\x05.*?\x06', '', content)
        """remove bells, spaces at the beginnings and end of lines, and duplicate spaces and end-lines"""
        content = re.sub(r'(?<=\n) +| +(?=[\n ])|^ +| +$|\n+(?=\n)|[\x07,:]', '', content)
        """remove duplicate end-lines"""
        content = re.sub(r'\n+(?=\n)', '', content)
        """remove tags in square brackets"""
        content = re.sub(r'\[.*?\]', '', content)
        lines = content.splitlines()
        content = markdown.to_markdown(content).lower()
        """remove punctuation, and tags in square brackets"""
        content = re.sub(r'\'"|[.!?`"/{}\\();-]|\'($| )|\[.*?\]|&nbsp', ' ', content)
        """make glottal stops lower case where appropriate"""
        content = re.sub(r"(?<=[ \n])''", "'", content)
        for number, line in enumerate(content.splitlines()):
            for word in line.split():
                try:
                    if wordlist[word][-1] != number:
                        wordlist[word].append(number)
                except KeyError:
                    wordlist[word] = [number]
        return Analysis(wordlist, lines)


class Template:
    def __init__(self, filename='template.html'):
        try:
            with open(filename) as f:
                self.template = f.read()
        except IOError:
            win32api.MessageBox(0, 'There does not appear to be a template here at ' + os.getcwd(), 'Template Missing')


class MainPage:
    def __init__(self, filename):
        with open(filename) as f:
            self.main_page = f.read()


class Dictionary(Site):
    def __init__(self):
        Site.__init__(self, "Dictionary", 2)


class Grammar(Site):
    def __init__(self):
        Site.__init__(self, "Grammar")


class Story(Site):
    def __init__(self):
        Site.__init__(self, "The Coelacanth Quartet")


class ContentsMode:
    def __init__(self):
        self.modes = []
        self.mode = 'n'

        self.replacements = {'t': '<table><tr><td>',
                             '/t': '</tr></table>',
                             'r': '</tr><tr><td>',
                             'n': '<ol><li>',
                             '/n': '</ol>',
                             'l': '<ul><li>',
                             '/l': '</ul>',
                             'e': '<p class="example_no_lines">',
                             'f': '<p class="example">'}

    def normal(self):
        return self.mode == 'n'

    def table(self):
        return self.mode == 't'

    def list(self):
        return self.mode == 'l'

    def set(self, mode):
        if mode in ['t', 'l']:  # table, unordered list
            self.modes.append(self.mode)
            self.mode = mode
        elif mode == 'n':   # numbered list
            self.modes.append(self.mode)
            self.mode = 'l'
        elif mode.startswith('/'):   # leave mode
            try:
                self.mode = self.modes.pop()
            except IndexError:
                self.mode = 'n'

    def delimiter(self):
        if self.mode == 'n':
            return 'p'
        elif self.mode == 't':
            return 'td'
        elif self.mode == 'l':
            return 'li'


def normal_text(text):
    """puts html paragraph tags around carriage-return delimited texts
    @param (string) text: the text to be modified
    @return (string) text: the modified string"""
    return '<p>{0}</p>'.format('</p><p>'.join(text.splitlines())) if text else ''


class Analysis:
    def __init__(self, wordlist, lines, pages=None, names=None):
        self.wordlist = wordlist
        self.lines = lines
        self.pages = pages if pages else []
        self.names = names if pages else []

    def __str__(self):
        """Returns string version of Analysis"""
        """replace single quotes with double quotes to comply with json formatting"""
        wordlist = str(self.wordlist)
        wordlist = re.sub(r"(?<=[{ ])'|'(?=:)", '"', str(wordlist))
        """insert line breaks"""
        wordlist = re.sub(r'(?<=},) ', '\n', wordlist)
        lines = '"sentences":["{0}"]'.format('",\n "'.join(self.lines))
        pages = '"urls":["{0}"]'.format('",\n "'.join(self.pages))
        names = '"names":["{0}"]'.format('",\n "'.join(self.names))
        wordlist = '"terms": {0}'.format(wordlist)

        return '{{{0}}}'.format(',\n'.join([wordlist, lines, pages, names]))

if __name__ == '__main__':
    for site in Grammar, Story :#, Dictionary:
        site().publish()
