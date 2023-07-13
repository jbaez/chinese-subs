import datetime
from enum import Enum
from infra.file_system_interface import IFileSystem
from pypinyin import pinyin
import srt
import srt_tools.utils as srt_utils
import operator


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

    def _merge_subs(self, subs: list[srt.Subtitle], acceptable_diff: int, attr: str, width: int):
        """
        Merge subs with similar start/end times together. This prevents the
        subtitles jumping around the screen.

        The merge is done in-place.
        This code is taken from srt_tools/srt-mux
        """
        sorted_subs = sorted(subs, key=operator.attrgetter(attr))
        acceptable_time_delta = datetime.timedelta(
            milliseconds=acceptable_diff)

        for subs in srt_utils.sliding_window(sorted_subs, width=width):
            current_sub = subs[0]
            future_subs = subs[1:]
            current_comp: datetime.timedelta = getattr(current_sub, attr)

            for future_sub in future_subs:
                future_comp: datetime.timedelta = getattr(future_sub, attr)
                if current_comp + acceptable_time_delta > future_comp:
                    setattr(future_sub, attr, current_comp)
                else:
                    # Since these are sorted, and this one didn't match, we can be
                    # sure future ones won't match either.
                    break

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
                if src_color is not None:
                    converted_subs.append(
                        self._get_text_with_color(sub, src_color))
                else:
                    converted_subs.append(sub)

            for sub in additional_subs:
                if src_other_color is not None:
                    converted_subs.append(
                        self._get_text_with_color(sub, src_other_color))
                else:
                    converted_subs.append(sub)

            self._merge_subs(converted_subs, 800, 'start', 2)
            self._merge_subs(converted_subs, 800, 'end', 2)

        output = srt_utils.compose_suggest_on_fail(converted_subs)

        self._file_system.write(out_path, output)
