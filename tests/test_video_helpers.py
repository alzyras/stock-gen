from pydub import AudioSegment

from prompt_to_video.core.video.generate_video import add_background_music, parse_srt


def test_parse_srt_returns_second_offsets() -> None:
    subtitles = parse_srt(
        "1\n00:00:01,250 --> 00:00:02,500\nHello world\n",
    )

    assert subtitles == [
        {"start_time": 1.25, "end_time": 2.5, "text": "Hello world"},
    ]


def test_background_music_is_looped_and_trimmed() -> None:
    music = AudioSegment.silent(duration=400)

    result = add_background_music(
        total_duration=1.2, music_track=music, music_volume=0.5
    )

    assert len(result) == 1200
