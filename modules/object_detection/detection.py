def detect_objects_in_image(image_path):
    """Function detects objects in given image."""

    result = {
        "objects": [
            {
                "type": "logo",
                "position": {
                    "left": 5,
                    "top": 10,
                    "width": 20,
                    "height": 30
                }
            }
        ],
        "source": {
            "width": 250,
            "height": 250
        }
    }

    return result