from infra.file_info_reader_interface import FileInfoDto, IFileInfoReader
from typing import Dict


class FileInfoReaderFake(IFileInfoReader):
    def __init__(self, path_to_info: Dict[str, FileInfoDto]):
        self.path_to_info = path_to_info

    def file_exists_at_path(self, file_path: str) -> bool:
        return file_path in self.path_to_info

    def get_file_info(self, file_path: str) -> FileInfoDto | None:
        if not self.file_exists_at_path(file_path):
            return None
        return self.path_to_info[file_path]
