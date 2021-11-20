import logging
from pathlib import Path


ip = "0.0.0.0"
port = "7777"
logging_level = logging.DEBUG
log_file_max_size = 64  # In mb.
log_backups_count = 3  # The maximum amount of logs files that will be presented in logs dir.

#  Local folders:
uploaded_data_path = str(Path(__file__).parent.joinpath("uploaded_data"))
logs_dir = str(Path(__file__).parent.joinpath("logs"))
