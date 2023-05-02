from infra.file_system_interface import IFileSystem
from io import BytesIO, TextIOWrapper


class FileSystemFake(IFileSystem):
    _files: dict[str, str] = {}

    def open(self, file: str, encoding='utf-8') -> TextIOWrapper:
        bytes_data = self._files.get(file, '').encode('utf-8')
        buffer = BytesIO(bytes_data)
        return TextIOWrapper(buffer=buffer)

    def read(self, path: str) -> str:
        return self._files.get(path, '')

    def write(self, path: str, content: str) -> None:
        self._files[path] = content
