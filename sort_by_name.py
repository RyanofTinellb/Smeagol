from sites import Dictionary
from smeagol.utils import dump
import json

d = Dictionary()
r = d.root
for mat in r.daughters:
    kids = list(mat.daughters)
    kids.sort()
    kids = map(lambda x: x.find(), kids)
    mat.children = kids
d.update_source()
