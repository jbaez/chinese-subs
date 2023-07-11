from unittest import TestCase
from infra.file_info_reader_fake import FileInfoReaderFake
from infra.file_system_fake import FileSystemFake
from infra.file_info_reader_interface import Language, TrackSubCodec
from app.subtitle_service import AddAdditionalLanguage, AddAdditionalLanguageMode, LoadResult, SubtitleService
from app.exceptions.path_not_loaded_exception import PathNotLoadedException
from app.subtitle_dto import SubtitleExternalDto, SubtitleExternalExtension, SubtitleLanguageDto, SubtitleGenerateResult
from tests.fixture_file_file_info import CHINESE_SUBTITLE_WITH_ENGLISH, CHINESE_SUBTITLE_WITH_PINYIN_AND_ENGLISH, ENGLISH_SUBTITLE_ASS, ENGLISH_SUBTITLE_SRT, ENGLISH_SUBTITLE_WITH_PINYIN, SUBTITLE_2_EXPECTED_PATH, VIDEO_2_FILE_PATH, VIDEOS_DIR_PATH, get_embedded_ass_fixture,\
    VIDEO_FILE_PATH, SUBTITLE_EXPECTED_PATH, SubTrackID,\
    CHINESE_SUBTITLE_ASS, CHINESE_SUBTITLE_WITH_PINYIN, CHINESE_SUBTITLE_SRT, get_embedded_srt_fixture


class TestSubtitleServiceOpen(TestCase):
    '''
        Given the path to a single video file with embedded subs is valid
    '''

    def setUp(self) -> None:
        self.file_path = VIDEO_FILE_PATH
        file_info = get_embedded_ass_fixture()
        file_system = FileSystemFake(initial_files={self.file_path: ''})
        file_info_reader = FileInfoReaderFake(
            path_to_info={
                self.file_path: file_info
            },
            file_system=file_system)
        self.sut = SubtitleService(file_info_reader, file_system)

    def test_load_valid_path(self):
        '''
            When the file is loaded
            Then returns LoadResult.FILE_LOADED
        '''
        self.assertEqual(self.sut.load_path(
            self.file_path), LoadResult.FILE_LOADED)

    def test_attempt_to_load_with_invalid_path(self):
        '''
            When using an invalid path
            Then returns LoadResult.INVALID_PATH
        '''
        self.assertEqual(self.sut.load_path(
            'invalid_path'), LoadResult.INVALID_PATH)

    def test_attempt_to_use_app_if_not_loaded_exception(self):
        with self.assertRaises(PathNotLoadedException):
            self.sut.get_embedded_subtitles()


class TestSubtitleServiceEmbeddedAssSubs(TestCase):
    '''
        Given the path to a file with embedded
        subtitle languages with TrackSubCodec.ASS codec have been loaded
    '''

    def setUp(self) -> None:
        self.file_path = VIDEO_FILE_PATH
        file_info = get_embedded_ass_fixture()
        self.file_system = FileSystemFake(initial_files={self.file_path: ''})
        self.file_info_reader = FileInfoReaderFake(
            path_to_info={
                self.file_path: file_info
            },
            file_system=self.file_system)
        self.sut = SubtitleService(self.file_info_reader, self.file_system)
        self.sut.load_path(self.file_path)

    def test_get_embedded_subtitles(self):
        '''
            when asking for embedded subtitles
            then returns the chinese subtitles DTO
        '''
        expected_languages = [
            SubtitleLanguageDto(
                id=SubTrackID.CHI.value,
                language=Language.CHINESE,
                codec=TrackSubCodec.ASS),
            SubtitleLanguageDto(
                id=SubTrackID.ENG.value,
                language=Language.ENGLISH,
                codec=TrackSubCodec.ASS),
        ]
        available_languages = self.sut.get_embedded_subtitles()

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
            and any temporary files are deleted
        '''
        self.file_info_reader.add_extracted_content(CHINESE_SUBTITLE_ASS)
        result = self.sut.generate_chinese_subtitle_with_pinyin('3')

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         CHINESE_SUBTITLE_WITH_PINYIN)
        remaining_paths_after_cleanup = self.file_system.get_file_paths()
        self.assertEqual(len(remaining_paths_after_cleanup), 2)
        self.assertIn(SUBTITLE_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(self.file_path, remaining_paths_after_cleanup)

    def test_generate_chinese_subtitle_with_other_language(self):
        '''
            given there is a chinese subtitle with TrackSubCodec.ASS and ID 3
            when attempting to generate a subtitle with ID '3'
            and adding english as the additional language using ID '2'
            then a subtitle is generated with english with extension .srt
            and any temporary files are deleted
        '''
        self.file_info_reader.add_extracted_content(CHINESE_SUBTITLE_ASS)
        self.file_info_reader.add_extracted_content(ENGLISH_SUBTITLE_ASS)
        result = self.sut.generate_subtitle_with_additional_language('3', AddAdditionalLanguage(
            mode=AddAdditionalLanguageMode.WITHOUT_PINYIN, subtitle_id='2'))

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         CHINESE_SUBTITLE_WITH_ENGLISH)
        remaining_paths_after_cleanup = self.file_system.get_file_paths()
        print(remaining_paths_after_cleanup)
        self.assertEqual(len(remaining_paths_after_cleanup), 2)
        self.assertIn(SUBTITLE_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(self.file_path, remaining_paths_after_cleanup)

    def test_generate_chinese_subtitle_with_pinyin_and_additional_language(self):
        '''
            given there is a chinese subtitle with TrackSubCodec.ASS and ID 3
            and a english subtitle with TrackSubCodec.ASS and ID 2
            when generating a subtitle with chinese and pinyin using ID '3'
            and adding english as the additional language using ID '2'
            then a subtitle is generated with chinese, pinyin and english with extension .srt
            and any temporary files are deleted
        '''
        self.maxDiff = None
        self.file_info_reader.add_extracted_content(CHINESE_SUBTITLE_ASS)
        self.file_info_reader.add_extracted_content(ENGLISH_SUBTITLE_ASS)
        result = self.sut.generate_subtitle_with_additional_language(
            chinese_subtitle_id='3',
            other_subtitle=AddAdditionalLanguage(
                mode=AddAdditionalLanguageMode.WITH_CHINESE_AND_PINYIN,
                subtitle_id='2'))

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         CHINESE_SUBTITLE_WITH_PINYIN_AND_ENGLISH)
        remaining_paths_after_cleanup = self.file_system.get_file_paths()
        self.assertEqual(len(remaining_paths_after_cleanup), 2)
        self.assertIn(SUBTITLE_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(self.file_path, remaining_paths_after_cleanup)

    def test_generate_english_subtitle_with_pinyin(self):
        '''
            given there is a chinese subtitle with TrackSubCodec.ASS and ID 3
            and a english subtitle with TrackSubCodec.ASS and ID 2
            when generating a subtitle with pinyin using ID '3'
            and adding english as the additional language using ID '2'
            then a subtitle is generated with pinyin and english with extension .srt
            and any temporary files are deleted
        '''
        self.maxDiff = None
        self.file_info_reader.add_extracted_content(CHINESE_SUBTITLE_ASS)
        self.file_info_reader.add_extracted_content(ENGLISH_SUBTITLE_ASS)
        result = self.sut.generate_subtitle_with_additional_language(
            chinese_subtitle_id='3',
            other_subtitle=AddAdditionalLanguage(
                mode=AddAdditionalLanguageMode.WITH_PINYIN,
                subtitle_id='2'))

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         ENGLISH_SUBTITLE_WITH_PINYIN)
        remaining_paths_after_cleanup = self.file_system.get_file_paths()
        self.assertEqual(len(remaining_paths_after_cleanup), 2)
        self.assertIn(SUBTITLE_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(self.file_path, remaining_paths_after_cleanup)


class TestSubtitleServiceEmbeddedSrtSubs(TestCase):
    '''
        Given the path to a file with embedded
        subtitle languages with TrackSubCodec.SRT codec have been loaded
    '''

    def setUp(self) -> None:
        self.file_path = VIDEO_FILE_PATH
        file_info = get_embedded_srt_fixture()
        self.file_system = FileSystemFake(initial_files={self.file_path: ''})
        self.file_info_reader = FileInfoReaderFake(
            path_to_info={
                self.file_path: file_info
            },
            file_system=self.file_system)
        self.sut = SubtitleService(self.file_info_reader, self.file_system)
        self.sut.load_path(self.file_path)

    def test_get_embedded_subtitles(self):
        '''
            when asking for embedded subtitles
            then returns the chinese subtitles DTO
        '''
        expected_languages = [
            SubtitleLanguageDto(
                id=SubTrackID.CHI.value,
                language=Language.CHINESE,
                codec=TrackSubCodec.SRT),
            SubtitleLanguageDto(
                id=SubTrackID.ENG.value,
                language=Language.ENGLISH,
                codec=TrackSubCodec.SRT),
        ]
        available_languages = self.sut.get_embedded_subtitles()

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
            given there is a chinese subtitle with TrackSubCodec.SRT and ID 3
            when attempting to generate a subtitle with ID '3'
            then a subtitle is generated with pinyin and extension .srt
            and any temporary files are deleted
        '''
        self.file_info_reader.add_extracted_content(CHINESE_SUBTITLE_SRT)
        result = self.sut.generate_chinese_subtitle_with_pinyin('3')

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         CHINESE_SUBTITLE_WITH_PINYIN)
        remaining_paths_after_cleanup = self.file_system.get_file_paths()
        self.assertEqual(len(remaining_paths_after_cleanup), 2)
        self.assertIn(SUBTITLE_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(self.file_path, remaining_paths_after_cleanup)

    def test_generate_chinese_subtitle_with_pinyin_and_additional_language(self):
        '''
            given there is a chinese subtitle with TrackSubCodec.SRT and ID 3
            and a english subtitle with TrackSubCodec.SRT and ID 2
            when generating a subtitle with chinese and pinyin using ID '3'
            and adding english as the additional language using ID '2'
            then a subtitle is generated with chinese, pinyin and english with extension .srt
            and any temporary files are deleted
        '''
        self.maxDiff = None
        self.file_info_reader.add_extracted_content(CHINESE_SUBTITLE_SRT)
        self.file_info_reader.add_extracted_content(ENGLISH_SUBTITLE_SRT)
        result = self.sut.generate_subtitle_with_additional_language(
            chinese_subtitle_id='3',
            other_subtitle=AddAdditionalLanguage(
                mode=AddAdditionalLanguageMode.WITH_CHINESE_AND_PINYIN,
                subtitle_id='2'))

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         CHINESE_SUBTITLE_WITH_PINYIN_AND_ENGLISH)
        remaining_paths_after_cleanup = self.file_system.get_file_paths()
        self.assertEqual(len(remaining_paths_after_cleanup), 2)
        self.assertIn(SUBTITLE_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(self.file_path, remaining_paths_after_cleanup)

    def test_generate_english_subtitle_with_pinyin(self):
        '''
            given there is a chinese subtitle with TrackSubCodec.SRT and ID 3
            and a english subtitle with TrackSubCodec.SRT and ID 2
            when generating a subtitle with pinyin using ID '3'
            and adding english as the additional language using ID '2'
            then a subtitle is generated with pinyin and english with extension .srt
            and any temporary files are deleted
        '''
        self.maxDiff = None
        self.file_info_reader.add_extracted_content(CHINESE_SUBTITLE_SRT)
        self.file_info_reader.add_extracted_content(ENGLISH_SUBTITLE_SRT)
        result = self.sut.generate_subtitle_with_additional_language(
            chinese_subtitle_id='3',
            other_subtitle=AddAdditionalLanguage(
                mode=AddAdditionalLanguageMode.WITH_PINYIN,
                subtitle_id='2'))

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         ENGLISH_SUBTITLE_WITH_PINYIN)
        remaining_paths_after_cleanup = self.file_system.get_file_paths()
        self.assertEqual(len(remaining_paths_after_cleanup), 2)
        self.assertIn(SUBTITLE_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(self.file_path, remaining_paths_after_cleanup)


class TestSubtitleServiceEmbeddedAndExternalAssSubs(TestCase):
    '''
        Given the path to a file with one external subtitle with .ass extension
        has been loaded
    '''

    def setUp(self) -> None:
        file_path = VIDEO_FILE_PATH
        self._external_file_path = 'some/file/path/video.ass'
        file_info = get_embedded_ass_fixture()
        self.file_system = FileSystemFake(
            initial_files={self._external_file_path: CHINESE_SUBTITLE_ASS})
        self.file_info_reader = FileInfoReaderFake(
            path_to_info={
                file_path: file_info
            },
            file_system=self.file_system)
        self.sut = SubtitleService(self.file_info_reader, self.file_system)
        self.sut.load_path(file_path)

    def test_get_external_subtitles(self):
        '''
            when asking for external subtitles
            then it returns a list of SubtitleExternalDto
        '''
        external_subtitles = self.sut.get_external_subtitles()
        expected_dto = SubtitleExternalDto(
            id='ext-0', path=self._external_file_path, extension=SubtitleExternalExtension.ASS)

        self.assertCountEqual(external_subtitles, [expected_dto])

    def test_generate_chinese_subtitle_with_pinyin(self):
        '''
            when attempting to generate a subtitle with ID 'ext-0'
            then a subtitle is generated with pinyin and extension .srt
            and any temporary files are deleted
            and the original .ass file is kept
        '''
        result = self.sut.generate_chinese_subtitle_with_pinyin('ext-0')

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         CHINESE_SUBTITLE_WITH_PINYIN)
        remaining_paths_after_cleanup = self.file_system.get_file_paths()
        self.assertEqual(len(remaining_paths_after_cleanup), 2)
        self.assertIn(SUBTITLE_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(self._external_file_path, remaining_paths_after_cleanup)


class TestSubtitleServiceEmbeddedAndExternalSrtSubs(TestCase):
    '''
        Given the path to a file with one external subtitle with .srt extension
        has been loaded
    '''

    def setUp(self) -> None:
        file_path = VIDEO_FILE_PATH
        self._external_file_path = 'some/file/path/video.srt'
        file_info = get_embedded_ass_fixture()
        self.file_system = FileSystemFake(
            initial_files={self._external_file_path: CHINESE_SUBTITLE_SRT})
        self.file_info_reader = FileInfoReaderFake(
            path_to_info={
                file_path: file_info
            },
            file_system=self.file_system)
        self.sut = SubtitleService(self.file_info_reader, self.file_system)
        self.sut.load_path(file_path)

    def test_get_external_subtitles(self):
        '''
            when asking for external subtitles
            then it returns a list of SubtitleExternalDto
        '''
        external_subtitles = self.sut.get_external_subtitles()
        expected_dto = SubtitleExternalDto(
            id='ext-0', path=self._external_file_path, extension=SubtitleExternalExtension.SRT)

        self.assertCountEqual(external_subtitles, [expected_dto])

    def test_generate_chinese_subtitle_with_pinyin(self):
        '''
            when attempting to generate a subtitle with ID 'ext-0'
            then a subtitle is generated with pinyin and extension .srt
            and any temporary files are deleted
            and the original .srt file is kept
        '''
        result = self.sut.generate_chinese_subtitle_with_pinyin('ext-0')

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         CHINESE_SUBTITLE_WITH_PINYIN)
        remaining_paths_after_cleanup = self.file_system.get_file_paths()
        self.assertEqual(len(remaining_paths_after_cleanup), 2)
        self.assertIn(SUBTITLE_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(self._external_file_path, remaining_paths_after_cleanup)


class TestSubtitleServiceBatchDirectoryWithoutVideoFiles(TestCase):
    '''
        Given the path to a directory with files that has no supported videos
        has been loaded
    '''

    def setUp(self) -> None:
        self.file_path_1 = 'unsupported/videos/dir/path/one.mp3'
        self.file_path_2 = 'unsupported/videos/dir/path/two.jpg'
        self.file_path_dir = 'unsupported/videos/dir/path'
        self.file_system = FileSystemFake(
            initial_files={
                self.file_path_1: '',
                self.file_path_2: ''
            },
            directory_path=self.file_path_dir)
        self.file_info_reader = FileInfoReaderFake(
            path_to_info={},
            file_system=self.file_system)
        self.sut = SubtitleService(self.file_info_reader, self.file_system)
        self.sut.load_path(self.file_path_dir)

    def test_get_subtitles(self):
        '''
            when asking for external or embedded subtitles
            then it returns an empty list
        '''
        embedded_subtitles = self.sut.get_embedded_subtitles()
        external_subtitles = self.sut.get_external_subtitles()

        self.assertEqual(embedded_subtitles, [])
        self.assertEqual(external_subtitles, [])


class TestSubtitleServiceEmbeddedSubsBatch(TestCase):
    '''
        Given the path to a directory with 2 files, that both have the same
        embedded subtitle languages with TrackSubCodec.ASS codec, has been loaded
    '''

    def setUp(self) -> None:
        self.file_path_1 = VIDEO_FILE_PATH
        self.file_path_2 = VIDEO_2_FILE_PATH
        self.file_path_dir = VIDEOS_DIR_PATH
        file_info = get_embedded_ass_fixture()
        self.file_system = FileSystemFake(
            initial_files={
                self.file_path_1: '',
                self.file_path_2: ''
            },
            directory_path=self.file_path_dir)
        self.file_info_reader = FileInfoReaderFake(
            path_to_info={
                self.file_path_1: file_info,
                self.file_path_2: file_info
            },
            file_system=self.file_system)
        self.sut = SubtitleService(self.file_info_reader, self.file_system)
        self.sut.load_path(self.file_path_dir)

    def test_load_valid_path(self):
        '''
            When the directory is loaded
            Then returns true
        '''
        self.assertEqual(self.sut.load_path(
            self.file_path_dir), LoadResult.DIR_LOADED)

    def test_get_embedded_subtitles(self):
        '''
            when asking for embedded subtitles
            then returns the chinese subtitles DTO
        '''
        expected_languages = [
            SubtitleLanguageDto(
                id=SubTrackID.CHI.value,
                language=Language.CHINESE,
                codec=TrackSubCodec.ASS),
            SubtitleLanguageDto(
                id=SubTrackID.ENG.value,
                language=Language.ENGLISH,
                codec=TrackSubCodec.ASS),
        ]
        available_languages = self.sut.get_embedded_subtitles()

        self.assertCountEqual(available_languages, expected_languages)

    def test_generate_chinese_subtitle_with_pinyin(self):
        '''
            given there is a chinese subtitle with TrackSubCodec.ASS and ID 3 in both files
            when attempting to generate a subtitle with ID '3'
            then a subtitle is generated with pinyin and extension .srt for each file
            and any temporary files are deleted
        '''
        self.file_info_reader.add_extracted_content(CHINESE_SUBTITLE_ASS)
        self.file_info_reader.add_extracted_content(CHINESE_SUBTITLE_ASS)
        result = self.sut.generate_chinese_subtitle_with_pinyin('3')

        self.assertEqual(result, SubtitleGenerateResult.SUCCESS)
        self.assertEqual(self.file_system.read(SUBTITLE_EXPECTED_PATH),
                         CHINESE_SUBTITLE_WITH_PINYIN)
        self.assertEqual(self.file_system.read(SUBTITLE_2_EXPECTED_PATH),
                         CHINESE_SUBTITLE_WITH_PINYIN)

        remaining_paths_after_cleanup = self.file_system.get_file_paths()
        self.assertEqual(len(remaining_paths_after_cleanup), 4)
        self.assertIn(SUBTITLE_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(SUBTITLE_2_EXPECTED_PATH, remaining_paths_after_cleanup)
        self.assertIn(self.file_path_1, remaining_paths_after_cleanup)
        self.assertIn(self.file_path_2, remaining_paths_after_cleanup)
