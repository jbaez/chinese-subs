from infra.file_info_reader_interface import FileInfoDto
from enum import Enum


class SubTrackID(Enum):
    ENG = 2
    CHI = 3


VIDEO_FILE_PATH = 'some/file/path/video.mkv'
VIDEO_2_FILE_PATH = 'some/file/path/video_2.mkv'
VIDEOS_DIR_PATH = 'some/file/path'
SUBTITLE_EXPECTED_PATH = 'some/file/path/video generated.srt'
SUBTITLE_2_EXPECTED_PATH = 'some/file/path/video generated.srt'

CHINESE_SUBTITLE_ASS = '''[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 1080
Timer: 100.0
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,sans-serif,71,&H00FFFFFF,&H00FFFFFF,&H000F0F0F,&H000F0F0F,0,0,0,0,100,100,0,0.00,1,2,3,2,20,20,20,0

[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:06.85,0:00:09.97,Default,,0,0,0,,‎VIDEO 原创动画剧集
Dialogue: 0,0:01:20.35,0:01:22.97,Default,,0,0,0,,‎真不愧是天下第一刺客
'''

ENGLISH_SUBTITLE_ASS = '''[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 1080
Timer: 100.0
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,sans-serif,71,&H00FFFFFF,&H00FFFFFF,&H000F0F0F,&H000F0F0F,0,0,0,0,100,100,0,0.00,1,2,3,2,20,20,20,0

[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:26.10,0:00:29.27,Default,,0,0,0,,MISSION 1\\NKILL BAD PEOPLE, EARN GOOD MONEY
Dialogue: 0,0:00:42.18,0:00:44.60,Default,,0,0,0,,TARGET
Dialogue: 0,0:01:20.35,0:01:22.97,Default,,0,0,0,,You really are the greatest killer\\Nin the world.
'''

CHINESE_SUBTITLE_SRT = '''1
00:00:06,850 --> 00:00:09,970
‎VIDEO 原创动画剧集

2
00:01:20,350 --> 00:01:22,970
‎真不愧是天下第一刺客

'''

ENGLISH_SUBTITLE_SRT = '''1
00:00:26,100 --> 00:00:29,270
MISSION 1
KILL BAD PEOPLE, EARN GOOD MONEY

2
00:00:42,180 --> 00:00:44,600
TARGET

3
00:01:20,350 --> 00:01:22,970
You really are the greatest killer
in the world.

'''

CHINESE_SUBTITLE_WITH_PINYIN = '''1
00:00:06,850 --> 00:00:09,970
‎VIDEO 原创动画剧集
<font color="#00ffff">‎VIDEO  yuán chuàng dòng huà jù jí</font>

2
00:01:20,350 --> 00:01:22,970
‎真不愧是天下第一刺客
<font color="#00ffff">‎ zhēn bù kuì shì tiān xià dì yī cì kè</font>

'''

CHINESE_SUBTITLE_WITH_ENGLISH = '''1
00:00:06,850 --> 00:00:09,970
<font color="#00ffff">‎VIDEO 原创动画剧集</font>

2
00:00:26,100 --> 00:00:29,270
MISSION 1
KILL BAD PEOPLE, EARN GOOD MONEY

3
00:00:42,180 --> 00:00:44,600
TARGET

4
00:01:20,350 --> 00:01:22,970
You really are the greatest killer
in the world.
<font color="#00ffff">‎真不愧是天下第一刺客</font>

'''


CHINESE_SUBTITLE_WITH_PINYIN_AND_ENGLISH = '''1
00:00:06,850 --> 00:00:09,970
‎VIDEO 原创动画剧集
<font color="#00ffff">‎VIDEO  yuán chuàng dòng huà jù jí</font>

2
00:00:26,100 --> 00:00:29,270
MISSION 1
KILL BAD PEOPLE, EARN GOOD MONEY

3
00:00:42,180 --> 00:00:44,600
TARGET

4
00:01:20,350 --> 00:01:22,970
You really are the greatest killer
in the world.
‎真不愧是天下第一刺客
<font color="#00ffff">‎ zhēn bù kuì shì tiān xià dì yī cì kè</font>

'''

ENGLISH_SUBTITLE_WITH_PINYIN = '''1
00:00:06,850 --> 00:00:09,970
<font color="#00ffff">‎VIDEO  yuán chuàng dòng huà jù jí</font>

2
00:00:26,100 --> 00:00:29,270
MISSION 1
KILL BAD PEOPLE, EARN GOOD MONEY

3
00:00:42,180 --> 00:00:44,600
TARGET

4
00:01:20,350 --> 00:01:22,970
You really are the greatest killer
in the world.
<font color="#00ffff">‎ zhēn bù kuì shì tiān xià dì yī cì kè</font>

'''

CHINESE_SUBTITLE_SRT_UNMATCHED_TIMINGS_SRT = '''1
00:00:06,850 --> 00:00:09,970
‎VIDEO 原创动画剧集

2
00:01:20,350 --> 00:01:22,970
‎真不愧是天下第一刺客

3
00:02:20,791 --> 00:02:22,625
‪那個髮型師竟然是…

4
00:02:22,708 --> 00:02:26,083
‪聽說他要去玄武國取首領的人頭了

5
00:03:45,333 --> 00:03:49,416
‪是吗？那个吸血鬼赤牙吗？

6
00:03:49,500 --> 00:03:53,416
‪-不是很强的吗？
‪-对啊 我也听说了

'''

ENGLISH_SUBTITLE_UNMATCHED_TIMINGS_SRT = '''1
00:00:26,100 --> 00:00:29,270
MISSION 1
KILL BAD PEOPLE, EARN GOOD MONEY

2
00:00:42,180 --> 00:00:44,600
TARGET

3
00:01:20,350 --> 00:01:22,970
You really are the greatest killer
in the world.

4
00:02:20,791 --> 00:02:22,583
That hairdresser can't be…

5
00:02:22,666 --> 00:02:25,375
I heard that he was going to
behead the leader of Xuanwu.

6
00:03:45,208 --> 00:03:46,208
Yeah?

7
00:03:47,208 --> 00:03:49,250
That vampire Redtooth?

8
00:03:49,333 --> 00:03:51,000
Wasn't he really tough?

'''

CHINESE_SUBTITLE_WITH_ENGLISH_UNMATCHED_TIMINGS = '''1
00:00:06,850 --> 00:00:09,970
<font color="#00ffff">‎VIDEO 原创动画剧集</font>

2
00:00:26,100 --> 00:00:29,270
MISSION 1
KILL BAD PEOPLE, EARN GOOD MONEY

3
00:00:42,180 --> 00:00:44,600
TARGET

4
00:01:20,350 --> 00:01:22,970
You really are the greatest killer
in the world.
<font color="#00ffff">‎真不愧是天下第一刺客</font>

5
00:02:20,791 --> 00:02:22,625
That hairdresser can't be…
<font color="#00ffff">‪那個髮型師竟然是…</font>

6
00:02:22,666 --> 00:02:26,083
I heard that he was going to
behead the leader of Xuanwu.
<font color="#00ffff">‪聽說他要去玄武國取首領的人頭了</font>

7
00:03:45,208 --> 00:03:46,208
Yeah?

8
00:03:45,333 --> 00:03:49,416
<font color="#00ffff">‪是吗？那个吸血鬼赤牙吗？</font>

9
00:03:47,208 --> 00:03:49,250
That vampire Redtooth?

10
00:03:49,333 --> 00:03:51,000
Wasn't he really tough?

11
00:03:49,500 --> 00:03:53,416
<font color="#00ffff">‪-不是很强的吗？
‪-对啊 我也听说了</font>

'''


def get_embedded_ass_fixture() -> FileInfoDto:
    return FileInfoDto.parse_file('src/tests/fixture_file_info_ass.json')


def get_embedded_srt_fixture() -> FileInfoDto:
    return FileInfoDto.parse_file('src/tests/fixture_file_info_srt.json')
