CONTENTS OF THIS FILE
---------------------

*   Introduction
*   Setup
*   Getting started
*   Examples

INTRODUCTION
------------

A simple iterator that reads conll and conllu files (https://universaldependencies.org/format.html) without keeping them in memory. It can iterate over words, sentences, or documents.

SETUP
-----
via pip:
```
pip install conll-iterator
```
via github:
```
pip install git+https://github.com/nicolaCirillo/conll_iterator.git
```

GETTING STARTED
---------------

```
from conll_iterator import ConllIterator
from tqdm import tqdm


sentences = ConllIterator('sample/sample_corpus.conllu', 
                         fields=['form', 'upos'], 
                         mode='sentences', 
                         join_char='/')

for s in tqdm(sentences):
    # do something
```

EXAMPLES
--------------

### Training word2vec

```
from gensim.models import Word2Vec
from tqdm import tqdm
from conll_iterator import ConllIterator

sentences = ConllIterator('sample/sample_corpus.conllu', fields=['lemma', 'upos'], mode='sentences', join_char='/')
w2v_parameters = {'vector_size': 25, 'window': 5, 'min_count': 1, 'sg': 1, 'epochs': 15}
model = Word2Vec(tqdm(sentences), workers=5, **w2v_parameters)
model.save('sample_w2v')
word_vectors = model.wv
similar = list(zip(*word_vectors.most_similar('Pecorino/PROPN')[:10]))[0]
print("Most similar words to Pecorino/PROPN:")
print(similar)
```

### Keyword extraction via tf-idf

```
from itertools import chain
from collections import Counter

docs = ConllIterator('sample/sample_corpus.conllu', fields=['lemma', 'upos'], lower=['lemma'], mode='documents')
doc_tf = list()
df = Counter()
allowed_pos = ['NOUN', 'PROPN','VERB', 'ADJ']
for d in docs:
    tokens = list(chain(*d))
    tokens = [t[0] for t in tokens if t[1] in allowed_pos]
    tf = Counter(tokens)
    df.update(set(tokens))
    doc_tf.append(tf)

doc_keywords = list()
for d in doc_tf:
    doc_tfidf = [(w, d[w]/df[w]) for w in d]
    doc_tfidf = sorted(doc_tfidf, key=lambda x:x[1], reverse=True)
    doc_keywords.append(list(zip(*doc_tfidf[:10]))[0])

for i, k in enumerate(doc_keywords[:20]):
    print('keywords of doc {}:'.format(i+1), '; '.join(k))
```
