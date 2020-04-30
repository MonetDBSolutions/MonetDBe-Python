from abc import ABC, abstractmethod


class BaseInterAPI(ABC):
    @abstractmethod
    def append(self):
        ...

    @abstractmethod
    def cleanup_result(self, connection, result):
        ...

    @abstractmethod
    def clear_prepare(self):
        ...

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def disconnect(self, connection):
        ...

    @abstractmethod
    def get_autocommit(self):
        ...

    @abstractmethod
    def get_columns(self):
        ...

    @abstractmethod
    def get_table(self):
        ...

    @abstractmethod
    def is_initialized(self):
        ...

    @abstractmethod
    def query(self, connection, query):
        ...

    @abstractmethod
    def result_fetch(self):
        ...

    @abstractmethod
    def result_fetch_rawcol(self):
        ...

    @abstractmethod
    def send_close(self):
        ...

    @abstractmethod
    def set_autocommit(self):
        ...

    @abstractmethod
    def shutdown(self):
        ...

    @abstractmethod
    def startup(self):
        ...