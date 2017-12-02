import re
import json

class Analysis:
    def __init__(self, words, sentences, urls=None, names=None):
        """
        :param words (dict): {term: locations}
        """
        self.words = words
        self.sentences = sentences
        self.urls = urls or []
        self.names = names or []
        self.string = json.dumps(dict(terms=self.words,
                                      sentences=self.sentences,
                                      urls=self.urls,
                                      names=self.names))

    def __str__(self):
        return self.string
