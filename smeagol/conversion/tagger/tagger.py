from .tag import Tag


class Tagger:
    def __init__(self, tags):
        self.tags = {t.name: t for t in [Tag(i, **t) for i, t in enumerate(tags)]}