from enum import Enum
from infra.file_system_interface import IFileSystem
from pypinyin import pinyin
import srt


class Color(Enum):
    WHITE = '#ffffff'
    CYAN = '#00ffff'


class SubtitleManipulator:
    def __init__(self, file_system: IFileSystem) -> None:
        self._file_system = file_system

    def _to_pinyin(self, chinese: str):
        return ' '.join([seg[0] for seg in pinyin(chinese)])

    def _get_text_with_color(self, subtitle: srt.Subtitle, color: Color | None) -> str:
        if color is None:
            return subtitle

        content = subtitle.content
        new_content = f'<font color="{color.value}">{content}</font>'
        subtitle.content = new_content
        return subtitle

    def add_pinyin_to_subtitle(
            self,
            src_path_chinese: str,
            out_path: str,
            keep_chinese: bool = True) -> None:
        converted_subs: list[srt.Subtitle] = []

        with self._file_system.open(file=src_path_chinese, encoding='utf-8') as fi:
            subs = srt.parse(fi)
            srt.sort_and_reindex(subs, start_index=1, in_place=True, skip=True)

            for sub in subs:
                content = sub.content
                new_content = f'<font color="#ffffff">{content}</font><br>' if keep_chinese else ''
                new_content += f'<font color="#00ffff">{self._to_pinyin(content)}</font>'
                sub.content = new_content
                converted_subs.append(sub)

            self._file_system.write(out_path, srt.compose(converted_subs))

    def add_language_to_subtitle(
            self,
            src_path: str,
            src_other_language_path: str,
            out_path: str,
            src_color: Color | None = None,
            src_other_color: Color | None = None) -> None:
        converted_subs: list[srt.Subtitle] = []

        with self._file_system.open(file=src_path, encoding='utf-8') as src_file,\
                self._file_system.open(file=src_other_language_path, encoding='utf-8') as src_other_file:
            original_subs = srt.parse(src_file)
            additional_subs = srt.parse(src_other_file)

            for sub in original_subs:
                converted_subs.append(
                    self._get_text_with_color(sub, src_color))

            for sub in additional_subs:
                converted_subs.append(
                    self._get_text_with_color(sub, src_other_color))

        srt.sort_and_reindex(converted_subs, start_index=1,
                             in_place=True, skip=True)
        self._file_system.write(out_path, srt.compose(converted_subs))
