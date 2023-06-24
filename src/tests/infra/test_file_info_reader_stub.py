from unittest import TestCase
from infra.file_info_reader_fake import FileInfoReaderFake
from infra.file_system_fake import FileSystemFake
from tests.fixture_file_file_info import get_embedded_ass_fixture


class TestFileInfoReaderFake(TestCase):
    def test_get_file_info(self):
        '''
            When the file exists
            Then returns the file info
        '''
        expected_file_info = get_embedded_ass_fixture()
        file_system = FileSystemFake()
        sut = FileInfoReaderFake(
            path_to_info={
                'some/file/path/video.mkv': expected_file_info
            },
            file_system=file_system)

        file_info = sut.get_file_info('some/file/path/video.mkv')

        self.assertEqual(file_info, expected_file_info)
