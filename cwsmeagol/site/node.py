"""
Helper functions for navigating a Site
"""

def find(node, location):
    if len(location) == 1:
        return node['children'][location[0]]
    elif len(location) > 1:
        try:
            return find(node['children'][location[0]], location[1:])
        except TypeError:
            raise TypeError(node)
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

def has_children(root, location):
    return num_children(root, location) > 0

def num_children(root, location):
    return len(find(root, location)['children'])

def next(root, location, _seen_children=False):
    if not _seen_children and has_children(root, location):
        location += [0]
        return find(root, location)
    elif len(location) == 0:
        raise IndexError('No more nodes')
    else:
        try:
            return next_sister(root, location)
        except IndexError:
            location.pop()
            return next(root, location, _seen_children=True)

def previous(root, location):
    try:
        return find(root,
                _last_grandchild(root, previous_sister(root, location)))
    except IndexError:
        if len(location):
            location.pop()
            return find(root, location)
        else:
            raise IndexError('No more nodes')

def _last_grandchild(node, location):
    children = num_children(node, location)
    if children:
        location += [children - 1]
        return _last_grandchild(node, location)
    else:
        return location
