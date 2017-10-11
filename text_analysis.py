class TextAnalysis:
    def __init__(self, words, sentences, urls=None, names=None):
        """
        :param words (dict): {term: locations}
        """
        self.words = words
        self.sentences = sentences
        self.urls = urls if urls else []
        self.names = names if urls else []

    def __str__(self):
        # Replace single quotes with double quotes, and insert line breaks, to comply with JSON formatting
        words = str(self.words)
        words = re.sub(r"(?<=[{ ])'|'(?=:)", '"', str(words))
        words = re.sub(r'(?<=},) ', '\n', words)
        # Create each section of the JSON
        words = '"terms": {0}'.format(words)
        sentences = '"sentences":["{0}"]'.format('",\n "'.join(self.sentences))
        urls = '"urls":["{0}"]'.format('",\n "'.join(self.urls))
        names = '"names":["{0}"]'.format('",\n "'.join(self.names))
        return '{{{0}}}'.format(',\n'.join([words, sentences, urls, names]))
