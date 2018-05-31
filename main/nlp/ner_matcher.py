from .. import nlp_spacy as nlp


class EntityMatcher(object):

    def __init__(self, mode='spacy'):
        if mode == 'spacy':
            self.nlp = nlp

    def get_matches(self, text):
        doc = self.nlp(text)
        for ele in doc.ents:
            yield ele.text, ele.start, ele.end, ele.label_
        '''
        spans = list(doc.ents) + list(doc.noun_chunks)
        for span in spans:
            span.merge()
        for ele in doc:
            if ele.ent_type_:
                yield ele.text, ele.ent_type_
        '''

    def get_entity_relation(self, text):
        doc = nlp(text)
        relations = []
        # for ele in filter(lambda w: w.ent_type_ in ['MONEY', 'DATE'], doc):
        for ele in doc:
            if ele.dep_ in ('attr', 'dobj'):
                subject = [w for w in ele.head.lefts if w.dep_ == 'nsubj']
                if subject:
                    subject = subject[0]
                    relations.append((subject, ele))
            elif ele.dep_ == 'pobj' and ele.head.dep_ == 'prep':
                relations.append((ele.head.head, ele))
        return relations  #  r1.text, r2.ent_type_, r2.text


if __name__ == '__main__':
    text = "Net income was $9.4 million compared to the prior year of $2.7 million. The package delivery company said Friday that it will raise total compensation by more than $200 million, citing recent tax reform legislation."
    for ele in EntityMatcher().get_matches(text):
        print(ele)
