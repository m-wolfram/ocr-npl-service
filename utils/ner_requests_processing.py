import json
from modules.ner_natasha import ner_text as ner_text_natasha
from modules.ner_deeppavlov import ner_text as ner_text_dp


def get_text_from_request(request_json):
    """
    Function returns text for ner from request.
    Required request format:
    {
        "text": text for named entity recognition.
    }
    """

    request_data = json.loads(request_json)
    text = request_data["text"]

    return text


def prepare_response(ner_module_result):
    """Function preparing server named entity recognition response."""

    response = json.dumps(ner_module_result)

    return response


def ner_txt(txt):
    """Function passes given text to suitable ner module."""

    #  Can be replaced with classifier that classify what ner engine is more suitable for given text recognition.
    engine_type = "DP"

    if engine_type == "Natasha":
        recognition_result = ner_text_natasha(txt)
    elif engine_type == "DP":
        recognition_result = ner_text_dp(txt)
    else:
        raise NotImplementedError("Unsupported NER engine type!")

    return recognition_result


def process_ner_request(request_json):
    """
    Function processes named entity recognition request.
    Required request format:
    {
        "text": text for named entity recognition.
    }
    """

    text = get_text_from_request(request_json)

    text_recognition_result = ner_txt(text)

    response = prepare_response(text_recognition_result)

    return response