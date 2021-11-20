import base64


def save_from_b64(save_path, encoded_file):
    """Function saves file from b64 in a given directory."""

    decoded_file = base64.b64decode(bytes(encoded_file, encoding="utf-8"))

    with open(save_path, "wb") as wf:
        wf.write(decoded_file)

    return save_path