import re
from pathlib import Path
from modules.recognition import recognize_image
from modules.object_detection import detect_objects_in_image
from modules.classification import classify_img
from pipelines.ner_image_pipeline import run_ner_image_pipeline, get_entities_from_ocr


def recognize_each_image(images_paths):
    """
    Function recognizes each image in given images list and creates list of results.
    Result:
        [
            {
                "image_path": image path,
                "recognition" image recognition result
            },
            ...
        ]
    """

    recognition_data = []

    for img_path in images_paths:
        recognition_result = recognize_image(img_path)

        recognition_dict = {
            "image_path": img_path,
            "recognition": recognition_result
        }

        recognition_data.append(recognition_dict)

    return recognition_data


def detect_objects_in_each_image(images_paths):
    """
    Function detects objects in each image in given images list and creates list of results.
    Result:
        [
            {
                "image_path": image path,
                "detection" image object detection result
            },
            ...
        ]
    """

    object_detection_data = []

    for img_path in images_paths:
        detection_result = detect_objects_in_image(img_path)

        detection_dict = {
            "image_path": img_path,
            "detection": detection_result
        }

        object_detection_data.append(detection_dict)

    return object_detection_data


def classify_document_pages(images_paths):
    """
    Function classifies document pages and creates list of results.
    Result:
        [
            {
                "image_path": image path,
                "classification" image classification result
            },
            ...
        ]
    """

    #  Note:
    #  Images can be classified according to others images in document.
    #  That is why it can be implemented by not passing each
    #  image into classification module but all images at one time.

    #  Single image:
    page_classification_data = []

    for img_path in images_paths:
        classification_result = classify_img(img_path)

        classification_dict = {
            "image_path": img_path,
            "classification": classification_result
        }

        page_classification_data.append(classification_dict)

    #  All pages at one time.
    # page_classification_data = classify_img(image_paths)

    return page_classification_data


def ner_each_image(images_paths):
    """
    Function recognizes named entities from each image in given images list and creates list of results.
    Result:
        [
            {
                "image_path": image path,
                "recognition" image named entities recognition result
            },
            ...
        ]
    """

    ner_imgs_data = []

    for img_path in images_paths:
        ner_image_pipeline_result = run_ner_image_pipeline(img_path)

        recognition_dict = {
            "image_path": img_path,
            "recognition": ner_image_pipeline_result
        }

        ner_imgs_data.append(recognition_dict)

    return ner_imgs_data


def ner_each_ocrdata(ocr_data_list):
    """
    Function recognizes named ents from each already recognized image in given data list and creates list of results.
    Input:
        [
            {
                "image_path": image path,
                "recognition" image ocr recognition result
            },
            ...
        ]
    Result:
        [
            {
                "image_path": image path,
                "recognition" image named entities recognition result
            },
            ...
        ]
    """

    ner_data_list = []

    for ocr_data in ocr_data_list:
        ner_result = get_entities_from_ocr(ocr_data["recognition"])

        recognition_dict = {
            "image_path": ocr_data["image_path"],
            "recognition": ner_result
        }

        ner_data_list.append(recognition_dict)

    return ner_data_list


def get_main_pages(pages_data):
    """
    Function returns path of a main document page.
    :param pages_data: list of dicts, where each dict contains information about page.
    Input format list of dicts:
    [
        {
            "image_path": image path,
            "classification": {
                "source": {
                    "width": number,
                    "height": number,
                    "type": type(main or other)
                }
            }
        },
        ...
    ]
    """

    main_pages = [p_info for p_info in pages_data if p_info["classification"]["source"]["type"] == "main"]
    main_pages_paths = [page["image_path"] for page in main_pages]

    return main_pages_paths


def combine_result(ocr_data, obj_detection_data, pages_data, ner_data):
    """
    Function combines final pipeline's result from received from modules data.

    Returns following pipeline result:

    {
        "text": total document text,
        "pages": [
            {
                "index": page number,
                "text": page text,
                "objects": detected objects,
                "info": page info,
                "facts": named entities(None if page is not main)
            }
        ]
    }

    Verbose:

    {
        "text": string concatenated pages text,
        "pages": [
            {
                "index": int page number,
                "text": string page text,
                "objects": [
                    {
                        "type": string "logo" or "sign",
                        "position": {
                            "left": int x pos,
                            "top": int y pos,
                            "width": int object width,
                            "height" int object height
                        }
                    },
                    ...
                ],
                "info": {
                    "width": int page width,
                    "height": ing page height,
                    "type": string "main" or "other"
                },
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
                ] or None if page is not main
            },
            ...
        ]
    }
    """

    def _get_page_index(path):
        """Returns extracted page index from path."""
        return int(re.search("(?s:.*)_page_(\\d)", path).group(1))

    text = " ".join([page["recognition"]["text"] for page in ocr_data])
    pages = []

    for i in range(len(pages_data)):
        path_page = pages_data[i]["image_path"]
        type_ = pages_data[i]["classification"]["source"]["type"]

        index = _get_page_index(path_page)
        text_page = [page_ for page_ in ocr_data if page_["image_path"] == path_page][0]["recognition"]["text"]
        objects = [page_ for page_ in obj_detection_data if page_["image_path"] == path_page][0]["detection"]["objects"]
        info = pages_data[i]["classification"]["source"]
        if type_ == "main":
            facts = [page_ for page_ in ner_data if page_["image_path"] == path_page][0]["recognition"]["facts"]
        else:
            facts = None

        page = {
            "index": index,
            "text": text_page,
            "objects": objects,
            "info": info,
            "facts": facts
        }

        pages.append(page)

    result = {
        "text": text,
        "pages": pages
    }

    return result


def run_document_pipeline(document_images_paths):
    """Function goes through document processing pipeline steps and returns combined result."""

    #  Next steps can be paralleled.
    #  Recognizing each image from document.
    ocr_data = recognize_each_image(document_images_paths)

    #  Getting information about detected objects in images.
    object_detection_data = detect_objects_in_each_image(document_images_paths)

    #  Getting information about pages classification.
    pages_data = classify_document_pages(document_images_paths)

    #  Getting paths of main pages.
    main_pages_paths = get_main_pages(pages_data)

    #  Applying NER to each main page.
    #  getting ocr data of main pages from already recognized images.
    ocr_data_mps = [page for page in ocr_data if page["image_path"] in main_pages_paths]
    ner_data = ner_each_ocrdata(ocr_data_mps)

    result = combine_result(ocr_data, object_detection_data, pages_data, ner_data)

    return result
