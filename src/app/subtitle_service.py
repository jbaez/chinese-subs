from enum import Enum
from typing import List, NamedTuple, Tuple
from infra.file_info_reader_interface import IFileInfoReader, Language, TrackSubCodec
from infra.file_system_interface import IFileSystem
from app.exceptions.path_not_loaded_exception import PathNotLoadedException
from app.core.subtitle_converter import SubtitleConverter
from app.core.subtitle_manipulator import Color, SubtitleManipulator
from app.subtitle_dto import SubtitleExternalExtension, SubtitleLanguageDto, SubtitleExternalDto, SubtitleGenerateResult
import os

TEMP_EXTRACTED_ASS_FILE_PATH = 'temp_extracted_ass'
TEMP_PINYIN_SRT_FILE_PATH = 'temp_pinyin.srt'

supported_sub_codecs = [TrackSubCodec.ASS, TrackSubCodec.SRT]


class AddAdditionalLanguageMode(Enum):
    WITH_PINYIN = 'WITH_PINYIN'
    WITH_CHINESE_AND_PINYIN = 'WITH_CHINESE_AND_PINYIN'
    WITHOUT_PINYIN = 'WITHOUT_PINYIN'


class AddAdditionalLanguage(NamedTuple):
    mode: AddAdditionalLanguageMode
    subtitle_id: int | str


class LoadResult(Enum):
    FILE_LOADED = 'FILE_LOADED'
    DIR_LOADED = 'DIR_LOADED'
    INVALID_PATH = 'INVALID_PATH'


class ValidatedFilePath(NamedTuple):
    path: str
    is_temp: bool


class SubtitleService:
    _file_path: str | None = None
    _file_path_load_result: LoadResult | None
    _supported_extensions: list[str] = [
        extension.value for extension in SubtitleExternalExtension]

    def __init__(
            self, file_info_reader: IFileInfoReader,
            file_system: IFileSystem):
        self._file_info_reader = file_info_reader
        self._file_system = file_system

    def _get_file_path(self) -> Tuple[str, LoadResult]:
        if self._file_path is None or self._file_path_load_result is None:
            raise PathNotLoadedException()
        return (self._file_path, self._file_path_load_result)

    def _get_supported_files_in_dir(self, dir_path: str) -> list[str]:
        return [self._file_system.join_path(dir_path, f)
                for f in self._file_system.list_dir(dir_path)
                if not self._file_system.path_is_dir(f) and f.endswith(('.mp4', '.mkv'))]

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

    def _get_subtitle_srt_file_path(
            self,
            file_path: str,
            subtitle_id: int | str,
            output_file_path: str,
            validate_is_chinese: bool = True,) -> ValidatedFilePath | SubtitleGenerateResult:
        embedded_subtitles = [subtitle for subtitle in self.get_embedded_subtitles()
                              if (validate_is_chinese == False) or (subtitle.language == Language.CHINESE)]
        external_subtitles = self.get_external_subtitles()

        if len(embedded_subtitles) == 0 and len(external_subtitles) == 0:
            return SubtitleGenerateResult.NO_SUBTITLES_FOUND

        ass_file_path: str | None = None
        srt_file_path: str | None = None
        is_temp_subtitle = True
        if len(embedded_subtitles) > 0:
            if self._is_embedded_subtitle(subtitle_id):
                embedded_subtitle = next((sub for sub in embedded_subtitles
                                          if sub.id == int(subtitle_id)), None)
            else:
                embedded_subtitle = None

            if embedded_subtitle is not None:
                if embedded_subtitle.codec not in supported_sub_codecs:
                    return SubtitleGenerateResult.CODEC_NOT_SUPPORTED

                if embedded_subtitle.codec is TrackSubCodec.ASS:
                    ass_file_path = TEMP_EXTRACTED_ASS_FILE_PATH
                    self._file_info_reader.extract_subtitle(
                        file_path,
                        embedded_subtitle.id,
                        ass_file_path)
                elif embedded_subtitle.codec is TrackSubCodec.SRT:
                    srt_file_path = output_file_path
                    self._file_info_reader.extract_subtitle(
                        file_path,
                        embedded_subtitle.id,
                        srt_file_path)

            elif len(external_subtitles) == 0:
                return SubtitleGenerateResult.NO_CHINESE_FOUND

        if srt_file_path is None and len(external_subtitles) > 0:
            if not self._is_embedded_subtitle(subtitle_id):
                source_subtitle = next((sub for sub in external_subtitles
                                        if sub.id == subtitle_id))
                if (source_subtitle is not None):
                    if source_subtitle.extension == SubtitleExternalExtension.ASS:
                        ass_file_path = source_subtitle.path
                    elif source_subtitle.extension == SubtitleExternalExtension.SRT:
                        srt_file_path = source_subtitle.path
                        is_temp_subtitle = False

        if ass_file_path is not None:
            srt_file_path = output_file_path
            converter = SubtitleConverter(self._file_system)
            converter.convert_ass_to_srt(
                ass_file_path, srt_file_path)
            if ass_file_path == TEMP_EXTRACTED_ASS_FILE_PATH:
                self._file_system.remove(ass_file_path)

        if srt_file_path is None:
            return SubtitleGenerateResult.NO_SUBTITLES_FOUND

        return ValidatedFilePath(is_temp=is_temp_subtitle, path=srt_file_path)

    def _generate_subtitle(self,
                           chinese_subtitle_id: int | str,
                           additional_subtitle: AddAdditionalLanguage | None = None) -> SubtitleGenerateResult:
        try:
            file_path, file_path_type = self._get_file_path()
        except:
            return SubtitleGenerateResult.NOT_LOADED

        if file_path_type == LoadResult.DIR_LOADED:
            supported_files = self._get_supported_files_in_dir(file_path)
            result = SubtitleGenerateResult.NO_SUBTITLES_FOUND
            for file in supported_files:
                result = self._generate_subtitle_for_path(
                    file, chinese_subtitle_id, additional_subtitle)
                if result != SubtitleGenerateResult.SUCCESS:
                    return result

            return result

        else:
            return self._generate_subtitle_for_path(file_path, chinese_subtitle_id, additional_subtitle)

    def _generate_subtitle_for_path(
            self,
            file_path: str,
            chinese_subtitle_id: int | str,
            additional_subtitle: AddAdditionalLanguage | None = None) -> SubtitleGenerateResult:

        temp_file_paths: List[str] = []
        srt_file_path = self._get_subtitle_srt_file_path(
            file_path=file_path,
            subtitle_id=chinese_subtitle_id,
            output_file_path='temp_one.srt')

        if isinstance(srt_file_path, SubtitleGenerateResult):
            return srt_file_path

        if srt_file_path.is_temp:
            temp_file_paths.append(srt_file_path.path)

        if additional_subtitle is None or\
                (additional_subtitle and additional_subtitle.mode == AddAdditionalLanguageMode.WITH_CHINESE_AND_PINYIN):
            keep_chinese = True
        else:
            keep_chinese = False

        if additional_subtitle is None:
            pinyin_file_path = self._get_base_file_path_appending(
                file_path, ' generated.srt')
        elif additional_subtitle.mode != AddAdditionalLanguageMode.WITHOUT_PINYIN:
            pinyin_file_path = TEMP_PINYIN_SRT_FILE_PATH
            temp_file_paths.append(pinyin_file_path)
        else:
            pinyin_file_path = srt_file_path.path

        manipulator = SubtitleManipulator(self._file_system)

        if additional_subtitle is None or additional_subtitle.mode != AddAdditionalLanguageMode.WITHOUT_PINYIN:
            manipulator.add_pinyin_to_subtitle(
                srt_file_path.path, pinyin_file_path, keep_chinese)

        if additional_subtitle is not None:
            srt_file_path = self._get_subtitle_srt_file_path(
                file_path=file_path,
                subtitle_id=additional_subtitle.subtitle_id,
                output_file_path='temp_two.srt',
                validate_is_chinese=False)

            if isinstance(srt_file_path, SubtitleGenerateResult):
                return srt_file_path

            if srt_file_path.is_temp:
                temp_file_paths.append(srt_file_path.path)

            src_color = Color.CYAN if additional_subtitle.mode == AddAdditionalLanguageMode.WITHOUT_PINYIN else None

            final_file_path = self._get_base_file_path_appending(
                file_path, ' generated.srt')
            manipulator.add_language_to_subtitle(
                src_path=pinyin_file_path,
                src_other_language_path=srt_file_path.path,
                out_path=final_file_path,
                src_color=src_color)

        for temp_file_path in temp_file_paths:
            self._file_system.remove(temp_file_path)

        return SubtitleGenerateResult.SUCCESS

    def load_path(self, file_path: str) -> LoadResult:
        self._file_path = file_path
        if not self._file_system.path_exists(file_path):
            self._file_path_load_result = LoadResult.INVALID_PATH
        elif self._file_system.path_is_dir(file_path):
            self._file_path_load_result = LoadResult.DIR_LOADED
        else:
            self._file_path_load_result = LoadResult.FILE_LOADED

        return self._file_path_load_result

    def get_embedded_subtitles(self) -> list[SubtitleLanguageDto]:
        file_path, file_path_type = self._get_file_path()

        if file_path_type == LoadResult.DIR_LOADED:
            supported_files = self._get_supported_files_in_dir(file_path)
            if len(supported_files) == 0:
                return []

            file_info = self._file_info_reader.get_file_info(
                supported_files[0])
        else:
            file_info = self._file_info_reader.get_file_info(file_path)

        if file_info is None:
            return []

        all_available_tracks = [track for track in file_info.tracks
                                if track.codec in supported_sub_codecs]

        return list(map(lambda track: SubtitleLanguageDto(
            id=track.id, language=track.properties.language, codec=track.codec),
            all_available_tracks))

    def get_external_subtitles(self) -> list[SubtitleExternalDto]:
        file_path, _ = self._get_file_path()
        external_subtitles: list[SubtitleExternalDto] = []
        dir_path = self._file_system.get_dir_path(file_path)
        subtitle_files = [self._file_system.join_path(dir_path, f)
                          for f in self._file_system.list_dir(dir_path)]

        for i, path in enumerate(subtitle_files):
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
