class FlatName:
    def __init__(self, name, markdown):
        """
        'flattens' the name to only include letters aiu'pbtdcjkgmnqlrfsxh
        Smallest number comes earlier in the ordering.
        """
        alphabet = "aiu'pbtdcjkgmnqlrfsxh"
        punctuation = "-'#"
        radix = len(punctuation)

        name = urlform(name, markdown)
        score = 0
        double_letter = re.compile(r'([{0}])\1'.format(alphabet))
        name = re.sub(double_letter, r'\1#', name, 1)

        for points, pattern in enumerate(punctuation):
            score += score_pattern(name, pattern, radix, points+1)
            name = name.replace(pattern, '*')
            name = name.replace('*', '')
            self.name = name
            self.score = score

    def score_pattern(word, pattern, radix, points):
        """
        Calculate a score for each occurance of a pattern in the word.
        More points are given for later occurances.

        :param word: The word being tested.
        :param pattern: The pattern being searched for.
        :param points: The number of points given for this pattern.
        """
        total = sum([points * radix**index for index in pattern_indices(word, pattern)])
        return total

    def pattern_indices(word, pattern):
        index = -1
        while True:
            try:
                index = word.index(pattern, index+1)
                yield index+1
            except ValueError:
                raise StopIteration
