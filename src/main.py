from app.subs_service import SubsService
from app.subtitle_dto import SubtitleGenerateResult
from infra.file_info_reader import FileInfoReader
from infra.file_system import FileSystem
from infra.file_info_reader_interface import Language


def main():
    file_path = ''
    file_reader = FileInfoReader()
    file_system = FileSystem()
    subs_service = SubsService(file_reader, file_system)
    subs_service.load_path(file_path)
    subtitles = subs_service.get_available_languages()
    if subtitles.count == 0:
        print('No subtitles found')
        return

    print('Subtitles found:')
    for subtitle in subtitles:
        if isinstance(subtitle.language, Language):
            subtitle_value = subtitle.language.value
        else:
            subtitle_value = subtitle.language
        print(f"{subtitle_value} - ID: {subtitle.id}")

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
