import cv2
from modules.recognition import recognize_image
from modules.ner_natasha import ner_text as ner_text_natasha
from modules.ner_deeppavlov import ner_text as ner_text_dp


def extend_ner_result_with_positions(ner_recognition_result, ocr_recognition_result):
    """
    Function mutates ner recognition list and extends it with tokens from ocr result that
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


def draw_debug_image(result, image, save_path):
    """Debugging function. Draws ner recognized rectangles on an image"""

    color = (89, 28, 252)
    image_to_draw_at = image.copy()

    for fact in result["facts"]:
        for token in fact["tokens"]:
            x, y, w, h = token["position"]["left"], token["position"]["top"], \
                         token["position"]["width"], token["position"]["height"]
            cv2.rectangle(image_to_draw_at, (x, y), (x + w, y + h), color, 4)

    cv2.imwrite(save_path, image_to_draw_at)

    return save_path


def run_ner_image_pipeline(image_path):
    """
    Function goes throught image ner pipeline steps and returns combined result.
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

    #  Can be replaced with classifier that classify what ner engine is more suitable for given text recognition.
    ner_engine_type = "DP"

    ocr_recognition_result = recognize_image(image_path)

    if ner_engine_type == "Natasha":
        ner_recognition_result = ner_text_natasha(ocr_recognition_result["text"])
    elif ner_engine_type == "DP":
        ner_recognition_result = ner_text_dp(ocr_recognition_result["text"])
    else:
        raise NotImplementedError("Unsupported NER engine type!")

    extended_ner_recognition_result = extend_ner_result_with_positions(ner_recognition_result, ocr_recognition_result)

    return extended_ner_recognition_result