from infra.file_info_reader_interface import FileInfoDto, IFileInfoReader
from infra.file_system_interface import IFileSystem


class FileInfoReaderFake(IFileInfoReader):

    def __init__(
            self,
            path_to_info: dict[str, FileInfoDto],
            file_system: IFileSystem):

        self._path_to_info = path_to_info
        self._file_system = file_system

    def set_extracted_content(self, content: str) -> None:
        self._extracted_content = content

    def file_exists_at_path(self, file_path: str) -> bool:
        return file_path in self._path_to_info

    def get_file_info(self, file_path: str) -> FileInfoDto | None:
        if not self.file_exists_at_path(file_path):
            return None
        return self._path_to_info[file_path]

    def extract_subtitle(self, file_path: str, track_id: int, output_path: str) -> None:
        if not self.file_exists_at_path(file_path):
            return
        self._file_system.write(
            path=output_path,
            content=self._extracted_content)
