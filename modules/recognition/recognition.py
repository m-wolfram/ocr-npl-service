import os
import glob
import logging
from sys import platform
from pathlib import Path
from pytesseract import Output
import pytesseract
import cv2
from .image_preparation import prepare_image
from .result_preparation import build_result
from .settings import (
    debug,
    temp_files_dir,
    sep,
    size,
    config,
    lang
)


#  Module global variables.
if platform == "win32":
    #  A path to tesseract executable.
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
last_index = 0


def get_ocr_data(cv2_image, config, lang):
    """
    Function getting recognized text from an image

    :img_path: - A path to an image;
    :config: - a string config for tesseract;
    :lang: - language of recognition;

    Returns dataframe with ocr data(including coords, word text and confidence).
    """

    #  Ocr data extraction.
    ocr_data = pytesseract.image_to_data(cv2_image, lang=lang, output_type=Output.DATAFRAME, config=config)

    return ocr_data


def transform_coordinates(filtered_ocr_data, multiplier):
    """Function returns a dataframe with coordinates, that fit original image."""

    tesseract_coords_positions = ["left", "top", "width", "height"]

    for pos in tesseract_coords_positions:
        filtered_ocr_data[pos] = filtered_ocr_data[pos].apply(lambda c: int(c/multiplier))

    return filtered_ocr_data


def process_text(prepared_ocr_data, concatenation_sep):
    """
    Function processing text from recognized image.

    :prepared_ocr_data: - prepared dataframe of data from recognition;
    :concatenation_sep: - separator to be used in strings concatenaton.

    Returns dataframe with text info and concatenated text itself.
    """

    def _calc_span(row, sep):
        """
        Function calculating span for a word in dataframe.
        Requires access to a global var last_index.

        :sep: - concatenation separator;

        Returns span tupple(start index, stop index).
        """
        global last_index

        word_len = len(row["text"])

        span = tuple([last_index, last_index + word_len])

        #  Adding word len and sep len to a accumulation variable.
        last_index += word_len + len(sep)
        return span

    global last_index

    #  Counting span column using concatenation separator.
    span_col = prepared_ocr_data.apply(lambda r: _calc_span(r, concatenation_sep), axis=1)

    #  Adding new column to a dataframe.
    span_df = prepared_ocr_data.assign(span=span_col)

    #  Removing unused columns.
    text_df = span_df.drop(columns=["conf", "left", "top", "width", "height"])

    concatenated_text = concatenation_sep.join(text_df['text'])

    last_index = 0
    return concatenated_text, text_df


def process_layout(prepared_ocr_data):
    """
    Function processing coordinates of extracted text.

    :prepared_ocr_data: - prepared dataframe of data from recognition.

    Returns coords df.
    """

    layout_df = prepared_ocr_data.drop(columns=["conf"])

    return layout_df


def filter_ocr_data(ocr_data):
    """Function of tesseract output preparation"""

    cols = ['text', 'left', 'top', 'width', 'height', 'conf']

    #  Zero confidence entries deletion.
    confident_ocr_data = ocr_data[ocr_data.conf != -1]

    #  Unused columns removal.
    cleared_ocr_data = confident_ocr_data[cols]

    cleared_ocr_data.reset_index(drop=True, inplace=True)

    return cleared_ocr_data


def draw_debug_image(result, image, save_path):
    """Debugging function. Draws recognized rectangles on an image"""

    color = (89, 28, 252)
    image_to_draw_at = image.copy()

    for token in result["tokens"]:
        x, y, w, h = token["position"]["left"], token["position"]["top"], \
                     token["position"]["width"], token["position"]["height"]
        cv2.rectangle(image_to_draw_at, (x, y), (x + w, y + h), color, 4)

    cv2.imwrite(save_path, image_to_draw_at)
    return save_path


def debug_layout(img_path, result, image):
    """Function saves debug info picture about recognized text layout."""

    #  Removing previously saved layout debug images in order to prevent high disk usage.
    previous_files = glob.glob(str(Path(temp_files_dir).joinpath("*_layout_debug.jpg")))
    for file_path in previous_files:
        os.remove(file_path)

    debug_image_name = Path(img_path).stem + "_layout_debug.jpg"
    save_path = str(Path(temp_files_dir).joinpath(debug_image_name))
    draw_debug_image(result, image, save_path)

    return save_path


def recognize_image(img_path):
    """
    Main function of recognition module.
    Goes through all recognition steps and returning final result.
    """

    #  Image preparations.
    #  Interpolation, channels conversion from bgr to rgb to pass into tesseract.
    image, resized_image, multiplier, converted_image = prepare_image(img_path, size)

    #  Getting recognition data and removing unused data from tesseract output.
    ocr_data = get_ocr_data(converted_image, config, lang)
    filtered_ocr_data = filter_ocr_data(ocr_data)

    #  Coordinate transformation after resizing.
    #  Due to resize, it is needed to return back coords fitting original image.
    prepared_ocr_data = transform_coordinates(filtered_ocr_data, multiplier)

    #  Processing only text data from recognition.
    #  Affects only text information.
    extracted_text, text_df = process_text(prepared_ocr_data, sep)

    #  Processing extracted layout information (coordinates).
    layout_df = process_layout(prepared_ocr_data)

    #  Combined dataframe(text spans info + layout). In order to make it possible to parallel previous operations.
    merged_df = text_df.merge(layout_df)

    #  Result preparation.
    result = build_result(merged_df, extracted_text, image.shape)

    #  Debug depicting.
    if debug:
        #  Saving image containing information about recognized boxes layout.
        debug_layout(img_path, result, image)

    return result