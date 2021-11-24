import json
from pathlib import Path
from settings import uploaded_data_path
from utils.file_maintenance import save_from_b64, create_folder
from utils.data_preparation import split_multipage_tif
from pipelines.PipelineDocProcessing import PipelineDocProcessing


class RequestDocPipeline():
    """Doc pipeline request class."""

    def __init__(self, request_body, request_id):
        self.body = request_body
        self.id = request_id

    def save_document_on_server(self, save_dir):
        """
        Method saves document from received json.
        Required request format:
        {
            "filename": name of the image to be recognized,
            "file_b64": encoded image in base64
        }
        """

        request_data = json.loads(self.body)

        file_name = request_data["filename"]
        encoded_file_b64 = request_data["file_b64"]

        saved_file_path = save_from_b64(str(Path(save_dir).joinpath(file_name)), encoded_file_b64)

        return saved_file_path

    def prepare_response(self, result):
        """Method prepares server document pipeline response."""

        response = json.dumps(result)

        return response

    def process_doc_pipeline_request(self):
        """
        Method processes document pipeline request.
        Required request format:
        {
            "filename": name of the image to be recognized,
            "file_b64": encoded image in base64
        }
        """

        session_folder_path = create_folder(uploaded_data_path, self.id)

        document_path_on_server = self.save_document_on_server(session_folder_path)

        #  Getting images list after tif splitting.
        document_images_paths = split_multipage_tif(document_path_on_server, session_folder_path)

        pipeline = PipelineDocProcessing(document_images_paths)
        doc_pipeline_result = pipeline.run_document_pipeline()

        response = self.prepare_response(doc_pipeline_result)

        return response
