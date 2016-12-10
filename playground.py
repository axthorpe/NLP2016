from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
import numpy as np
from nltk.corpus import brown

ngram = defaultdict(lambda: defaultdict(int))
ngram_rev = defaultdict(lambda: defaultdict(int)) #reversed n-grams
corpus = " ".join(str(word) for word in brown.words())

for sentence in nltk.sent_tokenize(corpus):
    tokens = map(str.lower, nltk.word_tokenize(sentence))
    for token, next_token in zip(tokens, tokens[1:]):
        ngram[token][next_token] += 1
    for token, rev_token in zip(tokens[1:], tokens):
        ngram_rev[token][rev_token] += 1
for token in ngram:
    total = np.log(np.sum(ngram[token].values()))
    total_rev = np.log(np.sum(ngram_rev[token].values()))
    ngram[token] = {nxt: np.log(v) - total 
                    for nxt, v in ngram[token].items()}
    ngram_rev[token] = {prv: np.log(v) - total_rev 
                    for prv, v in ngram_rev[token].items()}

"""
ngram_file = open('ngram.pickle', 'w')
cpickle.dump(ngram, ngram_file)
ngram_file.close()

ngram_rev_file = open('ngram_rev.pickle', 'w')
cpickle.dump(ngram_rev, ngram_rev_file)
ngram_rev_file.close()
"""