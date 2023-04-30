from infra.file_info_reader_interface import IFileInfoReader, Language, TrackSubCodec
from app.exceptions.path_not_loaded_exception import PathNotLoadedException


class SubsService:
    file_path: str | None = None

    def __init__(self, file_info_reader: IFileInfoReader):
        self._file_info_reader = file_info_reader

    def load_path(self, file_path: str) -> bool:
        self.file_path = file_path
        return self._file_info_reader.file_exists_at_path(file_path)

    def get_available_languages(self) -> list[Language]:
        if self.file_path is None:
            raise PathNotLoadedException()
        file_info = self._file_info_reader.get_file_info(self.file_path)
        if file_info is None:
            return []

        tracks = file_info.tracks
        all_languages = [track.properties.language for track in tracks
                         if track.codec == TrackSubCodec.ASS]
        available_languages = list(Language)
        return [language for language
                in available_languages if language in all_languages]
