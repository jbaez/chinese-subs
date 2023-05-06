from abc import ABC, abstractmethod
from io import TextIOWrapper


class IFileSystem(ABC):
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
    def get_files_match(self, pattern: str) -> list[str]:
        pass
