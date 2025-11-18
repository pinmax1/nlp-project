import logging
from pathlib import Path
import sys
import io

class LoggerConfig:
    def __init__(self, log_file: str, log_level: str = "INFO"):
        self.log_file = log_file
        self.log_level = log_level

        self._setup_logs_directory()
        self.setup_logging()

    def _setup_logs_directory(self) -> None:
        log_path = Path(self.log_file)
        log_dir = log_path.parent

        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)

    def setup_logging(self) -> None:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        log_level = getattr(logging, self.log_level.upper(), logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        file_handler = logging.FileHandler(self.log_file, mode='w', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)


    def get_logger(self, name: str) -> logging.Logger:
        return logging.getLogger(name)
