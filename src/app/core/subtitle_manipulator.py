from pypinyin import pinyin
import srt
from infra.file_system_interface import IFileSystem


class SubtitleManipulator:
    def __init__(self, file_system: IFileSystem) -> None:
        self._file_system = file_system

    def _to_pinyin(self, chinese: str):
        return ' '.join([seg[0] for seg in pinyin(chinese)])

    def add_pinyin_to_subtitle(self, src_path: str, out_path: str) -> None:
        converted_subs: list[srt.Subtitle] = []

        with self._file_system.open(file=src_path, encoding='utf-8') as fi:
            subs = srt.parse(fi)
            srt.sort_and_reindex(subs, start_index=1, in_place=True, skip=True)

            sub: srt.Subtitle
            for sub in subs:
                content = sub.content
                new_content = f'<font color="#ffffff">{content}</font><br>'
                new_content += f'<font color="#00ffff">{self._to_pinyin(content)}</font>'
                sub.content = new_content
                converted_subs.append(sub)

            self._file_system.write(out_path, srt.compose(converted_subs))
