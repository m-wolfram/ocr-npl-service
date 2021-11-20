import json
from modules.ner_natasha import ner_text


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


def prepare_response(recognition_result):
    """Function preparing server named entity recognition response."""

    response = json.dumps(recognition_result)

    return response


def process_ner_request(request_json):
    """
    Function processes named entity recognition request.
    Required request format:
    {
        "text": text for named entity recognition.
    }
    """

    text = get_text_from_request(request_json)

    recognition_result = ner_text(text)

    response = prepare_response(recognition_result)

    return response