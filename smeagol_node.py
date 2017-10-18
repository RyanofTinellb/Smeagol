from collections import deque

class Node(object):
    """
    A node in the hierarchy
    """

    def __init__(self, parent=None):
        """
        :param parent (Node): the Node's immediate ancestor

        :attribute children (list): the Nodes beneath self
        :attribute level (int): how low the Node is on the hierarchy
        """
        self.parent = parent
        self.children = []
        self.level = self.generation - 1

    def insert(self, index=None):
        """
        Insert self into the Site as a child of its parent
        :pre: Self has a filled parent attribute
        :param index (int): the index number to be inserted at
        :param index (None): self is inserted in order
        :return (Node): the Node just inserted
        """
        try:
            self.parent.children.insert(index, self)
        except TypeError:   # index is None
            for index, node in enumerate(self.parent.children):
                number = index
                if self <= node:
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
        :return (Node): the top Node in the Site
        """
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    @property
    def genealogy(self):
        """
        Generates for every Node in the Site sequentially
        :yield (Node):
        :raises StopIteration:
        """
        node = self.root
        yield node
        while True:
            try:
                node = node.next_node
                yield node
            except IndexError:
                node = self.root
                raise StopIteration

    @property
    def elders(self):
        """
        The first generation in the Site
        :return (Node[]):
        """
        return self.root.children

    @property
    def ancestors(self):
        """
        Self and the direct ancestors of self, in order down from the root.
        :return (Node[]):
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
        :return (int): the generation number of the Node, with the root at one
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
        :return (Node): the previous Node if it has the same parent as self
        :raises IndexError: the previous Node does not exist
        """
        return self.sister(-1)

    @property
    def next_sister(self):
        """
        :return (Node): the next Node if it has the same parent as self
        :raises IndexError: the next Node does not exist
        """
        return self.sister(1)

    @property
    def next_node(self):
        """
        Finds the next sister, or uses iteration to find the next Node
        :return (Node): the next Node in sequence
        :raises IndexError: the next Node does not exist
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
        Iterates over the Site to find the next Node
        :return (Node): the next Node in sequence
        :raises IndexError: the next Node does not exist
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
        :return (Node{}):
        """
        descendants = set(self.children)
        for child in self.children:
            descendants.update(child.descendants)
        return descendants

    @property
    def cousins(self):
        """
        Taking a sub-hierarchy as the descendants of a Node, cousins are Nodes at the same point as self, but in different sub-hierarchies.
        """
        node = self
        indices = deque()
        while node.parent is not None:
            indices.appendleft(node.parent.children.index(node))
            node = node.parent
        try:
            indices.popleft()
        except IndexError:
            return []
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

    @property
    def family(self):
        """
        Return all of self, descendants, sisters, ancestors, and sisters of ancestors
        :rtype (Node{}):
        """
        family = set([])
        for ancestor in self.ancestors:
            family.update(ancestor.children)
        family.update(self.descendants)
        return family
