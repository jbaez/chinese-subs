from infra.file_info_reader_interface import FileInfoDto, IFileInfoReader
from infra.file_system_interface import IFileSystem


class FileInfoReaderFake(IFileInfoReader):
    _extracted_content: list[str] = []

    def __init__(
            self,
            path_to_info: dict[str, FileInfoDto],
            file_system: IFileSystem):

        self._path_to_info = path_to_info
        self._file_system = file_system

    def add_extracted_content(self, content: str) -> None:
        self._extracted_content.append(content)

    def get_file_info(self, file_path: str) -> FileInfoDto:
        return self._path_to_info[file_path]

    def extract_subtitle(self, file_path: str, track_id: int, output_path: str) -> None:
        self._file_system.write(
            path=output_path,
            content=self._extracted_content.pop(0))
