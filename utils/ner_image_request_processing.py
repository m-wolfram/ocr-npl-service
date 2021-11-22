import json
from pathlib import Path
from settings import uploaded_data_path
from utils.file_maintenance import save_from_b64, create_folder
from pipelines.ner_image_pipeline import run_ner_image_pipeline


def save_image_on_server(request_json, save_dir):
    """
    Function saves image from received in ocr request json.
    Required request format:
    {
        "filename": name of the image to be recognized,
        "file_b64": encoded image in base64
    }
    """

    request_data = json.loads(request_json)

    image_name = request_data["filename"]
    encoded_image_b64 = request_data["file_b64"]

    saved_image_path = save_from_b64(str(Path(save_dir).joinpath(image_name)), encoded_image_b64)

    return saved_image_path


def prepare_response(recognition_result):
    """Function preparing server image recognition response."""

    response = json.dumps(recognition_result)

    return response


def process_ner_image_request(request_json, session_id):
    """
    Function processes ner image recognition request.
    Required request format:
    {
        "filename": name of the image to be recognized,
        "file_b64": encoded image in base64
    }
    """

    session_folder_path = create_folder(uploaded_data_path, session_id)

    image_path_on_server = save_image_on_server(request_json, session_folder_path)

    ner_img_pipeline_result = run_ner_image_pipeline(image_path_on_server)

    response = prepare_response(ner_img_pipeline_result)

    return response