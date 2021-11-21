import os
import base64
from pathlib import Path


def save_from_b64(save_path, encoded_file):
    """Function saves file from b64 in a given directory."""

    decoded_file = base64.b64decode(bytes(encoded_file, encoding="utf-8"))

    with open(save_path, "wb") as wf:
        wf.write(decoded_file)

    return save_path


def create_folder(where_to_create, folder_name):
    """Function creates empty directory in given directory path and returns path to a created folder."""

    folder_to_be_created_path = str(Path(where_to_create).joinpath(folder_name))

    if not os.path.exists(folder_to_be_created_path):
        os.mkdir(folder_to_be_created_path)

    return folder_to_be_created_path