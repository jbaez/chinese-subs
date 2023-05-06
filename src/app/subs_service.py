from infra.file_info_reader_interface import IFileInfoReader, Language, TrackSubCodec
from infra.file_system_interface import IFileSystem
from app.exceptions.path_not_loaded_exception import PathNotLoadedException
from app.core.subtitle_converter import SubtitleConverter
from app.core.subtitle_manipulator import SubtitleManipulator
from app.subtitle_dto import SubtitleLanguageDto, SubtitleExternalDto, SubtitleGenerateResult
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

    def _get_file_path(self) -> str:
        if self._file_path is None:
            raise PathNotLoadedException()
        return self._file_path

    def _get_base_file_path_appending(self, file_path: str, append_to_base: str) -> str:
        base, _ = os.path.splitext(file_path)
        return base + append_to_base

    def _get_external_file_id(self, index: int) -> str:
        return f'ext-{index}'

    def _is_embedded_subtitle(self, id: int | str) -> bool:
        if isinstance(id, int):
            return True
        return id.isnumeric()

    def load_path(self, file_path: str) -> bool:
        self._file_path = file_path
        return self._file_info_reader.file_exists_at_path(file_path)

    def get_embedded_chinese_subtitles(self) -> list[SubtitleLanguageDto]:
        file_path = self._get_file_path()
        file_info = self._file_info_reader.get_file_info(file_path)
        if file_info is None:
            return []

        all_available_tracks = [track for track in file_info.tracks
                                if track.codec == TrackSubCodec.ASS
                                and track.properties.language == Language.CHINESE]

        return list(map(lambda track: SubtitleLanguageDto(
            id=track.id, language=track.properties.language, codec=track.codec),
            all_available_tracks))

    def get_external_subtitles(self) -> list[SubtitleExternalDto]:
        file_path = self._get_file_path()
        external_subtitles: list[SubtitleExternalDto] = []
        file_path_base = self._get_base_file_path_appending(file_path, '')
        subtitle_paths = self._file_system.get_files_match(f'{file_path_base}*.srt') + \
            self._file_system.get_files_match(f'{file_path_base}*.ass')

        for i, path in enumerate(subtitle_paths):
            external_subtitles.append(
                SubtitleExternalDto(path=path, id=self._get_external_file_id(i)))

        return external_subtitles

    def generate_chinese_subtitle_with_pinyin(self, subtitle_id: int | str) -> SubtitleGenerateResult:
        if self._file_path is None:
            return SubtitleGenerateResult.NOT_LOADED

        chinese_subtitles = [subtitle for subtitle in self.get_embedded_chinese_subtitles()
                             if subtitle.language == Language.CHINESE]
        external_subtitles = self.get_external_subtitles()

        if len(chinese_subtitles) == 0 and len(external_subtitles) == 0:
            return SubtitleGenerateResult.NO_SUBTITLES_FOUND

        ass_file_path: str | None = None
        if len(chinese_subtitles) > 0:
            if self._is_embedded_subtitle(subtitle_id):
                chinese_subtitle = next((sub for sub in chinese_subtitles
                                        if sub.id == int(subtitle_id)), None)
            else:
                chinese_subtitle = None

            if chinese_subtitle is not None:
                if chinese_subtitle.codec is not TrackSubCodec.ASS:
                    return SubtitleGenerateResult.CODEC_NOT_SUPPORTED

                ass_file_path = TEMP_EXTRACTED_ASS_FILE_PATH
                self._file_info_reader.extract_subtitle(
                    self._file_path,
                    chinese_subtitle.id,
                    ass_file_path)
            elif len(external_subtitles) == 0:
                return SubtitleGenerateResult.NO_CHINESE_FOUND

        if len(external_subtitles) > 0:
            if not self._is_embedded_subtitle(subtitle_id):
                source_subtitle = next((sub for sub in external_subtitles
                                        if sub.id == subtitle_id))
                if (source_subtitle is not None):
                    ass_file_path = source_subtitle.path

        if ass_file_path is not None:
            srt_file_path = TEMP_CONVERTED_SRT_FILE_PATH
            converter = SubtitleConverter(self._file_system)
            converter.convert_ass_to_srt(
                ass_file_path, srt_file_path)
            if ass_file_path == TEMP_EXTRACTED_ASS_FILE_PATH:
                self._file_system.remove(ass_file_path)

        final_file_path = self._get_base_file_path_appending(
            self._file_path, ' generated.srt')
        manipulator = SubtitleManipulator(self._file_system)
        manipulator.add_pinyin_to_subtitle(srt_file_path, final_file_path)

        self._file_system.remove(srt_file_path)

        return SubtitleGenerateResult.SUCCESS
