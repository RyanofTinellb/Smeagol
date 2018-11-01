from cwsmeagol.utils import urlform

def find(node, location):
    if len(location) == 1:
        return node['children'][location[0]]
    elif len(location) > 1:
        try:
            return find(node['children'][location[0]], location[1:])
        except TypeError:
            raise TypeError(type(node))
    else:
        return node


def sister(root, location, index):
    if not len(location):
        raise IndexError('No such sister')
    children = find(root, location[:-1])['children']
    if len(children) > location[-1] + index >= 0:
        location[-1] += index
        return location
    else:
        raise IndexError('No such sister')


def previous_sister(node, location):
    return sister(node, location, -1)


def next_sister(node, location):
    return sister(node, location, 1)


def num_children(root, location):
    return len(find(root, location)['children'])


def has_children(root, location):
    return num_children(root, location) > 0


def is_leaf(root, location):
    return not has_children(root, location)


def next(root, location, _seen_children=False):
    if not _seen_children and has_children(root, location):
        location += [0]
        return location
    else:
        try:
            return next_sister(root, location)
        except IndexError:
            location.pop()
            next(root, location, _seen_children=True)


def previous(root, location):
    try:
        _last_grandchild(root, previous_sister(root, location))
        return location
    except IndexError:
        if len(location):
            location.pop()
            return location
        else:
            raise IndexError('No more nodes')


def _last_grandchild(node, location):
    children = num_children(node, location)
    if children:
        location += [children - 1]
        _last_grandchild(node, location)


def ancestors(root, location):
    for i in xrange(len(location) - 1):
        yield tuple(location[:i+1])


def cousin_degree(source, destination):
    try:
        return [i != j for i, j in zip(source, destination)].index(True) + 1
    except ValueError:
        return min(map(len, [source, destination]))


def startswith(location, other):
    return list(location[:len(other)]) == list(other)


def unshared_ancestors(root, one, other):
    source, destination = [set(ancestors(root, location))
            for location in (one, other)]
    for ancestor in sorted(source - destination):
        yield ancestor
    yield one


def matriarchs(root, source):
    for i, v in enumerate(root['children']):
        yield (i,)
    else:
        raise StopIteration


def sisters(root, source):
    if len(source) == 0:
        raise StopIteration
    location = list(source[:-1])
    for child in xrange(num_children(root, location)):
        yield tuple(location + [child])


def aunts(root, source):
    for ancestor in ancestors(root, source):
        for sister in sisters(root, ancestor):
            yield tuple(sister)


def descendants(root, location):
    generation = len(location)
    location = location[:]
    next(root, location)
    while len(location) <> generation:
        yield tuple(location)
        try:
            next(root, location)
        except IndexError:
            raise StopIteration


def reunion(root, location, *groups):
    relatives = set().union(*[group(root, location) for group in groups])
    for relative in sorted(relatives):
        yield relative


def family(root, location):
    for relative in reunion(root, location, aunts, descendants, sisters):
        yield relative


def name(node, location):
    return find(node, location)['name']


def url(root, location):
    return urlform(name(root, location))


def text(node, location):
    return find(node, location)['text']


def date(node, location):
    return find(node, location)['date']
