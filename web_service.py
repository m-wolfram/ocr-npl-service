import uuid
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask import Flask, request, make_response
from waitress import serve
from service_requests.RequestOCR import RequestOCR
from service_requests.RequestNER import RequestNER
from service_requests.RequestNERImage import RequestNERImage
from service_requests.RequestDocPipeline import RequestDocPipeline
from utils.requests_utils import create_error_response
from utils.network_utils import check_docker_environment, get_ip
from settings import (
    ip,
    port,
    logging_level,
    logs_dir,
    log_file_max_size,
    log_backups_count
)


app = Flask(__name__)

#  Setting up logger.
logger = logging.getLogger("main_logger")
logger.setLevel(logging_level)
stream_handler = logging.StreamHandler()  # Writes into console.
file_handler = RotatingFileHandler(Path(logs_dir).joinpath("service.log"),
                                   maxBytes=log_file_max_size*1000000, backupCount=log_backups_count,
                                   encoding="utf-8",
                                   delay=True)  # Writes into file.
#  Setting logs entries format.
stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s in %(module)s.%(funcName)s"
                                              " at line %(lineno)d: %(message)s"))
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s in %(module)s.%(funcName)s"
                                            " at line %(lineno)d: %(message)s"))
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


@app.route("/v1/recognize_image", methods=["POST"])
def request_recognition():
    """
    Request format(json):
    {
        "filename": name of the image to be recognized,
        "file_b64": encoded image in base64
    }
    """

    try:
        if request.content_type == "application/json":
            session_id = str(uuid.uuid4())

            Request = RequestOCR(request.json, session_id)
            response = Request.process_ocr_request()

            return make_response(response, 200)
        else:
            return make_response(create_error_response("Incorrect request content type! "
                                                       "'application/json' is required."), 400)
    except Exception as exc:
        logger.exception(str(exc))
        return make_response(create_error_response("Internal server error!"), 500)


@app.route("/v1/ner_txt", methods=["POST"])
def request_ner():
    """
    Request format(json):
    {
        "text": text for named entity recognition.
    }
    """

    try:
        if request.content_type == "application/json":

            Request = RequestNER(request.json)
            response = Request.process_ner_request()

            return make_response(response, 200)
        else:
            return make_response(create_error_response("Incorrect request content type! "
                                                       "'application/json' is required."), 400)
    except Exception as exc:
        logger.exception(str(exc))
        return make_response(create_error_response("Internal server error!"), 500)


@app.route("/v1/ner_image", methods=["POST"])
def request_ner_image():
    """
    Request format(json):
    {
        "filename": name of the image to be recognized,
        "file_b64": encoded image in base64
    }
    """

    try:
        if request.content_type == "application/json":
            session_id = str(uuid.uuid4())

            Request = RequestNERImage(request.json, session_id)
            response = Request.process_ner_image_request()

            return make_response(response, 200)
        else:
            return make_response(create_error_response("Incorrect request content type! "
                                                       "'application/json' is required."), 400)
    except Exception as exc:
        logger.exception(str(exc))
        return make_response(create_error_response("Internal server error!"), 500)


@app.route("/v1/process_document", methods=["POST"])
def request_document_processing():
    """
    Request format(json):
    {
        "filename": name of the document to be recognized,
        "file_b64": encoded document in base64
    }
    """

    try:
        if request.content_type == "application/json":
            session_id = str(uuid.uuid4())

            Request = RequestDocPipeline(request.json, session_id)
            response = Request.process_doc_pipeline_request()

            return make_response(response, 200)
        else:
            return make_response(create_error_response("Incorrect request content type! "
                                                       "'application/json' is required."), 400)
    except Exception as exc:
        logger.exception(str(exc))
        return make_response(create_error_response("Internal server error!"), 500)


if __name__ == "__main__":
    #  Rewriting ip address if project runs inside docker container with it's image.
    if check_docker_environment():
        logger.info("Running inside docker..")
        ip = get_ip()

    #app.run(host=ip, port=port, debug=True)
    serve(app, host=ip, port=port)
