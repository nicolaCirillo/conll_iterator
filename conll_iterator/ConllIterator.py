# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 08:01:55 2020

@author: nicol
"""
import codecs
from os import path
import json
from typing import List, Optional #,Literal

class _EndOf:
    def __init__(self, val):
        self.val = val

CONLLU = ['id', 'form', 'lemma', 'upos', 'xpos', 'feats', 'head', 
                   'deprel', 'deps', 'misc']

WAC = ['form', 'lemma', 'pos', 'id', 'head', 'misc']


class ConllIterator:
    """Iterator for conll files.

    A simple iterator that yields words, sentences or documents contained in a
    conll file by incrementally reading it. 
    The iterator also automatically generates a json file with the number of 
    word, sentences and documents contained in the corpus.

    Parameters
    ----------
    corpus_file: str
        Path to the conll file.
    fields: list of strings, default=CONNLU
        The fields that are returned for each token. e.g. ['form', 'lemma'] 
        will return only the form and the lemma of each token.
    mode: ['tokens', 'sentences', 'documents'], default=sentences
        Controls the behaviour of the iterator:
            'tokens': each element yelded is a token.
            'sentences': each element yelded is a sentence (list of tokens).
            'documents': each element yelded is a document (list of sentences).
    lower: list of strings, default=[]
        The list of feature provided to this argument are lowecased.
    join_char, optional: str
        If provided, the fields of each token are joined with the string 
        provided. Otherwise, a token is a tuple of its fields. e.g. '_' 
        [the_the_DET, dog_dog_NOUN, barks_bark_VERB]
    columns, list of strings, default=CONNLU
        The list of the columns of the conll file. This parameter could be
        changed to read other tab separated formats. 
    codec: str, default='utf8'
        The codec used to decode the conll file.

    Examples
    ----------
    >>> sentences = ConllIterator('my_conll', ['form', 'upos'])
    >>> for s in sentences:
    ...     print(s)
    [('the', 'DET'), ('modification', 'NOUN'), [...], ('»', 'PUNCT')]
    [('eighth', 'NUM'), ('month', 'NOUN'), [...], ('.', 'PUNCT')]
    [...]
    [('both', 'PRON'), ('equated', 'VERB'), [...], ('.', 'PUNCT')]

    >>> sentences = ConllIterator('my_conll', ['form', 'upos'], join_char='/')
    >>> for s in sentences:
    ...     print(s)
    ['the/DET', 'modification/NOUN', [...], '»/PUNCT']
    ['eighth/NUM', 'month/NOUN', [...], './PUNCT']
    [...]
    ['both/PRON', 'equated/VERB', [...], './PUNCT']

    """

    def __init__(
            self, 
            corpus_file: str,
            fields: List[str] = CONLLU,
            #mode: Literal['tokens', 'sentences', 'documents'] = 'sentences', 
            mode: str = 'sentences',  
            lower: List[str] = [], 
            join_char: str = False, 
            columns: List[str] = CONLLU, 
            codec: str = 'utf8'
                ):

        self.codec = codec
        self.filename = corpus_file
        self.idx_dict = {c: i for i, c in enumerate(columns)}
        self.lower = lower
        self.mode = mode
        self.fields = fields
        self.join_char = join_char
        self._open_corpus()
        self.counts = {'tokens': 0, 'sentences': 0, 'documents': 0}
        self.info_file = '.'.join(self.filename.split('.')[:-1]) + '_info.json'
        if path.exists(self.info_file):
            self._load_info()
        else:
            self.docs = None
            self.sentences = None
            self.tokens = None
            self._save_info()
    
    def _open_corpus(self):
        self.corpus = codecs.open(self.filename, 'r', self.codec)
    
    def close(self):
        self.corpus.close()

    def _save_info(self):
        with codecs.open(self.info_file, 'w', 'utf8') as fileout:
            json.dump(self.counts, fileout)

    def _load_info(self):
        with codecs.open(self.info_file, 'r', 'utf8') as filein:
            info = json.load(filein)
        self.sentences = info['sentences']
        self.tokens = info['tokens']
        self.docs = info['documents']
    
    def _get_value(self, field, row):
        idx = self.idx_dict[field]
        try:
            if field in self.lower:
                return row[idx].lower()
            else:
                return row[idx]
        # not  very professional :(
        except IndexError:
            return "_"

    @staticmethod
    def _is_comment(line):
        if line.startswith('#'):
            return True
        else:
            return False

    def _parse_line(self, line):
        if self._is_comment(line):
            if line.startswith('# newdoc'):
                self.counts['documents'] += 1
                return _EndOf('D')
            else: return None
        if line == '\n':
            self.counts['sentences'] += 1
            return _EndOf('S')
        else:
            self.counts['tokens'] += 1
            line = line.strip()
            row = line.split('\t')
            values = tuple([self._get_value(f, row) for f in self.fields])
            if self.join_char:
                values = self.join_char.join(values)
            return values

    def _next_token(self):
        line = next(self.corpus)
        while line:
            line = self._parse_line(line)
            if line is None:
                pass
            elif type(line) == _EndOf:
                pass
            else: return line
            line = next(self.corpus)

    def _next_sentence(self):
        sent = list()
        line = next(self.corpus)
        while line:
            line = self._parse_line(line)
            if line is None:
                pass
            elif type(line) == _EndOf:
                if line.val == 'S' and sent:
                    return sent
            else: sent.append(line)
            line = next(self.corpus)

    def _next_doc(self):
        doc = list()
        sent = list()
        line = next(self.corpus)
        while line:
            line = self._parse_line(line)
            if line is None:
                pass
            elif type(line) == _EndOf:
                if line.val == 'D' and doc:
                    return doc
                elif line.val == 'S' and sent:
                    doc.append(sent)
                    sent = list()
            else: sent.append(line)
            try:
                line = next(self.corpus)
            except StopIteration:
                if doc: return doc
    
    def _get_next(self):
        if self.mode == 'tokens':
            return self._next_token()
        elif self.mode == 'sentences':
            return self._next_sentence()
        elif self.mode == 'documents':
            return self._next_doc()
        else: raise NotImplementedError

    def __next__(self):
        return self._get_next()

    def __iter__(self):
        self.counts = {'tokens': 0, 'sentences': 0, 'documents': 0}
        while self.corpus:
            try:
                yield next(self)
            except StopIteration:
                break
        self._save_info()
        self._load_info()
        self._open_corpus()

    def __len__(self):
        if self.mode == 'tokens':
            return self.tokens
        if self.mode == 'sentences':
            return self.sentences
        if self.mode == 'documents':
            return self.docs

    def sample(self, n=100):
        """Prints the first n elements yielded by this iterator.

        Parameters
        ----------
        n: int, default=100
            The number of elements to be printed.

        """
        for i, item in enumerate(self):
            print(item)
            if i >= n:
                break

    def sentences2text(self, filename: str, join_char: str):
        """Save the sentences yielded by this iterator into a text file.

        Parameters
        ----------
        filename: str
            The path to the output file
        join_char: str,
            Each token will be represented as a string in which the tokens's
            fields are joined with the string provided.

        """
        tmp_mode, tmp_join_char = self.mode, self.join_char
        self.mode, self.join_char = "sentences", join_char
        with codecs.open(filename, 'w', 'utf8') as fileout:
            for sent in self:
                fileout.write(' '.join(sent) + '\n')
        self.mode, self.join_char =  tmp_mode, tmp_join_char
