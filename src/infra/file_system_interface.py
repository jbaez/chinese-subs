from abc import ABC, abstractmethod
from io import TextIOWrapper


class IFileSystem(ABC):
    @abstractmethod
    def path_exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def path_is_dir(self, path: str) -> bool:
        pass

    @abstractmethod
    def open(self, file: str, encoding='utf-8') -> TextIOWrapper:
        pass

    @abstractmethod
    def read(self, path: str) -> str:
        pass

    @abstractmethod
    def write(self, path: str, content: str) -> None:
        pass

    @abstractmethod
    def remove(self, path: str) -> None:
        pass

    @abstractmethod
    def get_dir_path(self, file_path: str) -> str:
        pass

    @abstractmethod
    def list_dir(self, path: str) -> list[str]:
        pass

    @abstractmethod
    def join_path(self, parent_dir: str, file_name: str) -> str:
        pass
