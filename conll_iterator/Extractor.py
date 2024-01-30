from collections import Counter
import re
from nltk import RegexpParser
from nltk.tree import Tree
from lxml import etree as ET


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
    

    def extract(self, iterator, concordance=False):
        """Extract all the sequences matching a pattern.

        Parameters
        ----------
        iterator: iterable
            The iterator of sentences from which to extract the sequences.
        
        concorance: bool, default=False
            If True, yields also the sentences containing the matching object
        
        Yields
        ------
        list:
            A list containing the extracted sequences from the sentence (list
            is empty if no sequence match the patterns).

        """
        for item in iterator:
            if self.dictionary:
                item = self._tagsent(item)
            chunks = [item[i:i + 100] for i in range(0, len(item), 100)]
            for c in chunks:
                tree = self.parser.parse(c)
                extracted = list()
                _fromtree(tree, extracted)
                if concordance:
                    yield extracted, " ".join(list(zip(*item))[0])
                else:
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

class DependencyExtractor(Extractor):
    def __init__(
            self, 
            xpaths: str,
            field = "lemma"
                ):

        self.xpaths = xpaths.strip().split("\n")
        self.field = field

    @staticmethod
    def _sort_item(item):
        return " ".join([x[1] for x in sorted(item, key=lambda x: int(x[0]))])
    
    @staticmethod
    def _sent2tree(sentence, fields):
        sent_elem = ET.Element("sentence")
        elements = dict()
        for word in sentence:
            w_dict = dict(zip(fields, word))
            w_elem = ET.Element("word", w_dict)
            elements[w_dict["id"]] = w_elem
        for id, e in elements.items():
            h = e.attrib["head"]
            if h == '0':
                sent_elem.append(e)
            elif h == id:
                pass
            else:
                elements[h].append(e)
        return sent_elem
    
    def _extract_word(self, path, tree, item=[]):
        find = ET.XPath(path)
        childs = find(tree)        
        inner_paths = re.findall("(?:\[| ).*?(word\[.*?\])(?= |\]$)", path)
        for c in childs:
            item.append((c.attrib["id"], c.attrib[self.field]))
            for path in inner_paths:
                path = './' + path
                self._extract_word(path, c, item)

    def _extract_seq(self, path, tree, output=[]):
        find = ET.XPath(path)
        childs = find(tree)
        for c in childs:
            item = [(c.attrib["id"], c.attrib[self.field])]
            inner_paths = re.findall("(?:\[| ).*?(word\[.*?\])(?= |\]$)", path)
            for p in inner_paths:
                p = './' + p
                self._extract_word(p, c, item)
            output.append(self._sort_item(item))
        return output
    
    def extract(self, iterator):
        for sentence in iterator:
            tree = self._sent2tree(sentence, iterator.fields)
            out = list()
            for p in self.xpaths:
                self._extract_seq(p, tree, out)
            yield out



