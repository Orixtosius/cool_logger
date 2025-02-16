import threading
import queue
from tests.context import cool_logger
from cool_logger.core.building import LogBuilder


class TestBasicCreation:

    @classmethod
    def setup_class(cls) -> None:
        cls.log_builder = LogBuilder()
        cls.log_queue = queue.Queue()
        cls.name = "Test"
        cls.path = "output/log"

    @classmethod
    def teardown_class(cls):
        cls.log_builder = None
        cls.log_queue = None
    
    def test_create_two_loggers(self):
        name = "Test"
        path = "output/log"
        logger = self.log_builder.name(f"{name}_1").target(path).build()
        logger2 = self.log_builder.name(f"{name}_2").target(path).build()
        assert logger == logger2
        assert len(logger.handlers) == 2

    def test_create_loggers_multithreadly_safe(self):
        sample_size = 1000
        threads = list()
        for i in range(sample_size):
            thread = threading.Thread(target=self._multithread_building, args=(i,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        loggers = []
        while not self.log_queue.empty():
            loggers.append(self.log_queue.get())
        assert self._is_all_loggers_have_same_name(loggers) == True

    def _multithread_building(self, key: int):
        logger = self.log_builder.name(f"{self.name}_{key}").target(self.path).build()
        self.log_queue.put(logger)

    def _is_all_loggers_have_same_name(self, loggers: list):
        if not loggers:
            return False
        first_value = loggers[0].name
        return all(instance.name == first_value for instance in loggers)

    def _test_class_instance(self, loggers: list):
        if not loggers:
            return False
        first_type = type(next(iter(loggers)))
        return all(isinstance(logger, first_type) for logger in loggers)