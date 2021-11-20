from pathlib import Path


size = 4000  # Size that images will be interpolated to by their y size
lang = 'eng'  # Recognition language
config = '--psm 11'  # Tesseract page segmentation mode
sep = ' '  # Text concatenation separator
debug = False  # Module debug flag

#  Folders:
temp_files_dir = str(Path(__file__).parent.joinpath("temp"))
