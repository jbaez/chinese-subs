from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel


class Language(Enum):
    CHINESE = 'chi'
    ENGLISH = 'eng'


class TrackType(Enum):
    VIDEO = 'video'
    AUDIO = 'audio'
    SUBTITLE = 'subtitles'


class TrackSubCodec(Enum):
    ASS = 'SubStationAlpha'
    SRT = 'SubRip/SRT'


class TrackInfoProperties(BaseModel):
    language: Language | str


class TrackInfo(BaseModel):
    codec: TrackSubCodec | str
    type: TrackType
    id: int
    properties: TrackInfoProperties


class FileInfoDto(BaseModel):
    file_name: str
    tracks: list[TrackInfo]


class IFileInfoReader(ABC):
    @abstractmethod
    def get_file_info(self, file_path: str) -> FileInfoDto:
        pass

    @abstractmethod
    def extract_subtitle(self, file_path: str, track_id: int, output_path: str) -> None:
        pass
