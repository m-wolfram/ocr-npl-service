import json
from pathlib import Path
from settings import uploaded_data_path
from utils.file_maintenance import save_from_b64, create_folder
from pipelines.PipelineNERImage import PipelineNERImage


class RequestNERImage():
    """NER Image request class."""

    def __init__(self, request_body, request_id):
        self.body = request_body
        self.id = request_id

    def save_image_on_server(self, save_dir):
        """
        Method saves image from received ner image request json.
        Required request format:
        {
            "filename": name of the image to be recognized,
            "file_b64": encoded image in base64
        }
        """

        request_data = json.loads(self.body)

        image_name = request_data["filename"]
        encoded_image_b64 = request_data["file_b64"]

        saved_image_path = save_from_b64(str(Path(save_dir).joinpath(image_name)), encoded_image_b64)

        return saved_image_path

    def prepare_response(self, recognition_result):
        """Method prepares server image recognition response."""

        response = json.dumps(recognition_result)

        return response

    def process_ner_image_request(self):
        """
        Method processes ner image recognition request.
        Required request format:
        {
            "filename": name of the image to be recognized,
            "file_b64": encoded image in base64
        }
        """

        session_folder_path = create_folder(uploaded_data_path, self.id)

        image_path_on_server = self.save_image_on_server(session_folder_path)

        pipeline = PipelineNERImage(image_path_on_server)
        ner_img_pipeline_result = pipeline.run_ner_image_pipeline()

        response = self.prepare_response(ner_img_pipeline_result)

        return response
