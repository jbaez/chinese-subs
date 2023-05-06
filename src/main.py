from app.subs_service import SubsService
from app.subtitle_dto import SubtitleGenerateResult
from infra.file_info_reader import FileInfoReader
from infra.file_system import FileSystem
from infra.file_info_reader_interface import Language


def main():
    file_reader = FileInfoReader()
    file_system = FileSystem()
    subs_service = SubsService(file_reader, file_system)
    print('*** Add pinyin to Chinese subtitles ***')
    file_path = input('Input file path: ')
    file_exists = subs_service.load_path(file_path)
    if not file_exists:
        print('File does not exist')
        return

    subtitles = subs_service.get_embedded_chinese_subtitles()
    external_subtitles = subs_service.get_external_subtitles()
    if subtitles.count == 0 and external_subtitles.count == 0:
        print('No subtitles found')

    if len(subtitles) > 0:
        print('Embedded subtitles found: ')
        for subtitle in subtitles:
            if isinstance(subtitle.language, Language):
                subtitle_value = subtitle.language.value
            else:
                subtitle_value = subtitle.language
            print(f'ID: {subtitle.id} - {subtitle_value}')

    if len(external_subtitles) > 0:
        print('External subtitles found: ')
        for subtitle in external_subtitles:
            print(f'ID: {subtitle.id} - {subtitle.path}')

    subtitle_id = input('Input subtitle ID to add pinyin to: ')

    result = subs_service.generate_chinese_subtitle_with_pinyin(subtitle_id)
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
