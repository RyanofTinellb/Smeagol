'''
Functions that take in a directory list, and a list of names, and
spit back its family as lists of strings. This list of strings can
then be fed into Nodes to get them as Node/Entry/Page.
'''


def get_name(obj):
    return obj if isinstance(obj, str) else obj[0]


def get_index(obj, name):
    for i, elt in enumerate(obj):
        if elt[0] == name:
            return i
    raise ValueError(f'{get_name(obj)} has no item {name}')


def recurse(obj, names):
    names = names[1:]
    if not names:
        return obj
    index = get_index(obj, names[0])
    return recurse(obj[index], names)


def generator(obj, names):
    for elt in obj[1:]:
        yield [*names, get_name(elt)]


def parent(names) -> list[str]:
    return names[:-1]


def lineage(names):
    names = names.copy()
    while len(names) > 1:
        yield names
        names.pop()


def children(directory, names) -> list[str]:
    obj = recurse(directory, names)
    yield from generator(obj, names)


def generation(directory: list[list[str]], names: list[str], number: int):
    if not number:
        yield [names[0]]
        return
    if number > len(names):
        raise IndexError(f'Entry has no generation {number}')
    obj = recurse(directory, names[:number])
    yield from generator(obj, names[:number])


def siblings(directory, names):
    names = parent(names)
    if not names:
        return
    obj = recurse(directory, names)
    yield from generator(obj, names)


def aunts(directory, names):
    for ancestor in lineage(names):
        yield from siblings(directory, ancestor)


def descendants(directory, names):
    obj = recurse(directory, names)
    for elt in obj[1:]:
        yield from _rec(elt, names)


def _rec(obj, names=None):
    names = [*(names or []), obj[0]]
    yield names
    for elt in obj[1:]:
        yield from _rec(elt, names)


def next_entry(directory, names, already: bool = False):
    if already:
        return _next_entry(directory, names)
    obj = recurse(directory, names)
    try:
        return [*names, get_name(obj[1])]
    except IndexError:  # has no children
        return sibling(directory, names)


def sibling(directory, names):
    try:
        return _next_entry(directory, names)
    except ValueError as e:
        raise IndexError('No more nodes!') from e


def _next_entry(directory, names):
    try:
        return next_sister(directory, names)
    except IndexError:
        return next_entry(directory, names, True)


def sister(directory, names, offset):
    name = names.pop()
    obj = recurse(directory, names)
    index = (get_index(obj, name) if name else 0) + offset
    if 0 < index < len(obj):
        return [*names, get_name(obj[index])]
    raise IndexError(f'No such sister {index}')


def next_sister(directory, names):
    return sister(directory, names, +1)


def previous_sister(directory, names):
    return sister(directory, names, -1)


def previous_entry(directory, names):
    name = names.pop()
    obj = recurse(directory, names)
    try:
        index = get_index(obj, name) - 1
    except ValueError as e:
        raise IndexError('No more nodes') from e
    if index:
        youngest_grandchild(obj[index], names)
    return names  # first child goes to parent


def youngest_grandchild(obj, names):
    names.append(get_name(obj))
    if len(obj) == 1:
        return
    youngest_grandchild(obj[-1], names)
