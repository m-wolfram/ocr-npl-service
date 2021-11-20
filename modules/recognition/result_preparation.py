#  Module global variables.
tokens = []


def build_result(merged_df, extracted_text, image_shape):
    """Function preparing final result."""

    def _create_token(row):
        """
        Function creates token from a merged dataframe row and
        appends it to global tokens variable
        """
        global tokens
        token_dict = {
            "text": row["text"],
            "position": {
                "left": row["left"],
                "top": row["top"],
                "width": row["width"],
                "height": row["height"]
            },
            "offset": row["span"][0]
        }
        tokens.append(token_dict)
        return None

    global tokens

    #  Tokens creation from merged dataframe.
    merged_df.apply(lambda row: _create_token(row), axis=1)

    source = {
        "width": image_shape[1],
        "height": image_shape[0]
    }

    result = {
        "text": extracted_text,
        "tokens": tokens,
        "source": source
    }

    tokens = []
    return result