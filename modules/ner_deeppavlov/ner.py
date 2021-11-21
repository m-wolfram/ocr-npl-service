from deeppavlov import build_model
import nltk
from nltk import pos_tag
from nltk.tree import Tree
from nltk.chunk import conlltags2tree
from .result_prepare import form_result
from .settings import (
    ner_model_type,
    download_model
)


nltk.download('averaged_perceptron_tagger')
#ner_model = build_model(ner_model_type, download=download_model)
ner_model = build_model(ner_model_type, download=download_model)
#ner_model = build_model(ner_model_type, download=download_model)


class DPToken():
    """
    Class of entity token.
    Contains information about it's position in text(start, stop) and token's text.
    """
    __attributes__ = ['start', 'stop', 'text']

    def __init__(self, start, stop, text):
        self.start = start
        self.stop = stop
        self.text = text


class DPSpan():
    """
    Class of extracted entity.
    Contains information about it's position in text(start, stop) and entity's text.
    """
    __attributes__ = ['start', 'stop', 'type', 'text', 'tokens']

    def __init__(self, start, stop, type, text, tokens=None):
        self.start = start
        self.stop = stop
        self.type = type
        self.text = text
        self.tokens = tokens


def get_full_tag(tag):
    """
    Function returning full version of received tag.
    Example: LOC - LOCATION, PER - PERSON etc.
    """

    replacements = {
        "GPE": "LOCATION",
        "ORG": "ORGANIZATION"
    }

    new_tag = tag

    for old, new in replacements.items():
        new_tag = new_tag.replace(old, new)

    return new_tag


def get_entities(text, dp_model):
    """Function processes given text with deeppavlov model and returns tokens, tags and tokens offsets."""

    def _find_offsets(tokens, string):
        """Function returns spans of given tokens from string in this string."""

        tid = [list(e) for e in tokens]

        i = 0
        for id_token, token in enumerate(tid):

            while token[0] != string[i]:
                i += 1

            tid[id_token] = tuple((i, i + len(token)))

            i += len(token)

        return tid

    #  Recognizing text with deeppavlov.
    ner_res = dp_model([text])

    tokens = ner_res[0][0]
    tags = ner_res[1][0]
    offsets = _find_offsets(tokens, text)  # Getting offsets of each token.

    return tokens, tags, offsets


def form_entities_spans(tokens, tags, offsets, text=None):
    """
    Function transforms received from deeppavlov tokens, tags and offsets into more usefull format.
    Returns entities themselves.
    """

    #  Getting tree in order to make it possible to concatenate tokens that belong to a single entity.
    pos_tags = [pos for token, pos in pos_tag(tokens)]
    conlltags = [(token, pos, tg) for token, pos, tg in zip(tokens, pos_tags, tags)]
    ne_tree = conlltags2tree(conlltags)

    spans = []
    span_offset_accum = 0

    for subtree in ne_tree:
        if type(subtree) == Tree:
            tree_len = len(subtree.leaves())
        else:
            tree_len = 1
        span_offset_accum += tree_len

        # skipping 'O' tags
        if type(subtree) == Tree:
            span_tokens = []

            #  Getting slice of a single entity in DP model result lists.
            span_start = span_offset_accum - tree_len
            span_stop = span_offset_accum

            #  Iterating through all tokens that belongs to a single entity.
            for i, token in enumerate(subtree.leaves()):
                #  Getting entity token span in text.
                token_span = offsets[span_start + i]
                token_text = token[0]

                #  Creating object of entity token with information about:
                #  it's start position in text,
                #  it's stop position in text,
                #  and it's text itself.
                token = DPToken(token_span[0], token_span[1], token_text)
                span_tokens.append(token)

            span_type = get_full_tag(subtree.label())

            #  Getting span of entity in text.
            span_span = (offsets[span_start][0], offsets[span_stop - 1][1])

            #  Concatenate all entity tokens into entity text or getting
            #  entity text from text for recognition.
            #  Secong variant is more accurate.
            if text is None:
                span_text = " ".join([token for token, pos in subtree.leaves()])
            else:
                span_text = text[span_span[0]:span_span[1]]

            #  Creating entity object containing info about:
            #  it's start position in text,
            #  it's stop position in text,
            #  it's text,
            #  list of it's tokens(each token is an object. See comment above.)
            span = DPSpan(span_span[0], span_span[1], span_type, span_text, span_tokens)
            spans.append(span)

    return spans


def filter_entities(entities):
    """Function removes unused entities by it's type."""

    desired_tags = ["PERSON", "LOCATION", "ORGANIZATION", "MONEY", "DATE"]

    filtered_entities = [ent for ent in entities if ent.type in desired_tags]

    return filtered_entities


def format_spans(spans):
    """Function formats spans from NER to a service result format."""

    facts = []

    for span in spans:
        fact = get_fact_from_span(span)
        facts.append(fact)

    return facts


def get_fact_from_span(span):
    """Function transforms span from NER to a service result format."""

    text = span.text
    tag = span.type
    tokens = []

    for token in span.tokens:
        current_token = {
            "text": token.text,
            "offset": token.start
        }
        tokens.append(current_token)

    fact = {
        "text": text,
        "tag": tag,
        "tokens": tokens
    }

    return fact


def ner_text(text):
    """Main function of NER module. Prepares result and goes through all steps of named entities extraction."""

    #  Getting output of deeppavlov model.
    tokens, tags, offsets = get_entities(text, ner_model)

    #  Processing model output to more usefull format:
    #  B, I tags concatenation to a single entity with it's text and tokens(each B, I tag),
    spans = form_entities_spans(tokens, tags, offsets, text)

    #  Leaving only 5 types of entities: LOC, PER, DATE, MONEY, ORG
    filtered_entities = filter_entities(spans)

    #  Formatting module results to a service format.
    facts = format_spans(filtered_entities)

    result = form_result(facts)

    return result