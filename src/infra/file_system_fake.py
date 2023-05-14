import os
from infra.file_system_interface import IFileSystem
from io import BytesIO, TextIOWrapper


class FileSystemFake(IFileSystem):

    def __init__(self, initial_files: dict[str, str] = {}, directory_path: str | None = None) -> None:
        '''
        Parameters:
        initial_files: A dictionary of file paths and their contents.
        directory_path: To be used when doing batch work on a directory that contains the files.
        '''
        self._files = initial_files.copy()
        self._directory_path = directory_path

    def get_file_paths(self) -> list[str]:
        return list(self._files.keys())

    def path_exists(self, path: str) -> bool:
        if self._directory_path is not None:
            if self._directory_path == path:
                return True

        return path in self._files

    def path_is_dir(self, path: str) -> bool:
        return self._directory_path == path

    def open(self, file: str, encoding='utf-8') -> TextIOWrapper:
        bytes_data = self._files.get(file, '').encode('utf-8')
        buffer = BytesIO(bytes_data)
        return TextIOWrapper(buffer=buffer)

    def read(self, path: str) -> str:
        return self._files.get(path, '')

    def write(self, path: str, content: str) -> None:
        self._files[path] = content

    def remove(self, path: str) -> None:
        self._files.pop(path)

    def list_dir(self, path: str) -> list[str]:
        file_list = [os.path.basename(f) for f in self._files.keys()
                     if os.path.dirname(f) == path]

        return file_list

    def get_dir_path(self, file_path: str) -> str:
        return os.path.dirname(file_path)

    def join_path(self, parent_dir: str, file_name: str) -> str:
        return os.path.join(parent_dir, file_name)
