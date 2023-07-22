from enum import Enum
from infra.file_system_interface import IFileSystem
from pypinyin import pinyin
import srt

MAX_SECONDS_DIFF = 0.6


class Color(Enum):
    WHITE = '#ffffff'
    CYAN = '#00ffff'


class SubtitleManipulator:
    def __init__(self, file_system: IFileSystem) -> None:
        self._file_system = file_system

    def _to_pinyin(self, chinese: str):
        return ' '.join([seg[0] for seg in pinyin(chinese)])

    def _add_color_to_text(self, subtitle: srt.Subtitle, color: Color) -> srt.Subtitle:
        content = subtitle.content
        new_content = f'<font color="{color.value}">{content}</font>'
        subtitle.content = new_content
        return subtitle

    def _should_adjust_subtitle_start_time(self, source_sub: srt.Subtitle, sub_to_adjust: srt.Subtitle) -> bool:
        if source_sub.start < sub_to_adjust.start:
            return abs(sub_to_adjust.start.total_seconds() - source_sub.start.total_seconds()) < MAX_SECONDS_DIFF

        return False

    def _should_adjust_subtitle_end_time(self, source_sub: srt.Subtitle, sub_to_adjust: srt.Subtitle) -> bool:
        if source_sub.end > sub_to_adjust.end:
            return abs(source_sub.end.total_seconds() - sub_to_adjust.end.total_seconds()) < MAX_SECONDS_DIFF

        return False

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

            srt.sort_and_reindex(original_subs, start_index=1,
                                 in_place=True, skip=True)
            srt.sort_and_reindex(additional_subs, start_index=1,
                                 in_place=True, skip=True)

            original_sub = next(original_subs, None)
            additional_sub = next(additional_subs, None)

            while original_sub is not None or additional_sub is not None:
                if original_sub is not None and (additional_sub is None or original_sub.end < additional_sub.start):
                    if src_color is not None:
                        self._add_color_to_text(original_sub, src_color)

                    converted_subs.append(original_sub)
                    original_sub = next(original_subs, None)
                elif additional_sub is not None and (original_sub is None or additional_sub.end < original_sub.start):
                    converted_subs.append(additional_sub)
                    additional_sub = next(additional_subs, None)
                elif original_sub is not None and additional_sub is not None:
                    if self._should_adjust_subtitle_start_time(source_sub=original_sub, sub_to_adjust=additional_sub):

                        additional_sub.start = original_sub.start
                    if self._should_adjust_subtitle_end_time(source_sub=original_sub, sub_to_adjust=additional_sub):
                        additional_sub.end = original_sub.end

                    if self._should_adjust_subtitle_start_time(source_sub=additional_sub, sub_to_adjust=original_sub):
                        original_sub.start = additional_sub.start
                    if self._should_adjust_subtitle_end_time(source_sub=additional_sub, sub_to_adjust=original_sub):
                        original_sub.end = additional_sub.end

                    if src_color is not None:
                        self._add_color_to_text(original_sub, src_color)

                    original_sub.content = additional_sub.content + '\n' + original_sub.content
                    converted_subs.append(original_sub)

                    original_sub = next(original_subs, None)
                    additional_sub = next(additional_subs, None)
                else:
                    pass

        self._file_system.write(out_path, srt.compose(converted_subs))
