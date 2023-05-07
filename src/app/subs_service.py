from enum import Enum
from typing import NamedTuple
from infra.file_info_reader_interface import IFileInfoReader, Language, TrackSubCodec
from infra.file_system_interface import IFileSystem
from app.exceptions.path_not_loaded_exception import PathNotLoadedException
from app.core.subtitle_converter import SubtitleConverter
from app.core.subtitle_manipulator import SubtitleManipulator
from app.subtitle_dto import SubtitleExternalExtension, SubtitleLanguageDto, SubtitleExternalDto, SubtitleGenerateResult
import os

TEMP_EXTRACTED_ASS_FILE_PATH = 'temp_extracted_ass'
TEMP_CONVERTED_SRT_FILE_PATH = 'temp_converted.srt'
TEMP_PINYIN_SRT_FILE_PATH = 'temp_pinyin.srt'


class AddAdditionalLanguageMode(Enum):
    WITH_PINYIN = 'WITH_PINYIN'
    WITH_CHINESE_AND_PINYIN = 'WITH_CHINESE_AND_PINYIN'


class AddAdditionalLanguage(NamedTuple):
    mode: AddAdditionalLanguageMode
    subtitle_id: int | str


class SubsService:
    _file_path: str | None = None
    _supported_extensions: list[str] = [
        extension.value for extension in SubtitleExternalExtension]

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

    def _get_external_subtitle_extension(self, file_path: str) -> SubtitleExternalExtension | None:
        _, extension = os.path.splitext(file_path)
        if extension in self._supported_extensions:
            return SubtitleExternalExtension(extension)
        return None

    def _generate_and_get_srt_file_path(
            self,
            file_path: str,
            subtitle_id: int | str,
            validate_is_chinese: bool = True) -> str | SubtitleGenerateResult:
        embedded_subtitles = [subtitle for subtitle in self.get_embedded_subtitles()
                              if (validate_is_chinese == False) or (subtitle.language == Language.CHINESE)]
        external_subtitles = self.get_external_subtitles()

        if len(embedded_subtitles) == 0 and len(external_subtitles) == 0:
            return SubtitleGenerateResult.NO_SUBTITLES_FOUND

        ass_file_path: str | None = None
        srt_file_path: str | None = None
        if len(embedded_subtitles) > 0:
            if self._is_embedded_subtitle(subtitle_id):
                embedded_subtitle = next((sub for sub in embedded_subtitles
                                          if sub.id == int(subtitle_id)), None)
            else:
                embedded_subtitle = None

            if embedded_subtitle is not None:
                if embedded_subtitle.codec is not TrackSubCodec.ASS:
                    return SubtitleGenerateResult.CODEC_NOT_SUPPORTED

                ass_file_path = TEMP_EXTRACTED_ASS_FILE_PATH
                self._file_info_reader.extract_subtitle(
                    file_path,
                    embedded_subtitle.id,
                    ass_file_path)
            elif len(external_subtitles) == 0:
                return SubtitleGenerateResult.NO_CHINESE_FOUND

        if len(external_subtitles) > 0:
            if not self._is_embedded_subtitle(subtitle_id):
                source_subtitle = next((sub for sub in external_subtitles
                                        if sub.id == subtitle_id))
                if (source_subtitle is not None):
                    if source_subtitle.extension == SubtitleExternalExtension.ASS:
                        ass_file_path = source_subtitle.path
                    elif source_subtitle.extension == SubtitleExternalExtension.SRT:
                        srt_file_path = source_subtitle.path

        if ass_file_path is not None:
            srt_file_path = TEMP_CONVERTED_SRT_FILE_PATH
            converter = SubtitleConverter(self._file_system)
            converter.convert_ass_to_srt(
                ass_file_path, srt_file_path)
            if ass_file_path == TEMP_EXTRACTED_ASS_FILE_PATH:
                self._file_system.remove(ass_file_path)

        if srt_file_path is None:
            return SubtitleGenerateResult.NO_SUBTITLES_FOUND

        return srt_file_path

    def _generate_subtitle(
            self,
            chinese_subtitle_id: int | str,
            additional_subtitle: AddAdditionalLanguage | None = None) -> SubtitleGenerateResult:
        if self._file_path is None:
            return SubtitleGenerateResult.NOT_LOADED

        srt_file_path = self._generate_and_get_srt_file_path(
            self._file_path, chinese_subtitle_id)

        if isinstance(srt_file_path, SubtitleGenerateResult):
            return srt_file_path

        if additional_subtitle is None or\
                (additional_subtitle and additional_subtitle.mode == AddAdditionalLanguageMode.WITH_CHINESE_AND_PINYIN):
            keep_chinese = True
        else:
            keep_chinese = False

        if additional_subtitle is None:
            pinyin_file_path = self._get_base_file_path_appending(
                self._file_path, ' generated.srt')
        else:
            pinyin_file_path = TEMP_PINYIN_SRT_FILE_PATH

        manipulator = SubtitleManipulator(self._file_system)
        manipulator.add_pinyin_to_subtitle(
            srt_file_path, pinyin_file_path, keep_chinese)

        if srt_file_path == TEMP_CONVERTED_SRT_FILE_PATH:
            self._file_system.remove(srt_file_path)

        if additional_subtitle is not None:
            srt_file_path = self._generate_and_get_srt_file_path(
                self._file_path, additional_subtitle.subtitle_id, False)
            if isinstance(srt_file_path, SubtitleGenerateResult):
                return srt_file_path

            final_file_path = self._get_base_file_path_appending(
                self._file_path, ' generated.srt')
            manipulator.add_language_to_subtitle(
                pinyin_file_path, srt_file_path, final_file_path)

            if srt_file_path == TEMP_CONVERTED_SRT_FILE_PATH:
                self._file_system.remove(srt_file_path)

            if pinyin_file_path == TEMP_PINYIN_SRT_FILE_PATH:
                self._file_system.remove(pinyin_file_path)

        return SubtitleGenerateResult.SUCCESS

    def load_path(self, file_path: str) -> bool:
        self._file_path = file_path
        return self._file_info_reader.file_exists_at_path(file_path)

    def get_embedded_subtitles(self) -> list[SubtitleLanguageDto]:
        file_path = self._get_file_path()
        file_info = self._file_info_reader.get_file_info(file_path)
        if file_info is None:
            return []

        all_available_tracks = [track for track in file_info.tracks
                                if track.codec == TrackSubCodec.ASS]

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
            extension = self._get_external_subtitle_extension(path)
            if extension is not None:
                external_subtitles.append(
                    SubtitleExternalDto(path=path,
                                        id=self._get_external_file_id(i),
                                        extension=extension))

        return external_subtitles

    def generate_chinese_subtitle_with_pinyin(
            self,
            subtitle_id: int | str) -> SubtitleGenerateResult:

        return self._generate_subtitle(subtitle_id)

    def generate_subtitle_with_additional_language(
            self,
            chinese_subtitle_id: int | str,
            other_subtitle: AddAdditionalLanguage) -> SubtitleGenerateResult:
        return self._generate_subtitle(chinese_subtitle_id, other_subtitle)
