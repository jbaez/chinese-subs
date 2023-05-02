import asstosrt
from infra.file_system_interface import IFileSystem


class SubtitleConverter:
    def __init__(self, file_system: IFileSystem) -> None:
        self._file_system = file_system

    def convert_ass_to_srt(self, ass_file_path: str, srt_file_path: str) -> None:
        ass_file = self._file_system.open(ass_file_path)
        srt_subtitle = asstosrt.convert(ass_file)
        self._file_system.write(srt_file_path, srt_subtitle)
