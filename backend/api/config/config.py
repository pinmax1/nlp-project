import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from api.logger import LoggerConfig


class ServerConfigOptions:
    REQUIRED_VARS: Dict[str, type] = {
        "SECRET_KEY": str,
        "API_TOKEN": str,
        "MODEL": str,
        "INDEX_MODEL_NAME": str,
        "EMBEDDINGS_PATH": str,
        "STEAMDB_PATH": str,
        "URL": str,
        "OLLAMA_HOST": str,
        "DEBUG": bool,
        "HOST": str,
        "PORT": int,
        "LOG_LEVEL": str,
        "LOG_FILE": str,
        "THREADS": int,
        "CONNECTION_LIMIT": int,
        "REQUEST_TIMEOUT": float,
    }


class ServerConfig:
    __annotations__ = ServerConfigOptions.REQUIRED_VARS

    def __init__(self, env_file: Optional[str] = None) -> None:
        if env_file:
            self._load_env_file(env_file)
        else:
            load_dotenv()

        self._load_required_vars()

        self.logger_config = LoggerConfig(self.LOG_FILE, self.LOG_LEVEL)
        self.logger = self.logger_config.get_logger("ServerConfig")

        self._setup_logs_directory()
        self.logger.info(f"Server configuration loaded: {self.to_dict()}")

    def _load_env_file(self, env_file: str) -> None:
        env_file_path = Path(env_file)

        if not env_file_path.exists():
            raise FileNotFoundError(
                f"Can not find .env file provided by path {env_file}"
            )

        load_dotenv(env_file_path)

    def _load_required_vars(self) -> None:
        for var_name, type_converter in ServerConfigOptions.REQUIRED_VARS.items():
            value = os.getenv(var_name)
            if not value:
                raise ValueError(f"Required environment variable {var_name} is not set")

            try:
                typed_value = type_converter(value)
                setattr(self, var_name, typed_value)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Failed to convert environment variable {var_name} = {value} "
                    f"using converter {type_converter.__name__}: {e}"
                ) from e

    def _setup_logs_directory(self) -> None:
        log_path = Path(self.LOG_FILE)
        log_dir = log_path.parent

        if not log_dir.exists():
            self.logger.info(f"Create logs directory {log_dir}")
            log_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        config_dict: Dict[str, Any] = {}

        for var_name in ServerConfigOptions.REQUIRED_VARS:
            config_dict[var_name] = getattr(self, var_name)

        return config_dict
