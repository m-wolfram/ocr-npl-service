import json
from modules.ner_natasha import ner_text as ner_text_natasha
from modules.ner_deeppavlov import ner_text as ner_text_dp


class RequestNER():
    """NER request class."""

    def __init__(self, request_body):
        self.body = request_body

    def get_text_from_request(self):
        """
        Method returns text for ner from request.
        Required request format:
        {
            "text": text for named entity recognition.
        }
        """

        request_data = json.loads(self.body)
        text = request_data["text"]

        return text

    @staticmethod
    def ner_txt(txt):
        """Method passes given text to suitable ner module."""

        #  Can be replaced with classifier that classify what ner engine is more suitable for given text recognition.
        engine_type = "DP"

        if engine_type == "Natasha":
            recognition_result = ner_text_natasha(txt)
        elif engine_type == "DP":
            recognition_result = ner_text_dp(txt)
        else:
            raise NotImplementedError("Unsupported NER engine type!")

        return recognition_result

    def prepare_response(self, ner_module_result):
        """Method prepares server named entity recognition response."""

        response = json.dumps(ner_module_result)

        return response

    def process_ner_request(self):
        """
        Method processes named entity recognition request.
        Required request format:
        {
            "text": text for named entity recognition.
        }
        """

        text = self.get_text_from_request()

        text_recognition_result = self.ner_txt(text)

        response = self.prepare_response(text_recognition_result)

        return response
