import os
import re
import datetime
import win32api

import Translation


class Site:
    """
    A hierarchy of Pages
    """
    def __init__(self, destination, name, source, template, main_template, markdown, searchjson, leaf_level):
        """
        :param destination (str): the full path where the Site is to be located
        :param name (str): human-readable name of the Site
        :param source (str): filename and extension of the source file, relative to destination
        :param template (str): filename and extension of the template for ordinary pages, relative to destination
        :param main_template (str): filename and extension of the template for the top-level (root) page, relative to destination
        :param markdown (str): filename and extension of the markdown file, relative to destination
        :param leaf_level (int): the level of the lowermost pages in the hierarchy, where the root is at 0.

        :attribute template (Template): the template for ordinary pages
        :attribute main_template (Template): the template for the top-level page
        :attribute markdown (Markdown): the conversion between markup and markdown
        :attribute current (Page):
        :attribute root (Page): the root of the hierarchy
        """
        self.choose_dir(destination)
        # initialize attributes and utility classes
        self.name = name
        self.template = Template(template)
        self.main_template = Template(main_template)
        self.markdown = Translation.Markdown(markdown)
        self.searchjson = searchjson
        self.leaf_level = leaf_level
        self.current = None
        self.length = 0
        node = self.root = Page(name, leaf_level=self.leaf_level, markdown=self.markdown)

        # break source text into pages, with the splits on square brackets before numbers <= leaf_level
        with open(source) as source:
            source = source.read()
        split = re.compile(r'\[(?=[{0}])'.format(''.join(map(lambda x: str(x + 1), range(self.leaf_level)))))
        source = split.split(source)

        # create page on appropriate level of hierarchy, with name taken from the source file
        # ignore first (empty) page
        for page in source[1:]:
            previous = node
            level, name = re.split('[]\n]', page, 2)[:2]
            level = int(level)
            while level != node.level + 1:
                # climb back up the hierarchy to the appropriate level
                node = node.parent
            node = self.add_node(name, node, page, previous)
            self.length += 1

    @staticmethod
    def choose_dir(destination):
        try:
            os.makedirs(destination)
        except os.error:
            pass
        try:
            os.chdir(destination)
        except os.error:
            win32api.MessageBox(0, 'That does not seem to be a valid destination. Please try again.', 'Unable to Create destination')
            return
        os.chdir(destination)

    def __str__(self):
        """
        Join each non-empty page, and remove the first character
        :rtype: str
        :class: Site
        """
        return ''.join([str(page) for page in self if str(page)])[1:] # apparently adds a [ to the beginning, which is why we remove it

    def __len__(self):
        """
        :return: the number of pages in the Site
        :rtype: int
        :class: Site
        """
        return self.length

    def __iter__(self):
        """
        :class: Site
        """
        return self

    def next(self):
        """
        Set the next Page as the current Page
        :return: new current Page
        :rtype: Page
        :class: Site
        """
        if self.current is None:
            self.current = self.root
            return self.root
        try:
            self.current = self.current.next_node()
        except IndexError:
            self.current = None
            raise StopIteration
        return self.current

    def previous(self):
        """
        Set the previous Page as the current Page, assuming the old Page has an instance variable 'previous'
        :return: new current Page
        :rtype: Page
        :class: Site
        """
        self.current = self.current.previous
        return self.current

    def reset(self):
        """
        Reset the iterator
        :class: Site
        """
        self.current = None

    def __getitem__(self, page):
        """
        Search the Site for a particular page
        :param page (str): the name of the page being searched for
        :param page (int): the index number of the page being searched for, where 0 is the root
        :rtype: Page
        :class: Site
        """
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
        """
        Add a Page to the appropriate location in the Site, and return that Page
        If another Page exists at the same point with the same name, a '2' is appended to the name
        :param name (str): human-readable name of the Page
        :param parent (Page): the parent node of the new Page
        :param content (str): the content of the Page, including the header line
        :param previous (Page): the previous Page in the Site
        :return (Page): the Page that was added
        :class: Site
        """
        child = Page(name, parent, content, self.leaf_level, previous, self.markdown)
        if child not in parent.children:
            parent.children.append(child)
        else:
            return self.add_node(name + '2', parent, content, previous)
        return child

    def publish(self):
        """
        Publish all webpages, and create search JSON file.
        :class: Site
        """
        length = len(self)
        chunk = 3 if length > 1000 else 50
        progress = 1
        self.root.publish(self.main_template)
        self.reset(); self.next()
        for i, page in enumerate(self):
            page.publish(self.template)
            if i == int(progress * chunk * length / 100):
                yield str(progress * chunk) + '% Done'
                progress += 1
        self.update_json()

    def update_json(self):
        with open(self.searchjson, 'w') as f:
            f.write(str(self.analyse()))

    def analyse(self):
        """
        Analyse the Site for searchable content
        :rtype: Analysis
        :class: Site
        """
        words, sentences, urls, names = {}, [], [], []
        for page_number, entry in enumerate(self):
            # line numbers in each Page are incremented by the current total number of sentences
            base = len(sentences)
            # analyse the Page
            analysis = entry.analyse(self.markdown)
            # add results to appropriate lists and dictionaries
            new_words = analysis.words
            sentences += analysis.sentences
            urls.append(entry.link(False))
            names.append(entry.name)
            for word in new_words:
                # increment line numbers by base
                # use str(page_number) because search.js relies on that
                locations = {str(page_number): map(lambda x: x + base, new_words[word])}
                try:
                    words[word].update(locations)
                except KeyError:
                    words[word] = locations
        return Analysis(words, sentences, urls, names)


class Page:
    """
    A node in the hierarchy
    """
    def __init__(self, name, parent=None, content="", leaf_level=3, previous=None, markdown=None):
        """
        :param name (str): the name of the Page
        :param parent (Page): the Page's immediate ancestor
        :param content (str): text that will ultimately appear on the Page's webpage
        :param leaf_level (int): the level number of the outermost branches of the hierarchy
        :param previous (Page):
        :param markdown (Markdown): the Markdown to be used when constructing the text of the webpage

        :attribute children (list): the Pages beneath self
        :attribute isLeaf (bool): is the Page at the lowest level of the hierarchy?
        :attribute urlform (str): the name of the Page, in a form suitable for URLs
        :attribute level (int): how low the Page is on the hierarchy
        :attribute flatname (FlatName): the name and Tinellbian alphabetical order of the Page
        """
        self.name = name
        self.parent = parent
        self.children = []
        self.level = self.generation() - 1
        self.isLeaf = (leaf_level == self.level)
        self.content = content
        self.previous = previous
        self.markdown = markdown
        self.urlform = self.simple()
        self.flatname = FlatName(self.urlform)

    def simple(self):
        """
        Simplify the name to make it more suitable for urls
        Put the name in lower case, and remove tags
        Allowed punctuation: -'.$_+!()
        """
        name = self.name.lower()
        # remove safe punctuations that should only be used to encode non-ascii characters
        name = re.sub(r'[\'.$_+!()]', '', name)
        name = self.markdown.to_markdown(name)
        # remove text within tags
        name = re.sub(r'<(div|ipa).*?\1>', '', name)
        # remove tags, spaces and punctuation
        name = re.sub(r'<.*?>|[/*;: ]', '', name)
        return name

    def __str__(self):
        return '[' + self.content

    def __eq__(self, other):
        """
        :param self (Page):
        :param other (Page): the two Pages being compared
        :return (bool): True iff both nodes have the same URL and the same parent
        """
        try:
            if self.urlform == other.urlform:
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
        """
        :return (bool): True iff the self.name comes before self.other in Tinellbian alphabetical order
        """
        alphabet = " aeiyuow'pbtdcjkgmnqlrfvszxh"
        try:
            if self.name == other.name:
                return False
        except AttributeError:  # self or other are None
            return self is None is not other
        if self.flatname.name == other.flatname.name:
            return self.flatname.score < other.flatname.score
        for s, t in zip(self.flatname.name, other.flatname.name):
            if s != t:
                try:
                    return alphabet.index(s) < alphabet.index(t)
                except ValueError:
                    continue
        else:
            return len(self.flatname.name) < len(other.flatname.name)

    def __gt__(self, other):
        return not self <= other

    def __le__(self, other):
        return self < other or self.name == other.name

    def __ge__(self, other):
        return not self < other

    def __getitem__(self, item):
        """
        Search the children of the Page for a particular item
        :param item (int): index number of the item to return
        :param item (str): name of the item to return
        :return (Page):
        :raises KeyError: item cannot be found
        """
        try:
            item = int(item)
            return self.children[item]
        except ValueError:  # item is a string
            for child in self.children:
                if child.name == item:
                    return child
            else:
                raise KeyError('No such page ' + item + 'in ' + self.name)

    def __hash__(self):
        return hash(self.name)

    def insert(self, index=None):
        """
        Insert self into the Site as a child of its parent
        :pre: Self has a filled parent attribute
        :param index (int): the index number to be inserted at
        :param index (None): self is inserted in the correct Tinellbian alphabetical order
        :return (Page): the Page just inserted
        """
        try:
            self.parent.children.insert(index, self)
        except TypeError:   # index is None
            for index, page in enumerate(self.parent.children):
                number = index
                if self <= page:
                    self.parent.children.insert(number, self)
                    break
            else:
                self.parent.children.append(self)
            return self

    def delete(self):
        """
        Delete self and all of its descendants
        """
        self.parent.children.remove(self)

    def has_children(self):
        """
        :return (bool): True iff self has children
        """
        return len(self.children) > 0

    def root(self):
        """
        Proceed up the Site
        :return (Page): the top Page in the Site
        """
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    def genealogy(self):
        """
        Generates for every Page in the Site sequentially
        :yield (Page):
        :raises StopIteration:
        """
        node = self.root()
        yield node
        while True:
            try:
                node = node.next_node()
                yield node
            except IndexError:
                raise StopIteration

    def elders(self):
        """
        The first generation in the Site
        :return (Page[]):
        """
        return self.root().children

    def ancestors(self):
        """
        Self and the direct ancestors of self
        :return (Page[]):
        """
        node = self
        ancestry = [node]
        while node.parent is not None:
            node = node.parent
            ancestry.insert(0, node)
        return ancestry

    def generation(self):
        """
        :return (int): the generation number of the Page, with the root at one
        """
        return len(self.ancestors())

    def sister(self, index):
        children = self.parent.children
        node_order = children.index(self)
        if len(children) > node_order + index >= 0:
            return children[node_order + index]
        else:
            raise IndexError('No such sister')

    def previous_sister(self):
        """
        :return (Page): the previous Page if it has the same parent as self
        :raises IndexError: the previous Page does not exist
        """
        return self.sister(-1)

    def next_sister(self):
        """
        :return (Page): the next Page if it has the same parent as self
        :raises IndexError: the next Page does not exist
        """
        return self.sister(1)

    def next_node(self):
        """
        Finds the next sister, or uses iteration to find the next Page
        :return (Page): the next Page in sequence
        :raises IndexError: the next Page does not exist
        """
        if self.has_children():
            return self.children[0]
        else:
            try:
                next_node = self.next_sister()
            except IndexError:
                next_node = self.next_node_iter(self.parent)
        return next_node

    def next_node_iter(self, node):
        """
        Iterates over the Site to find the next Page
        :return (Page): the next Page in sequence
        :raises IndexError: the next Page does not exist
        """
        if node.parent is None:
            raise IndexError('No more nodes')
        try:
            right = node.next_sister()
            return right
        except IndexError:
            right = self.next_node_iter(node.parent)
        return right

    def descendants(self):
        """
        All the descendants of self, using iteration
        :return (Page{}):
        """
        descendants = set(self.children)
        for child in self.children:
            descendants.update(child.descendants())
        return descendants

    def cousins(self):
        """
        Taking a sub-hierarchy as the descendants of a Page, cousins are Pages at the same point as self, but in different sub-hierarchies.
        """
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
                except (IndexError, AttributeError):
                    cousin = None
            cousins.append(cousin)
        return cousins

    def family(self):
        """
        Return all of self, descendants, sisters, ancestors, and sisters of ancestors
        :rtype (Page{}):
        """
        family = set([])
        for ancestor in self.ancestors():
            family.update(ancestor.children)
        family.update(self.descendants())
        return family

    def fullUrlForm(self):
        """
        :return (str): the name and extension of the Page in a form suitable for URLs
        """
        # extension = '/index' if not self.isLeaf else ''
        return '{0}{1}.html'.format(self.urlform, '/index' if not self.isLeaf else '')

    def folder(self):
        """
        :return (str): the folder in which the Page should appear, or an empty string if Page is the root
        """
        if self.level:
            text = "/".join([i.urlform for i in self.ancestors()[1:-1]]) + '/'
            text += self.urlform + '/' if not self.isLeaf else ''
            return text if self.level != 1 else self.urlform + '/'
        else:
            return ''

    def link(self, extend=True):
        """
        :return (str): a link to self of the form 'highlulani/morphology/index.html'
        """
        if extend:
            return self.folder() + (self.fullUrlForm() if self.isLeaf else 'index.html')
        else:
            return self.folder() + (self.urlform if self.isLeaf else 'index')

    def hyperlink(self, destination, template="{0}", needAnchorTags=True, fragment=''):
        """
        Source and destination must be within the same website
        :param needAnchorTags (bool): Put anchor tags around the link?
        :param template (str): The form of the hyperlink
        :param destination (Page): the Page being linked to
        :param fragment (str): allows for a # fragment. Must include the hash sign.
        :return (str):
        """
        # returns plain text (i.e.: not a hyperlink) if source and destination are the same
        if destination is self:
            return template.format(destination.name)
        # :variable change (int): accounts for the fact that an internal node has one less level than expected
        change = int(not self.isLeaf)
        # :variable address (str): a hyperlink reference of the form '../../phonology/consonants/index.html'
        # :variable link (str): a hyperlink of the form '<a href="../../phonology/consonants/index.html>Consonants</a>'
        try:
            extension = ".html" if destination.isLeaf else "/index.html"
            ancestors = {'self': self.ancestors(), 'destination': destination.ancestors()}
            isDirect = destination in ancestors['self']
            # :variable (int) common: the number of nodes common to both source and destination ancestries
            try:
                common = [i != j for i, j in zip(*[x for x in ancestors.values()])].index(True)
            except ValueError:
                common = min(map(len, ancestors.values()))
            # :variable (int) up: the number of levels the common ancestor is above the source
            # :variable (str) down: the hyperlink address from the common ancestor to the descendant
            if destination == self.root():
                up = self.level + change - 1
                down = "index"
                extension = ".html"
            else:
                up = self.level + change - (destination.level if isDirect else common)
                down = destination.urlform if isDirect else \
                    "/".join([ancestor.urlform for ancestor in ancestors['destination'][common:]])
            address = (up * '../') + down + extension + fragment
            link = '<a href="{0}">{1}</a>'.format(address, template.format(destination.name))
        except AttributeError:  # destination is a string
            up = self.level + change - 1
            address = (up * '../') + destination + fragment
            link = '<a {0}>{1}</a>'.format(address, template.format(destination))
        return link if needAnchorTags else address

    def change_to_heading(self, text):
        """
        Transform '3]Blah' --> '<h2 id="blah">Blah</h2>'
        :param text (str)
        :return (str): an HTML heading with the id as the URL form of the name of the Page
        """
        level, name = text.split(']')
        level = int(level) - self.level + 1
        url_id = Page(name, markdown=self.markdown).urlform
        return '<h{0} id="{1}">{2}</h{0}>\n'.format(str(level), url_id, name)

    def title(self):
        """
        :return (str): the ancestry of self, suitable for HTML titles
        """
        # remove tags from names
        ancestry = map(lambda x: re.sub(r'[[<].*?[]>]', '', x.name), self.ancestors())
        return ' &lt; '.join(ancestry[::-1])

    def contents(self):
        """
        Markup tags in square brackets to HTML, including headings, paragraphs, tables and lists.
        :return (str): the main contents of a Page
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
                line += '<p>{0}</p>\n'.format('</p>\n<p>'.join(rest.splitlines())) if rest else ''
            else: # tag is non-numeric, i.e.: represents something other than a heading
                try:
                    category, text = line.split(']', 1)
                    mode.set(category)
                    try:
                        line = mode.replacements[category] + text
                    except KeyError: # something's gone wrong
                        raise KeyError('{0}]{1}. Please check source file'.format(category, line))
                    if not mode.table():
                        line = line.replace('</tr><tr><td>', '<' + mode.delimiter + '>')
                    line = re.sub('\n$', '</' + mode.delimiter + '>', line)
                    line = '</d>\n<d>'.replace('d', mode.delimiter).join(line.splitlines())
                except ValueError:
                    raise ValueError(line + ': ' + self.name)
            output += line
        return output

    def stylesheet_and_icon(self):
        """
        :return (str): relative HTML links to the stylesheet and icon for self.
        :class: Page:
        """
        output = '''<link rel="stylesheet" type="text/css" href="{0}">
    <link rel="icon" type="image/png" href="{1}">'''.format(
            self.hyperlink('style.css', needAnchorTags=False),
            self.hyperlink('favicon.png', needAnchorTags=False))
        return output

    def search_script(self):
        """
        :return (str): javascript function for moving to search page if required, using relative links
        """
        output = '''<script type="text/javascript">
        if (window.location.href.indexOf("?") != -1) {{
            window.location.href = "{0}" +
            window.location.href.substring(window.location.href.indexOf("?")) + "&andOr=and";
        }}
    </script>'''.format(self.hyperlink('search.html', needAnchorTags=False))
        return output

    def toc(self):
        """
        :return (str): a table of contents in HTML
        """
        if self.isLeaf:
            return ''
        elif self.level: # self neither root nor leaf
            return "".join(['<p>{0}</p>\n'.format(self.hyperlink(child)) for child in self.children])
        else:  # self is root
            links = ''
            level = 0
            for page in self.genealogy():
                if not page.level:
                    continue
                old_level = level
                level = page.level
                if level > old_level:
                    links += '<ul class=\"level-{0}\">'.format(str(level))
                elif level < old_level:
                    links += (old_level - level) * '</ul>\n'
                links += '<li>{0}</li>\n'.format(self.hyperlink(page))
            links += (level - 1) * '</ul>\n'
            return links

    def links(self):
        """
        :return (str):
        """
        output = '''<ul>
                  <li class="link"><a href="http://www.tinellb.com">&uarr; Main Page</a></li>
                  <li class="link">$out$</li>
                  <li class="link">$out$</li>
                </ul>
                <ul><li{0}>{1}</li>
                  <form id="search">
                    <li class="search">
                      <input type="text" name="term"></input> <button type="submit">Search</button>
                    </li>
                  </form>
                $links$
                </ul>'''.format(' class="normal"' if self == self.root() else '',
                                self.hyperlink(self.root()))
        for item, link in ( ['Grammar', 'grammar'],
                            ['Dictionary', 'dictionary'],
                            ['The Coelacanth Quartet', 'coelacanthquartet']):
            if item != self.root().name:
                output = output.replace('$out$', '<a href="http://{0}.tinellb.com">{1} &rarr;</a>'.format(link, item), 1)
        return output

    def family_links(self):
        links = ''
        level = 0
        family = self.family()
        for page in self.genealogy():
            if page in family:
                old_level = level
                level = page.level
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
        for page in self.genealogy():
            if page in family:
                old_level = level
                level = page.level
                if level > old_level:
                    links += '<ul class="level-{0}">'.format(str(level))
                elif level < old_level:
                    links += (old_level - level) * '</ul>\n'
                if page == self:
                    links += '<li class="normal">{0}</li>\n'.format(self.hyperlink(page))
                else:
                    links += '<li>{0}</li>\n'.format(self.hyperlink(page))
        links += (level + 1) * '</ul>\n' + '<p>Other Versions:</p>\n<ul class="level-1">'
        categories = [node.name for node in self.elders()]
        cousins = self.cousins()
        for cousin, category in zip(cousins, categories):
            if cousin and cousin is not self:
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
        div = '<div>\n{0}\n</div>\n'
        if self.previous:
            output = div.format(self.hyperlink(self.previous, '&larr; Previous page'))
        else:
            output = div.format(self.hyperlink(self.root(), '&uarr; Return to Menu'))
        try:
            output += div.format(self.hyperlink(self.next_node(), 'Next page &rarr;'))
        except IndexError:
            output += div.format(self.hyperlink(self.root(), 'Return to Menu &uarr;'))
        return output

    def copyright(self):
        try:
            date = datetime.datetime.strptime(max(re.findall(r'(?<=&date=)\d{8}', self.content)), '%Y%m%d')
        except ValueError:
            return ''
        suffix = "th" if 4 <= date.day <= 20 or 24 <= date.day <= 30 else ["st", "nd", "rd"][date.day % 10 - 1]
        output = datetime.datetime.strftime(date, '&copy;%Y&nbsp;Ryan&nbsp;Eakins. Last&nbsp;updated:&nbsp;%A,&nbsp;%B&nbsp;%#d' + suffix + ',&nbsp;%Y.')
        return output

    def publish(self, template):
        """
        :param template (Template): the basic template to be published against
        :param template (str): the basic template to be published against
        """
        try:
            page = template.template
        except AttributeError:
            # template is a string
            page = template
        for (section, function) in [
            ('{title}', self.title),
            ('{stylesheet}', self.stylesheet_and_icon),
            ('{search-script}', self.search_script),
            ('{content}', self.contents),
            ('{toc}', self.toc),
            ('{family-links}', self.family_links),
            ('{cousin-links}', self.cousin_links),
            ('{elder-links}', self.elder_links),
            ('{nav-footer}', self.nav_footer),
            ('{copyright}', self.copyright)
        ]:
            if page.count(section):
                page = page.replace(section, function())
        try:
            os.makedirs(self.folder())
        except os.error:
            pass
        with open(self.link(), "w") as f:
            page = re.sub('\x05.*?(\x06\x06*)', '', page)
            page = re.sub(r'\x07', '', page)
            page = re.sub(r'&date=\d{8}', '', page)
            f.write(page)

    def remove(self):
        os.remove(self.link())

    def analyse(self, markdown):
        wordlist = {}
        content = self.content[2:]
        """remove tags, and items between some tags"""
        content = re.sub(r'\[\d\]|<(ipa|high-lulani|span)>.*?</\1>|<.*?>', ' ', content)
        """change punctuation to paragraph marks, so that splitlines works"""
        content = re.sub(r'[!?.]', '\n', content)
        """change punctuation to space"""
        content = re.sub(r'[_()]', ' ', content)
        """remove hidden text"""
        content = re.sub(r'\x05.*?(\x06\x06*)', '', content)
        """remove bells, spaces at the beginnings and end of lines, and duplicate spaces and end-lines"""
        content = re.sub(r'(?<=\n) +| +(?=[\n ])|^ +| +$|\n+(?=\n)|[\x07,:]', '', content)
        """remove duplicate end-lines"""
        content = re.sub(r'\n+(?=\n)', '', content)
        """remove tags in square brackets"""
        content = re.sub(r'\[.*?\]', '', content)
        lines = content.splitlines()
        content = markdown.to_markdown(content).lower()
        """change punctuation, and tags in square brackets, into spaces"""
        content = re.sub(r'\'\"|[!?`\"/{}\\();-]|\'($| )|\[.*?\]|&nbsp', ' ', content)
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

class FlatName:
    """
    'flattens' the name to only include letters aiu'pbtdcjkgmnqlrfsxh
    minigolf scoring rules: smallest number wins.
    """
    def __init__(self, name):
        alphabet = "aiu'pbtdcjkgmnqlrfsxh"
        score = 2
        double_letter = re.compile(r'([{0}])\1'.format(alphabet))
        self.score = 0
        self.name = name
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

class Template:
    def __init__(self, filename):
        with open(filename) as f:
            self.template = f.read()


class ContentsMode:
    def __init__(self):
        self.modes = []
        self.mode = 'n'
        self.delimiter = 'p'
        self.replacements = {'t': '<table><tr><td>',
                             '/t': '</tr></table>',
                             'r': '</tr><tr><td>',
                             'n': '<ol><li>',
                             '/n': '</ol>',
                             'l': '<ul><li>',
                             '/l': '</ul>',
                             'e': '<p class="example_no_lines">',
                             'f': '<p class="example">'}
        self.delimiters =   {'n': 'p',
                             't': 'td',
                             'l': 'li'}
        self.delimiter = self.delimiters[self.mode]

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
        self.delimiter = self.delimiters[self.mode]

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
    return '<p>{0}</p>\n'.format('</p>\n<p>'.join(text.splitlines())) if text else ''


class Analysis:
    def __init__(self, words, sentences, urls=None, names=None):
        """
        :param words (dict): {term: locations}
        """
        self.words = words
        self.sentences = sentences
        self.urls = urls if urls else []
        self.names = names if urls else []

    def __str__(self):
        """Returns string version of Analysis"""
        # Replace single quotes with double quotes, and insert line breaks, to comply with JSON formatting
        words = str(self.words)
        words = re.sub(r"(?<=[{ ])'|'(?=:)", '"', str(words))
        words = re.sub(r'(?<=},) ', '\n', words)
        # Create each section of the JSON
        words = '"terms": {0}'.format(words)
        sentences = '"sentences":["{0}"]'.format('",\n "'.join(self.sentences))
        urls = '"urls":["{0}"]'.format('",\n "'.join(self.urls))
        names = '"names":["{0}"]'.format('",\n "'.join(self.names))
        return '{{{0}}}'.format(',\n'.join([words, sentences, urls, names]))

class Dictionary(Site):
    def __init__(self):
        d = Default()
        Site.__init__(self, d.destination + 'dictionary', 'Dictionary', d.source, d.template, d.main_template, d.markdown, d.searchjson, 2)


class Grammar(Site):
    def __init__(self):
        d = Default()
        Site.__init__(self, d.destination + 'grammar', 'Grammar', d.source, d.template, d.main_template, d.markdown, d.searchjson, 3)


class Story(Site):
    def __init__(self):
        d = Default()
        Site.__init__(self, d.destination + 'thecoelacanthquartet', 'The Coelacanth Quartet', d.source, d.template, d.main_template, d.markdown, d.searchjson, 3)

class TheCoelacanthQuartet(Story):
    def __init__(self):
        Story.__init__(self)


class Default():
    def __init__(self):
        self.destination = 'c:/users/ryan/documents/tinellbianlanguages/'
        self.source = 'data.txt'
        self.template = 'template.html'
        self.main_template = 'main_template.html'
        self.markdown = '../replacements.html'
        self.searchjson = 'searching.json'


if __name__ == '__main__':
    oldtime = datetime.datetime.now()
    for site in Story, Grammar, Dictionary:
        site = site()
        print(site.name + ': ')
        for x in site.publish(): print(x)
        newtime = datetime.datetime.now()
        print('100% Done: ' + str(newtime - oldtime))
        oldtime = newtime
