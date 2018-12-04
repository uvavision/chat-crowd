from .. import nlp_spacy as nlp
from ..nlp.gazetteer_matcher import GazetteerMatcher
from ..nlp.ner_matcher import EntityMatcher

srl_link = 'https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.02.27.tar.gz'
from allennlp.service.predictors import Predictor


def srl(text):
    results = predictor.predict(sentence=text)


def domain_entity_matcher(text):
    gm = GazetteerMatcher()
    doc = nlp(text)
    return doc, gm.get_matches_spacy([text])


def ner_matcher(text):
    em = EntityMatcher()
    doc = nlp(text)
    return doc, em.get_matches(text)
