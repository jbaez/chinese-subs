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
<font color="#ffffff">‎VIDEO 原创动画剧集</font><br><font color="#00ffff">‎VIDEO  yuán chuàng dòng huà jù jí</font>

2
00:01:20,350 --> 00:01:22,970
<font color="#ffffff">‎真不愧是天下第一刺客</font><br><font color="#00ffff">‎ zhēn bù kuì shì tiān xià dì yī cì kè</font>

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
<font color="#00ffff">‎真不愧是天下第一刺客</font>

5
00:01:20,350 --> 00:01:22,970
You really are the greatest killer
in the world.

'''


CHINESE_SUBTITLE_WITH_PINYIN_AND_ENGLISH = '''1
00:00:06,850 --> 00:00:09,970
<font color="#ffffff">‎VIDEO 原创动画剧集</font><br><font color="#00ffff">‎VIDEO  yuán chuàng dòng huà jù jí</font>

2
00:00:26,100 --> 00:00:29,270
MISSION 1
KILL BAD PEOPLE, EARN GOOD MONEY

3
00:00:42,180 --> 00:00:44,600
TARGET

4
00:01:20,350 --> 00:01:22,970
<font color="#ffffff">‎真不愧是天下第一刺客</font><br><font color="#00ffff">‎ zhēn bù kuì shì tiān xià dì yī cì kè</font>

5
00:01:20,350 --> 00:01:22,970
You really are the greatest killer
in the world.

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
<font color="#00ffff">‎ zhēn bù kuì shì tiān xià dì yī cì kè</font>

5
00:01:20,350 --> 00:01:22,970
You really are the greatest killer
in the world.

'''


def get_embedded_ass_fixture() -> FileInfoDto:
    return FileInfoDto.parse_file('src/tests/fixture_file_info_ass.json')


def get_embedded_srt_fixture() -> FileInfoDto:
    return FileInfoDto.parse_file('src/tests/fixture_file_info_srt.json')
