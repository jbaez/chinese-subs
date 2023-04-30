from unittest import TestCase
from infra.file_info_reader_fake import FileInfoReaderFake
from tests.fixture_file_file_info import get_supported_and_unsupported_fixture


class TestFileInfoReaderFake(TestCase):
    def test_file_exists_at_path(self):
        '''
            When the file exists
            Then returns true
        '''
        sut = FileInfoReaderFake({
            'some/file/path/video.mkv': None
        })

        self.assertTrue(sut.file_exists_at_path('some/file/path/video.mkv'))

    def test_file_does_not_exist_at_path(self):
        '''
            When the file does not exist
            Then returns false
        '''
        sut = FileInfoReaderFake({
            'some/file/path/video.mkv': None
        })

        self.assertFalse(sut.file_exists_at_path('wrong/path/to/video.mkv'))

    def test_get_file_info(self):
        '''
            When the file exists
            Then returns the file info
        '''
        expected_file_info = get_supported_and_unsupported_fixture()
        sut = FileInfoReaderFake({
            'some/file/path/video.mkv': expected_file_info
        })

        file_info = sut.get_file_info('some/file/path/video.mkv')

        self.assertEqual(file_info, expected_file_info)

    def test_get_file_info_when_file_does_not_exist(self):
        '''
            When the file does not exist
            Then it returns none
        '''
        sut = FileInfoReaderFake({
            'some/file/path/video.mkv': None
        })

        self.assertIsNone(sut.get_file_info('wrong/path/to/video.mkv'))
