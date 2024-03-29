from enum import Enum
from infra.file_info_reader_interface import Language, TrackSubCodec
from pydantic import BaseModel


class SubtitleLanguageDto(BaseModel):
    id: int
    language: Language | str
    codec: TrackSubCodec | str


class SubtitleExternalExtension(Enum):
    SRT = '.srt'
    ASS = '.ass'


class SubtitleExternalDto(BaseModel):
    id: str
    path: str
    extension: SubtitleExternalExtension


class SubtitleGenerateResult(Enum):
    SUCCESS = 'SUCCESS'
    NOT_LOADED = 'NOT_LOADED'
    NO_SUBTITLES_FOUND = 'NO_SUBTITLES_FOUND'
    NO_CHINESE_FOUND = 'NO_CHINESE_FOUND'
    CODEC_NOT_SUPPORTED = 'CODEC_NOT_SUPPORTED'
