from infra.file_system_interface import IFileSystem
from io import TextIOWrapper
import os


class FileSystem(IFileSystem):
    def path_exists(self, path: str) -> bool:
        return os.path.exists(path)

    def path_is_dir(self, path: str) -> bool:
        return os.path.isdir(path)

    def open(self, file: str, encoding='utf-8') -> TextIOWrapper:
        return open(file=file, encoding=encoding)

    def read(self, path: str) -> str:
        return self.open(path).read()

    def write(self, path: str, content: str) -> None:
        with open(path, 'w') as f:
            f.write(content)

    def remove(self, path: str) -> None:
        os.remove(path)

    def list_dir(self, path: str) -> list[str]:
        return os.listdir(path)

    def get_dir_path(self, file_path: str) -> str:
        return os.path.dirname(file_path)

    def join_path(self, parent_dir: str, file_name: str) -> str:
        return os.path.join(parent_dir, file_name)
