# pylint: disable=C0103, W0611, C0305, C0304, C0301

from smeagol.conversion.text_tree.node import Node
from smeagol.editor.interface.interface import Interface

i = Interface('c:/users/ryan/tinellbianlanguages/grammar/data/config.smg', server=False)
k = i.site['A Grammar of the Tinellbian Languages', 'Languages', 'Lulani', 'High', 'Sample Text']
q = k.text

def para(p, inter):
    t = 'tinellbian@x-tlb-hl'
    node = Node(inter, t)
    node.add(''.join([m.middle_text for m in p.nodes if m.name == t]).replace('。。', '。'))
    return node


sample = [n for n in q.nodes if n.name == 'summary|sample'][0]
interlinear = [n for n in q.nodes if n.name == 'interlinear'][0]
sample.children = [*(para(paragraph, interlinear), '\n') for paragraph in interlinear.children if isinstance(paragraph, Node)][:-1]
k.text = q
i.save_site()