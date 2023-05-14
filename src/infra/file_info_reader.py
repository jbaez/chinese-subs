import subprocess
import os
from infra.file_info_reader_interface import IFileInfoReader, FileInfoDto


class FileInfoReader(IFileInfoReader):
    def get_file_info(self, file_path: str) -> FileInfoDto:
        raw_json = subprocess.check_output(
            ['mkvmerge', '-J', '-i', file_path],
            stderr=subprocess.STDOUT)
        return FileInfoDto.parse_raw(raw_json)

    def extract_subtitle(self, file_path: str, track_id: int, output_path: str) -> None:
        id_and_output = f"{track_id}:{output_path}"
        subprocess.check_output(
            ['mkvextract', file_path, 'tracks', id_and_output],
            stderr=subprocess.STDOUT)
