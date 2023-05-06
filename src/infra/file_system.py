from infra.file_system_interface import IFileSystem
from io import TextIOWrapper
from os import remove
from glob import glob


class FileSystem(IFileSystem):
    def open(self, file: str, encoding='utf-8') -> TextIOWrapper:
        return open(file=file, encoding=encoding)

    def read(self, path: str) -> str:
        return self.open(path).read()

    def write(self, path: str, content: str) -> None:
        with open(path, 'w') as f:
            f.write(content)

    def remove(self, path: str) -> None:
        remove(path)

    def get_files_match(self, pattern: str) -> list[str]:
        return glob(pattern)
