import json
from datetime import datetime


def create_error_response(error_text):
    """Function creates error response from server."""

    body = {
        "error": error_text,
        "time": str(datetime.now())
    }

    response = json.dumps(body)

    return response
