from unittest import TestCase
from infra.file_info_reader_fake import FileInfoReaderFake
from infra.file_system_fake import FileSystemFake
from infra.file_info_reader_interface import Language, TrackSubCodec
from app.subs_service import SubsService, TEMP_EXTRACTED_ASS_FILE_PATH
from app.exceptions.path_not_loaded_exception import PathNotLoadedException
from app.subtitle_dto import SubtitleLanguageDto, SubtitleGenerateResult
from tests.fixture_file_file_info import get_supported_and_unsupported_fixture,\
    VIDEO_FILE_PATH, SUBTITLE_EXPECTED_PATH, SubTrackID,\
    CHINESE_SUBTITLE_ASS, CHINESE_SUBTITLE_WITH_PINYIN


class TestSubsServiceOpen(TestCase):
    '''
        Given the path to a single video file with subs is valid
    '''

    def setUp(self) -> None:
        self.file_path = VIDEO_FILE_PATH
        file_info = get_supported_and_unsupported_fixture()
        file_system = FileSystemFake()
        file_info_reader = FileInfoReaderFake(
            path_to_info={
                self.file_path: file_info
            },
            file_system=file_system)
        self.sut = SubsService(file_info_reader, file_system)

    def test_load_valid_path(self):
        '''
            When the file is loaded
            Then returns true
        '''
        self.assertTrue(self.sut.load_path(self.file_path))

    def test_attempt_to_use_app_if_not_loaded_exception(self):
        with self.assertRaises(PathNotLoadedException):
            self.sut.get_available_languages()


class TestFileReaderService(TestCase):
    '''
        Given the path to a file with embedded supported and unsupported
        subtitle languages with TrackSubCodec.ASS codec have been loaded
    '''

    def setUp(self) -> None:
        file_path = 'some/file/path/video.mkv'
        file_info = get_supported_and_unsupported_fixture()
        self.file_system = FileSystemFake()
        self.file_info_reader = FileInfoReaderFake(
            path_to_info={
                file_path: file_info
            },
            file_system=self.file_system)
        self.sut = SubsService(self.file_info_reader, self.file_system)
        self.sut.load_path(file_path)

    def test_get_available_languages(self):
        '''
            when asking for available subtitle languages
            then returns only the available subtitle languages
        '''
        expected_languages = [
            SubtitleLanguageDto(
                id=SubTrackID.CHI.value,
                language=Language.CHINESE,
                codec=TrackSubCodec.ASS),
            SubtitleLanguageDto(
                id=SubTrackID.ENG.value,
                language=Language.ENGLISH,
                codec=TrackSubCodec.ASS)
        ]
        available_languages = self.sut.get_available_languages()

        self.assertCountEqual(available_languages, expected_languages)

    def test_generate_subtile_with_id_not_found(self):
        '''
            when attempting to generate subtitle with pinyin with an ID
            that does not match any of the subtitles
            then returns NO_CHINESE_FOUND
        '''
        result = self.sut.generate_chinese_subtitle_with_pinyin(123)

        self.assertEqual(result, SubtitleGenerateResult.NO_CHINESE_FOUND)

    def test_generate_subtile_with_invalid_string_id(self):
        '''
            when attempting to generate subtitle with pinyin with
            a non-numeric string ID
            then returns NO_CHINESE_FOUND
        '''
        result = self.sut.generate_chinese_subtitle_with_pinyin('abc')

        self.assertEqual(result, SubtitleGenerateResult.NO_CHINESE_FOUND)

    def test_generate_chinese_subtitle_with_pinyin(self):
        '''
            given there is a chinese subtitle with TrackSubCodec.ASS and ID 3
            when attempting to generate a subtitle with ID '3'
            then a subtitle is generated with pinyin and extension .srt
        '''
        self.file_info_reader.set_extracted_content(CHINESE_SUBTITLE_ASS)
        result = self.sut.generate_chinese_subtitle_with_pinyin('3')

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         CHINESE_SUBTITLE_WITH_PINYIN)