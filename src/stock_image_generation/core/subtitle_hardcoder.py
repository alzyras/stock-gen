import secrets

import ffmpeg


def add_subtitles_with_ffmpeg(
    input_video: str,
    input_audio: str,
    subtitle_file: str,
    output_file: str,
    text_size: int = 24,
    text_color: str = "#FFFFFF",
    box_color: str = "#000000",
    outline_color: str = "#000000",
    outline_transparency: float = 1.0,
    background_color: str = "#000000",
    background_transparency: float = 0.0,
    vertical_position: str = "bottom",
    orientation: str = "horizontal",
) -> None:
    # Map vertical position strings to pixel values
    vertical_position_map = {
        "top": 10,
        "middle": 120,
        "bottom": "(h-text_h)-10",
    }

    if vertical_position not in vertical_position_map:
        error_message = (
            "Invalid vertical position. Choose from 'top', 'middle', 'bottom'."
        )
        raise ValueError(error_message)

    # Get the duration of the audio file
    audio_info = ffmpeg.probe(input_audio)
    audio_duration = float(audio_info["format"]["duration"])

    # Get the duration of the video file
    video_info = ffmpeg.probe(input_video)
    video_duration = float(video_info["format"]["duration"])

    if audio_duration > video_duration:
        error_message = "Audio duration is longer than video duration."
        raise ValueError(error_message)

    # Choose a random start time for the video segment
    start_time = secrets.SystemRandom().uniform(0, video_duration - audio_duration)

    # Load the video and audio streams
    video = ffmpeg.input(input_video, ss=start_time, t=audio_duration)
    audio = ffmpeg.input(input_audio)

    video = video.filter(
        "subtitles",
        subtitle_file,
        force_style=(
            f"FontSize={text_size},PrimaryColour=&H{int(text_color[1:], 16):06X}&,"
            f"OutlineColour=&H{int(outline_color[1:], 16):06X}&,"
            f"BackColour=&H{int(background_color[1:], 16):06X}&,"
            f"BorderStyle=3,Outline={outline_transparency},Shadow=0,"
            f"MarginV={vertical_position_map[vertical_position]},"
            f"Box=1,BoxColour=&H{int(box_color[1:], 16):06X}&"
            f"{int(background_transparency * 255):02X}"
        ),
    )

    # If orientation is vertical, crop the video to 9x16 aspect ratio
    # from the middle
    if orientation == "vertical":
        video = video.filter("crop", "ih*9/16", "ih", "(iw-ow)/2", 0)

    # Combine video and audio
    output = ffmpeg.output(
        video,
        audio,
        output_file,
        vcodec="libx264",
        acodec="aac",
        strict="experimental",
    )

    # Run the ffmpeg command
    ffmpeg.run(output)


if __name__ == "__main__":
    background_video = "bg.mp4"
    srt_file = "test.srt"
    output_video = "output.mp4"
    input_audio = "test.mp3"

    add_subtitles_with_ffmpeg(
        input_video=background_video,
        input_audio=input_audio,
        subtitle_file=srt_file,
        output_file=output_video,
        text_size=40,
        text_color="#FFFFFF",
        box_color="#000000",
        outline_color="#000000",
        outline_transparency=0.5,
        background_color="#000000",
        background_transparency=0.1,
        vertical_position="middle",
        orientation="vertical",
    )
