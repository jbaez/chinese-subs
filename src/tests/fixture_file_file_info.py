from infra.file_info_reader_interface import FileInfoDto


def get_supported_and_unsupported_fixture() -> FileInfoDto:
    return FileInfoDto.parse_file('src/tests/fixture_file_info_all_lang.json')
