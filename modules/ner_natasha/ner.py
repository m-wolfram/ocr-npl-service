from natasha import (
    MorphVocab,
    NewsEmbedding,
    NewsNERTagger,
    Segmenter,
    Doc,

    NamesExtractor,
    DatesExtractor,
    MoneyExtractor,
    AddrExtractor
)
from natasha.doc import DocSpan
from .result_prepare import form_result


segmenter = Segmenter()
emb = NewsEmbedding()
ner_tagger = NewsNERTagger(emb)
morph_vocab = MorphVocab()

names_extractor = NamesExtractor(morph_vocab)
dates_extractor = DatesExtractor(morph_vocab)
money_extractor = MoneyExtractor(morph_vocab)
addr_extractor = AddrExtractor(morph_vocab)


def get_full_tag(tag):
    """
    Function returning full version of received tag.
    Example: LOC - LOCATION, PER - PERSON etc.
    """

    replacements = {
        "LOC": "LOCATION",
        "PER": "PERSON",
        "ORG": "ORGANISATION",
    }

    new_tag = tag

    for old, new in replacements.items():
        new_tag = new_tag.replace(old, new)

    return new_tag


def get_fact_from_span(span):
    """Function transforms span from natasha NER to a service result format."""

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
        "tag": get_full_tag(tag),
        "tokens": tokens
    }

    return fact


def format_spans(spans):
    """Function formats spans from natasha NER to a service result format."""

    facts = []

    for span in spans:
        fact = get_fact_from_span(span)
        facts.append(fact)

    return facts


def tag_entities(text, extractor):
    """Function extracts entities according to given extractor.
    Natasha's lib extractors are expected:
        DatesExtractor,
        MoneyExtractor
    """

    def _adjust_tokens(tokens, match):
        """Function makes certain entity tokens spans fitting given text."""

        adj_tokens = []

        for token in tokens:
            token.start = match.start + token.start
            token.stop = match.start + token.stop
            adj_tokens.append(token)

        return adj_tokens

    tags = {
        "NamesExtractor": "NAME",
        "DatesExtractor": "DATE",
        "MoneyExtractor": "MONEY",
        "AddrExtractor": "ADDRESS"
    }

    #  Getting matches.
    matches = list(extractor(text))
    spans = []

    for match in matches:
        span_text = text[match.start:match.stop]  # Getting whole money match span text(not tokenized).
        tag = tags[extractor.__class__.__name__]  # Setting tag name

        #  Tokenizing text in order to get tokens of entity.
        ndoc = Doc(span_text)
        ndoc.segment(segmenter)

        tokens = _adjust_tokens(ndoc.tokens, match)

        #  Creating money span class in a similar format to natasha's other tags format(LOC, ORG, PER).
        #  DocSpan class is imported from natasha lib.
        span = DocSpan(
            match.start,
            match.stop,
            tag,
            span_text,
            tokens
        )

        spans.append(span)

    return spans


def ner_text(text):
    """Main function of NER module. Prepares result and goes through all steps of named entities extraction."""

    ndoc = Doc(text)

    ndoc.segment(segmenter)
    ndoc.tag_ner(ner_tagger)

    money_spans = tag_entities(text, money_extractor)
    dates_spans = tag_entities(text, dates_extractor)

    entities = money_spans + ndoc.spans + dates_spans

    facts = format_spans(entities)

    result = form_result(facts)

    return result


if __name__ == "__main__":
    text = r"***"
    print(ner_text(text))