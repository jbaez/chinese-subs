from unittest import TestCase
from infra.file_info_reader_fake import FileInfoReaderFake
from infra.file_info_reader_interface import Language
from app.subs_service import SubsService
from app.exceptions.path_not_loaded_exception import PathNotLoadedException
from tests.fixture_file_file_info import get_supported_and_unsupported_fixture


class TestSubsServiceOpen(TestCase):
    '''
        Given the path to a single video file with subs is valid
    '''

    def setUp(self) -> None:
        self.file_path = 'some/file/path/video.mkv'
        fileInfo = get_supported_and_unsupported_fixture()
        file_info_reader = FileInfoReaderFake({
            self.file_path: fileInfo
        })
        self.sut = SubsService(file_info_reader)

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
        Given the path to a file with supported and unsupported 
        languages has been loaded
    '''

    def setUp(self) -> None:
        file_path = 'some/file/path/video.mkv'
        file_info = get_supported_and_unsupported_fixture()
        file_info_reader = FileInfoReaderFake({
            file_path: file_info
        })
        self.sut = SubsService(file_info_reader)
        self.sut.load_path(file_path)

    def test_get_available_languages(self):
        '''
            when asking for available languages
            then returns only the available languages
        '''
        expected_languages = [Language.CHINESE, Language.ENGLISH]
        available_languages = self.sut.get_available_languages()

        self.assertCountEqual(available_languages, expected_languages)
