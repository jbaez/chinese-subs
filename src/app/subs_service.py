from infra.file_info_reader_interface import IFileInfoReader, Language, TrackSubCodec
from infra.file_system_interface import IFileSystem
from app.exceptions.path_not_loaded_exception import PathNotLoadedException
from app.core.subtitle_converter import SubtitleConverter
from app.core.subtitle_manipulator import SubtitleManipulator
from app.subtitle_dto import SubtitleLanguageDto, SubtitleGenerateResult
import os

TEMP_EXTRACTED_ASS_FILE_PATH = 'temp_extracted_ass'
TEMP_CONVERTED_SRT_FILE_PATH = 'temp_converted.srt'


class SubsService:
    _file_path: str | None = None

    def __init__(
            self, file_info_reader: IFileInfoReader,
            file_system: IFileSystem):
        self._file_info_reader = file_info_reader
        self._file_system = file_system

    def _get_file_path_with_extension(self, _file_path: str, new_extension: str) -> str:
        base, _ = os.path.splitext(_file_path)
        return base + new_extension

    def load_path(self, file_path: str) -> bool:
        self._file_path = file_path
        return self._file_info_reader.file_exists_at_path(file_path)

    def get_chinese_subtitles(self) -> list[SubtitleLanguageDto]:
        if self._file_path is None:
            raise PathNotLoadedException()

        file_info = self._file_info_reader.get_file_info(self._file_path)
        if file_info is None:
            return []

        all_available_tracks = [track for track in file_info.tracks
                                if track.codec == TrackSubCodec.ASS
                                and track.properties.language == Language.CHINESE]

        return list(map(lambda track: SubtitleLanguageDto(
            id=track.id, language=track.properties.language, codec=track.codec),
            all_available_tracks))

    def generate_chinese_subtitle_with_pinyin(self, subtitle_id: int | str | None = None) -> SubtitleGenerateResult:
        if self._file_path is None:
            return SubtitleGenerateResult.NOT_LOADED

        chinese_subtitles = [subtitle for subtitle in self.get_chinese_subtitles()
                             if subtitle.language == Language.CHINESE]

        if chinese_subtitles.count == 0:
            return SubtitleGenerateResult.NO_CHINESE_FOUND

        if subtitle_id is None:
            chinese_subtitle = next((sub for sub in chinese_subtitles
                                    if sub.language == Language.CHINESE), None)
        else:
            if isinstance(subtitle_id, str):
                try:
                    subtitle_id = int(subtitle_id)
                except ValueError:
                    return SubtitleGenerateResult.NO_CHINESE_FOUND

            chinese_subtitle = next((sub for sub in chinese_subtitles
                                    if sub.id == subtitle_id), None)

        if chinese_subtitle is None:
            return SubtitleGenerateResult.NO_CHINESE_FOUND

        if chinese_subtitle.codec is not TrackSubCodec.ASS:
            return SubtitleGenerateResult.CODEC_NOT_SUPPORTED

        srt_file_path = TEMP_CONVERTED_SRT_FILE_PATH
        self._file_info_reader.extract_subtitle(
            self._file_path,
            chinese_subtitle.id,
            TEMP_EXTRACTED_ASS_FILE_PATH)

        converter = SubtitleConverter(self._file_system)
        converter.convert_ass_to_srt(
            TEMP_EXTRACTED_ASS_FILE_PATH, srt_file_path)

        final_file_path = self._get_file_path_with_extension(
            self._file_path, '.srt')
        manipulator = SubtitleManipulator(self._file_system)
        manipulator.add_pinyin_to_subtitle(srt_file_path, final_file_path)

        return SubtitleGenerateResult.SUCCESS
