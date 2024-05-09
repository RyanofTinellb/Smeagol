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
    obj = recurse(directory, names)
    yield from generator(obj, names)


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
    except ValueError:
        return [get_name(directory)]


def _next_entry(directory, names):
    name = names.pop()
    obj = recurse(directory, names)
    index = get_index(obj, name)
    try:
        return [*names, get_name(obj[index+1])]
    except IndexError:
        return next_entry(directory, names, True)


def previous_entry(directory, names):
    name = names.pop()
    obj = recurse(directory, names)
    try:
        index = get_index(obj, name) - 1
    except ValueError:
        return youngest_grandchild(directory, [name])
    if index:
        return _youngest_grandchild(obj[index])
    return names


def youngest_grandchild(directory, names):
    obj = recurse(directory, names)
    return _youngest_grandchild(obj)


def _youngest_grandchild(obj):
    if len(obj) == 1:
        return obj
    return _youngest_grandchild(obj[-1])
