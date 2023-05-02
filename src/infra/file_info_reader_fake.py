from infra.file_info_reader_interface import FileInfoDto, IFileInfoReader
from typing import Dict


class FileInfoReaderFake(IFileInfoReader):
    extracted_files: list[Dict[int, str]] = []

    def __init__(self, path_to_info: Dict[str, FileInfoDto]):
        self.path_to_info = path_to_info

    def file_exists_at_path(self, file_path: str) -> bool:
        return file_path in self.path_to_info

    def get_file_info(self, file_path: str) -> FileInfoDto | None:
        if not self.file_exists_at_path(file_path):
            return None
        return self.path_to_info[file_path]

    def extract_subtitle(self, file_path: str, track_id: int, output_path: str) -> None:
        if not self.file_exists_at_path(file_path):
            return
        self.extracted_files.append({track_id: output_path})
