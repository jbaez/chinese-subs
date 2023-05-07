from typing import Literal
from app.subtitle_service import AddAdditionalLanguage, AddAdditionalLanguageMode, SubtitleService
from app.subtitle_dto import SubtitleGenerateResult
from infra.file_info_reader import FileInfoReader
from infra.file_system import FileSystem
from infra.file_info_reader_interface import Language
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter


CHINESE_WITH_PINYIN: Literal['CHINESE_WITH_PINYIN'] = 'CHINESE_WITH_PINYIN'


def get_generate_subtitle_mode() -> AddAdditionalLanguageMode | Literal['CHINESE_WITH_PINYIN']:
    mode = input('\nGenerate subtitle mode:\n'
                 + 'a - chinese with pinyin\n'
                 + 'b - other language with pinyin\n'
                 + 'c - chinese with pinyin and other language\n'
                 + 'Input choice: ')
    if mode == 'a':
        return CHINESE_WITH_PINYIN
    elif mode == 'b':
        return AddAdditionalLanguageMode.WITH_PINYIN
    elif mode == 'c':
        return AddAdditionalLanguageMode.WITH_CHINESE_AND_PINYIN
    else:
        print('Invalid mode')
        return get_generate_subtitle_mode()


def main():
    file_reader = FileInfoReader()
    file_system = FileSystem()
    subtitle_service = SubtitleService(file_reader, file_system)
    print('*** Chinese subtitle tool ***')

    path_completer = PathCompleter()
    file_path = prompt('Input video file path: ', completer=path_completer)
    file_exists = subtitle_service.load_path(file_path)
    if not file_exists:
        print('File not found with given path')
        return

    embedded_subtitles = subtitle_service.get_embedded_subtitles()
    external_subtitles = subtitle_service.get_external_subtitles()
    if embedded_subtitles.count == 0 and external_subtitles.count == 0:
        print('No subtitles found')

    if len(embedded_subtitles) > 0:
        print('\nEmbedded subtitles found: ')
        for subtitle in embedded_subtitles:
            if isinstance(subtitle.language, Language):
                subtitle_value = subtitle.language.value
            else:
                subtitle_value = subtitle.language
            print(f'ID: {subtitle.id} - {subtitle_value}')

    if len(external_subtitles) > 0:
        print('\nExternal subtitles found: ')
        for subtitle in external_subtitles:
            print(f'ID: {subtitle.id} - {subtitle.path}')

    mode = get_generate_subtitle_mode()

    subtitle_id = input('\nInput Chinese subtitle ID: ')

    if isinstance(mode, AddAdditionalLanguageMode):
        additional_subtitle_id = input(
            '\nInput additional language subtitle ID: ')

        if additional_subtitle_id == '':
            print('No additional language subtitle ID provided\n')
            main()
            return

        result = subtitle_service.generate_subtitle_with_additional_language(
            subtitle_id,
            AddAdditionalLanguage(
                mode=mode,
                subtitle_id=additional_subtitle_id
            ))
    else:
        result = subtitle_service.generate_chinese_subtitle_with_pinyin(
            subtitle_id)

    if result == SubtitleGenerateResult.CODEC_NOT_SUPPORTED:
        return print('Codec not supported')
    if result == SubtitleGenerateResult.NO_CHINESE_FOUND:
        return print('No chinese subtitles found')
    if result == SubtitleGenerateResult.NOT_LOADED:
        return print('No file loaded')
    if result == SubtitleGenerateResult.SUCCESS:
        return print('Success')


if __name__ == '__main__':
    main()
