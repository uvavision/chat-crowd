from spacy.matcher import PhraseMatcher
import time
import plac
import ujson
import spacy
import os
from .. import nlp_spacy as nlp
from .. import APP_GAZETTEER


def read_gazetteer(in_json):
    lst = ujson.load(open(in_json))
    for ele in lst:
        phrase = nlp(ele)
        yield phrase


class GazetteerMatcher(object):

    def __init__(self, mode="spacy", in_dir=APP_GAZETTEER):
        if mode == 'spacy':
            self.matcher = PhraseMatcher(nlp.tokenizer.vocab)
            for fn in os.listdir(in_dir):
                phrase_type = fn.split('.')[0]
                for phrase in read_gazetteer(os.path.join(in_dir, fn)):
                    self.matcher.add(phrase_type, None, phrase)

    def get_matches_spacy(self, texts, max_length=6):
        for text in texts:
            doc = nlp.tokenizer(text)
            for w in doc:
                _ = doc.vocab[w.text]
            matches = self.matcher(doc)
            for ent_id, start, end in matches:
                yield doc[start:end].text, start, end


if __name__ == '__main__':
    in_dir = '../data/gazetteers'
    texts = ['I want to find an apartment in Columbia St Waterfront District.']
    sm = GazetteerMatcher(in_dir)
    for ele in sm.get_matches_spacy(texts):
        print(ele)
