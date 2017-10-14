from contents_mode import ContentsMode
from text_analysis import Analysis
from cached_property import cached_property
from collections import deque
from translation import *
import os

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
        :param markdown (Markdown): the Markdown to be used when creating the url of the Page

        :attribute children (list): the Pages beneath self
        :attribute isLeaf (bool): is the Page at the lowest level of the hierarchy?
        :attribute level (int): how low the Page is on the hierarchy
        """
        self.name = name
        self.parent = parent
        self.children = []
        self.level = self.generation - 1
        self.isLeaf = (leaf_level == self.level)
        self.content = content
        self.previous = previous
        self.markdown = markdown

    @cached_property
    def urlform(self):
        """
        Simplify the name to make it more suitable for urls
        Put the name in lower case, and remove tags
        Allowed punctuation: -'.$_+!()
        """
        return urlform(self.name, self.markdown)

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

    def remove_from_hierarchy(self):
        """
        Remove self and all of its descendants from the hierarchy
        """
        self.parent.children.remove(self)

    @property
    def has_children(self):
        """
        :return (bool): True iff self has children
        """
        return len(self.children) > 0

    @property
    def root(self):
        """
        Proceed up the Site
        :return (Page): the top Page in the Site
        """
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    @property
    def genealogy(self):
        """
        Generates for every Page in the Site sequentially
        :yield (Page):
        :raises StopIteration:
        """
        node = self.root
        yield node
        while True:
            try:
                node = node.next_node
                yield node
            except IndexError:
                raise StopIteration

    @property
    def elders(self):
        """
        The first generation in the Site
        :return (Page[]):
        """
        return self.root.children

    @property
    def ancestors(self):
        """
        Self and the direct ancestors of self, in order down from the root.
        :return (Page[]):
        """
        node = self
        ancestry = deque([node])
        while node.parent is not None:
            node = node.parent
            ancestry.appendleft(node)
        return list(ancestry)

    @property
    def generation(self):
        """
        :return (int): the generation number of the Page, with the root at one
        """
        return len(self.ancestors)

    def sister(self, index):
        children = self.parent.children
        node_order = children.index(self)
        if len(children) > node_order + index >= 0:
            return children[node_order + index]
        else:
            raise IndexError('No such sister')

    @property
    def previous_sister(self):
        """
        :return (Page): the previous Page if it has the same parent as self
        :raises IndexError: the previous Page does not exist
        """
        return self.sister(-1)

    @property
    def next_sister(self):
        """
        :return (Page): the next Page if it has the same parent as self
        :raises IndexError: the next Page does not exist
        """
        return self.sister(1)

    @property
    def next_node(self):
        """
        Finds the next sister, or uses iteration to find the next Page
        :return (Page): the next Page in sequence
        :raises IndexError: the next Page does not exist
        """
        if self.has_children:
            return self.children[0]
        else:
            try:
                next_node = self.next_sister
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
            right = node.next_sister
            return right
        except IndexError:
            right = self.next_node_iter(node.parent)
        return right

    @property
    def descendants(self):
        """
        All the descendants of self, using iteration
        :return (Page{}):
        """
        descendants = set(self.children)
        for child in self.children:
            descendants.update(child.descendants)
        return descendants

    @property
    def cousins(self):
        """
        Taking a sub-hierarchy as the descendants of a Page, cousins are Pages at the same point as self, but in different sub-hierarchies.
        """
        node = self
        indices = deque()
        while node.parent is not None:
            indices.appendleft(node.parent.children.index(node))
            node = node.parent
        indices.popleft()
        cousins = []
        for child in node.children:
            cousin = child
            for index in indices:
                try:
                    cousin = cousin.children[index]
                except (IndexError, AttributeError):
                    cousin = Page(name=None)
            cousins.append(cousin)
        return cousins

    @property
    def family(self):
        """
        Return all of self, descendants, sisters, ancestors, and sisters of ancestors
        :rtype (Page{}):
        """
        family = set([])
        for ancestor in self.ancestors:
            family.update(ancestor.children)
        family.update(self.descendants)
        return family

    @property
    def fullUrlForm(self):
        """
        :return (str): the name and extension of the Page in a form suitable for URLs
        """
        # extension = '/index' if not self.isLeaf else ''
        return '{0}{1}.html'.format(self.urlform, '/index' if not self.isLeaf else '')

    @property
    def folder(self):
        """
        :return (str): the folder in which the Page should appear, or an empty string if Page is the root
        """
        if self.level:
            text = "/".join([i.urlform for i in self.ancestors[1:-1]]) + '/'
            text += self.urlform + '/' if not self.isLeaf else ''
            return text if self.level != 1 else self.urlform + '/'
        else:
            return ''

    def link(self, extend=True):
        """
        :return (str): a link to self of the form 'highlulani/morphology/index.html'
        """
        if extend:
            return self.folder + (self.fullUrlForm if self.isLeaf else 'index.html')
        else:
            return self.folder + (self.urlform if self.isLeaf else 'index')

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
            ancestors = {'self': self.ancestors, 'destination': destination.ancestors}
            isDirect = destination in ancestors['self']
            # :variable (int) common: the number of nodes common to both source and destination ancestries
            try:
                common = [i != j for i, j in zip(*[x for x in ancestors.values()])].index(True)
            except ValueError:
                common = min(map(len, ancestors.values()))
            # :variable (int) up: the number of levels the common ancestor is above the source
            # :variable (str) down: the hyperlink address from the common ancestor to the descendant
            if destination == self.root:
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
        url_id = Page(re.sub(r'\(.*?\)', '', name), markdown=self.markdown).urlform
        if url_id:
            return '<h{0} id="{1}">{2}</h{0}>\n'.format(str(level), url_id, name)
        else:
            return '<h{0}>{1}</h{0}>\n'.format(str(level), name)

    @property
    def title(self):
        """
        :return (str): its own name, suitable for HTML titles
        """
        # remove tags from names
        return re.sub(r'[[<].*?[]>]', '', self.name)

    @property
    def category_title(self):
        """
        :return (str): A title of the form 'High Lulani Verbs'
        """
        if self.level < 2:
            return self.title
        else:
            matriarch = self.ancestors[1]
            if matriarch.name in ('Introduction', 'Appendices'):
                return self.title
            else:
                return matriarch.title + ' ' + self.title

    @property
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
                try:
                    heading, rest = line.split('\n', 1)
                except ValueError:
                    raise ValueError(line)
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

    @property
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

    @property
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

    @property
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
            for page in self.genealogy:
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

    @property
    def links(self):
        """
        :return (str):
        """
        output = '''<ul>
                  <li class="link"><a href="http://www.tinellb.com">&uarr; Main Page</a></li>
                  <li class="link">$out$</li>
                </ul>
                <ul><li{0}>{1}</li>
                  <form id="search">
                    <li class="search">
                      <input type="text" name="term"></input> <button type="submit">Search</button>
                    </li>
                  </form>
                $links$
                </ul>'''.format(' class="normal"' if self == self.root else '',
                                self.hyperlink(self.root))
        for item, link in ( ['Grammar', 'grammar'],
                            ['Dictionary', 'dictionary']):
            if item != self.root.name:
                output = output.replace('$out$', '<a href="http://{0}.tinellb.com">{1} &rarr;</a>'.format(link, item), 1)
        return output

    @property
    def family_links(self):
        links = ''
        level = 0
        family = self.family
        for page in self.genealogy:
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
        return self.links.replace('$links$', links)

    @property
    def cousin_links(self):
        links = ''
        level = 0
        family = self.family
        for page in self.genealogy:
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
        categories = [node.name for node in self.elders]
        cousins = self.cousins
        for cousin, category in zip(cousins, categories):
            if cousin.name and cousin is not self:
                links += '<li>{0}</li>\n'.format(self.hyperlink(cousin, category))
        links += '</ul><ul>'
        return self.links.replace('$links$', links)

    @property
    def elder_links(self):
        links = '<ul>'
        for elder in self.elders:
            links += '<li{0}>{1}</li>'.format(
                (' class="normal"' if elder in [self, self.parent] else ''), self.hyperlink(elder))
        return self.links.replace('$links$', links + '</ul>')

    @property
    def nav_footer(self):
        div = '<div>\n{0}\n</div>\n'
        if self.previous:
            output = div.format(self.hyperlink(self.previous, '&larr; Previous page'))
        else:
            output = div.format(self.hyperlink(self.root, '&uarr; Return to Menu'))
        try:
            output += div.format(self.hyperlink(self.next_node, 'Next page &rarr;'))
        except IndexError:
            output += div.format(self.hyperlink(self.root, 'Return to Menu &uarr;'))
        return output

    @property
    def copyright(self):
        try:
            date = datetime.strptime(max(re.findall(r'(?<=&date=)\d{8}', self.content)), '%Y%m%d')
        except ValueError:
            return ''
        suffix = "th" if 4 <= date.day <= 20 or 24 <= date.day <= 30 else ["st", "nd", "rd"][date.day % 10 - 1]
        output = datetime.strftime(date, '&copy;%Y&nbsp;Ryan&nbsp;Eakins. Last&nbsp;updated:&nbsp;%A,&nbsp;%B&nbsp;%#d' + suffix + ',&nbsp;%Y.')
        return output

    def publish(self, template):
        """
        Create / modify an .html file.
        :param template (Template): the basic template to be published against
        :param template (str): the basic template to be published against
        """
        try:
            page = template.template
        except AttributeError:
            # template is a string
            page = template
        for (section, function) in [
            ('{title}', 'title'),
            ('{stylesheet}', 'stylesheet_and_icon'),
            ('{search-script}', 'search_script'),
            ('{content}', 'contents'),
            ('{toc}', 'toc'),
            ('{family-links}', 'family_links'),
            ('{cousin-links}', 'cousin_links'),
            ('{elder-links}', 'elder_links'),
            ('{nav-footer}', 'nav_footer'),
            ('{copyright}', 'copyright'),
            ('{category-title}', 'category_title')
        ]:
            if page.count(section):
                page = page.replace(section, getattr(self, function))
        with ignored(os.error):
            os.makedirs(self.folder)
        with open(self.link(), "w") as f:
            page = re.sub('\x05.*?(\x06\x06*)', '', page)
            page = re.sub(r'\x07', '', page)
            page = re.sub(r'&date=\d{8}', '', page)
            f.write(page)

    def delete_htmlfile(self):
        os.remove(self.link())

    def analyse(self, markdown):
        wordlist = {}
        content = self.content[2:]
        """remove tags, and items between some tags"""
        content = re.sub(r'\[\d\]|<(ipa|high-lulani|span).*?</\1>|<.*?>', ' ', content)
        """remove datestamps"""
        content = re.sub(r'&date=\d{8}', '', content)
        """change punctuation to paragraph marks, so that splitlines works"""
        content = re.sub(r'[!?.|]', '\n', content)
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
        content = re.sub(r'\'\"|[!?`\"/{}\\;-]|\'($| )|\[.*?\]|&nbsp', ' ', content)
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
