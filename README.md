CONTENTS OF THIS FILE
---------------------

*   Introduction
*   Setup
*   Getting started

INTRODUCTION
------------

A simple iterator that reads conll_files (https://universaldependencies.org/format.html)

SETUP
-----
```
pip install git+https://github.com/nicolaCirillo/conll_iterator.git
```

GETTING STARTED
---------------

```
## import
from conll_iterator import ConllIterator

## Creates an object (ConllIterator) that iterates over sentences of a ConLL file.
corpus = "sample/sample_corpus.conllu"

# dictionary with features and their position in the ConLL lines.
# format: {<feature, str>: <position, int>}  
idx_dict = {"id": 0, "surface": 1, "lemma": 2, "pos": 3}

sentences = ConllIterator(corpus, idx_dict, codec='utf8')

# set_itermode changes the behaviour of the iterator.
sentences.set_itermode('sent', keys=["surface", "lemma", "pos"], ignore_compound=True)
```
