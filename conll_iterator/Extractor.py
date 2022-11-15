from collections import Counter

from nltk import RegexpParser
from nltk.tree import Tree


def _fromtree(tree, extracted=list(), i=0):
    if i == len(tree):
        return
    node = tree[i]
    if type(node) == Tree:
        if node.label() == 'CAND':
            extracted.append(tuple(node.leaves()))
        return _fromtree(node, extracted), \
            _fromtree(tree, extracted, i+1)
    else:
        return _fromtree(tree, extracted, i+1)


class Extractor:
    def __init__(
            self, 
            patterns: str, 
            dictionary: dict = None
                ):

        self.parser = RegexpParser(patterns)
        self.dictionary = dictionary
    
    def _tagsent(self, sent):
        newsent = list()
        for w, pos in sent:
            newsent.append((w, self.dictionary.get(w, pos)))
        return newsent

    def extract(self, iterator):
        """Extract all the sequences matching a pattern.

        Parameters
        ----------
        iterator: iterable
            The iterator of sentences from which to extract the sequences.
        
        Yields
        ------
        list:
            A list containing the extracted sequences from the sentence (list
            is empty if no sequences match the patterns).

        """
        for item in iterator:
            if self.dictionary:
                item = self._tagsent(item)
            chunks = [item[i:i + 100] for i in range(0, len(item), 100)]
            for c in chunks:
                tree = self.parser.parse(c)
                extracted = list()
                _fromtree(tree, extracted)
                yield extracted
    
    def count(self, iterator) -> Counter:
        """Counts all the sequences matching a pattern.

        Parameters
        ----------
        iterator: iterable
            The iterator of sentences from which to extract the sequences.
        
        Returns
        ----------
        Counter:   
            the counter with the frequency of sequences matching the patterns.
        """
        counter = Counter()
        for extr in self.extract(iterator):
            counter.update(extr)        
        return counter
        
        

