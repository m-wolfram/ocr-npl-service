from pathlib import Path
from PIL import Image
import os


def split_multipage_tif(file_path, save_dir):
    """
    Function splits multipage tif into single pages images and saves them into given directory with postfixes _pageN.
    :return: list of images paths.
    """
    pages_paths = []

    img = Image.open(file_path)

    pages_dir_path = str(Path(save_dir).joinpath("pages"))
    os.mkdir(pages_dir_path)

    for i in range(img.n_frames):
        try:
            page_file_path = str(Path(pages_dir_path).joinpath(Path(file_path).stem + '_page_{}.tif'.format(i)))
            img.seek(i)
            img.save(page_file_path)
            pages_paths.append(page_file_path)
        except EOFError:
            break

    return pages_paths
