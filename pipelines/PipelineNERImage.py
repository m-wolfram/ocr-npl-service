import cv2
from modules.recognition import recognize_image
from modules.ner_natasha import ner_text as ner_text_natasha
from modules.ner_deeppavlov import ner_text as ner_text_dp


class PipelineNERImage():
    def __init__(self, image_path):
        self.img_path = image_path

    @staticmethod
    def extend_ner_result_with_positions(ner_recognition_result, ocr_recognition_result):
        """
        Method mutates ner recognition list and extends it with tokens from ocr result that
        fits named entity span.
        """

        for i, fact in enumerate(ner_recognition_result["facts"]):
            fact_start = fact["tokens"][0]["offset"]  # Start of an entity in text.
            fact_stop = fact_start + len(fact["text"])  # Stop point of an entity in text.

            #  Getting tokens from ocr recognition results that are in recognized entity range.
            fact_ocr_tokens = [token for token in ocr_recognition_result["tokens"] if
                               token["offset"] in list(range(fact_start, fact_stop))]

            ner_recognition_result["facts"][i]["tokens"] = fact_ocr_tokens
            ner_recognition_result["source"] = ocr_recognition_result["source"]

        return ner_recognition_result

    def draw_debug_image(self, result, image, save_path):
        """Debugging method. Draws ner recognized rectangles on an image"""

        color = (89, 28, 252)
        image_to_draw_at = image.copy()

        for fact in result["facts"]:
            for token in fact["tokens"]:
                x, y, w, h = token["position"]["left"], token["position"]["top"], \
                             token["position"]["width"], token["position"]["height"]
                cv2.rectangle(image_to_draw_at, (x, y), (x + w, y + h), color, 4)

        cv2.imwrite(save_path, image_to_draw_at)

        return save_path

    @classmethod
    def get_entities_from_ocr(cls, ocr_data):
        """Method extracts entities from given ocr data."""

        #  Can be replaced with classifier that classify what ner engine is more suitable for given text recognition.
        ner_engine_type = "DP"

        if ner_engine_type == "Natasha":
            ner_recognition_result = ner_text_natasha(ocr_data["text"])
        elif ner_engine_type == "DP":
            ner_recognition_result = ner_text_dp(ocr_data["text"])
        else:
            raise NotImplementedError("Unsupported NER engine type!")

        extended_ner_recognition_result = cls.extend_ner_result_with_positions(ner_recognition_result, ocr_data)

        return extended_ner_recognition_result

    def run_ner_image_pipeline(self):
        """
        Method goes throught image ner pipeline steps and returns combined result.
        Returns following result:
        {
            "facts": [
                {
                    "text": string entity text,
                    "tag": string entity tag "PERSON" | "DATE" | "MONEY" | "ORGANIZATION" | "LOCATION",
                    "tokens": [
                        {
                            "text": string token text,
                            "offset" int index of first token symbol in text
                        },
                        ...
                    ]
                },
                ...
            ]
        }
        """

        ocr_recognition_result = recognize_image(self.img_path)

        #  Getting entities from ocr'ed image.
        entities = self.get_entities_from_ocr(ocr_recognition_result)

        return entities