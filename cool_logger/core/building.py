import os
import logging
import threading
from datetime import datetime
from cool_logger.core.color_format import ColorfulFormatter


class LogBuilder:
    _instance = None
    _is_initialized = False
    _logger = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Double Check Locking
        if cls._instance is None:
            with LogBuilder._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def name(self, name: str = "Default"):
        self._name = name
        return self

    def target(self, path: str = "output/logs/log"):
        self._path = self._reconstruct_path(path)
        return self

    def build(self) -> logging.Logger:
        if self._is_initialized:
            return self._instance._logger
        self._is_initialized = True
        formatter = ColorfulFormatter("%(asctime)s - [ %(levelname)s ] - %(name)s >> %(message)s")
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(logging.DEBUG)
        self._add_stream_handler(formatter)
        self._add_file_handler(formatter)
        self._logger.propagate = False
        return self._logger

    def _reconstruct_path(self, path: str) -> str:
        if os.path.isabs(path):
            if ".log" in path:
                return path
            else:
                raise ValueError("Given path is not supported.")
        moment = datetime.now().strftime("%Y-%m-%d")
        reformed_path = f"{path}_{moment}.log"
        self._create_folder(reformed_path)
        return reformed_path
    
    def _create_folder(self, path: str) -> None:
        root, _ = path.rsplit("/", 1)
        if not os.path.exists(root):
            os.makedirs(root)
    
    def _add_stream_handler(self, formatter: ColorfulFormatter) -> None:
        if not any(
            isinstance(handler, logging.StreamHandler)\
            and not isinstance(handler, logging.FileHandler)
            for handler in self._logger.handlers):
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            stream_handler.setLevel(logging.DEBUG)
            self._logger.addHandler(stream_handler)

    def _add_file_handler(self, formatter: ColorfulFormatter) -> None:
        if not any(isinstance(handler, logging.FileHandler) for handler in self._logger.handlers):
            file_handler = logging.FileHandler(self._path)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            self._logger.addHandler(file_handler)