from unittest import TestCase
from infra.file_info_reader_fake import FileInfoReaderFake
from infra.file_system_fake import FileSystemFake
from tests.fixture_file_file_info import get_supported_and_unsupported_fixture


class TestFileInfoReaderFake(TestCase):
    def test_file_exists_at_path(self):
        '''
            When the file exists
            Then returns true
        '''
        file_system = FileSystemFake()
        sut = FileInfoReaderFake(
            path_to_info={
                'some/file/path/video.mkv': None
            },
            file_system=file_system)

        self.assertTrue(sut.file_exists_at_path('some/file/path/video.mkv'))

    def test_file_does_not_exist_at_path(self):
        '''
            When the file does not exist
            Then returns false
        '''
        file_system = FileSystemFake()
        sut = FileInfoReaderFake(
            path_to_info={
                'some/file/path/video.mkv': None
            },
            file_system=file_system)

        self.assertFalse(sut.file_exists_at_path('wrong/path/to/video.mkv'))

    def test_get_file_info(self):
        '''
            When the file exists
            Then returns the file info
        '''
        expected_file_info = get_supported_and_unsupported_fixture()
        file_system = FileSystemFake()
        sut = FileInfoReaderFake(
            path_to_info={
                'some/file/path/video.mkv': expected_file_info
            },
            file_system=file_system)

        file_info = sut.get_file_info('some/file/path/video.mkv')

        self.assertEqual(file_info, expected_file_info)

    def test_get_file_info_when_file_does_not_exist(self):
        '''
            When the file does not exist
            Then it returns none
        '''
        file_system = FileSystemFake()
        sut = FileInfoReaderFake(
            path_to_info={
                'some/file/path/video.mkv': None
            },
            file_system=file_system)

        self.assertIsNone(sut.get_file_info('wrong/path/to/video.mkv'))
