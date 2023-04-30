import subprocess
import os
from infra.file_info_reader_interface import IFileInfoReader, FileInfoDto


class FileInfoReader(IFileInfoReader):

    def file_exists_at_path(self, file_path: str) -> bool:
        return os.path.exists(file_path)

    def get_file_info(self, file_path: str) -> FileInfoDto | None:
        if not self.file_exists_at_path(file_path):
            return None

        raw_json = subprocess.check_output(
            ['mkvmerge', '-J', '-i', file_path],
            stderr=subprocess.STDOUT)
        return FileInfoDto.parse_raw(raw_json)
