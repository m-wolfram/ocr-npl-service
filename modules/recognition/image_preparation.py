import cv2


def resize_image(image, size):
    """Image interpolation function"""

    # Output image dimensions calculation.
    multiplier = size / image.shape[0]
    width = int(image.shape[1] * multiplier)
    height = int(image.shape[0] * multiplier)
    shape = (width, height)

    #  Image resizing.
    resized_image = cv2.resize(image, shape, interpolation=cv2.INTER_CUBIC)
    return resized_image, multiplier


def prepare_image(img_path, size):
    """Function of image preparation before passing to recognition."""
    image = cv2.imread(img_path)
    #  Image resize and getting resize multiplier(how much bigger resized image than original).
    resized_image, multiplier = resize_image(image, size)

    #  Reverting image channelf before passing to recognition.
    converted_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)  # Image channels reversion.
    return image, resized_image, multiplier, converted_image