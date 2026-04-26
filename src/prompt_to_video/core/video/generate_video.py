import logging
import math
from io import BytesIO
from pathlib import Path
from typing import TypedDict

import pysrt
from mosaico.assets import create_asset
from mosaico.assets.audio import AudioAssetParams
from mosaico.assets.image import ImageAssetParams
from mosaico.assets.reference import AssetReference
from mosaico.assets.text import TextAssetParams
from mosaico.effects.pan import PanLeftEffect, PanRightEffect
from mosaico.positioning.relative import RelativePosition
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig
from mosaico.video.rendering import render_video
from PIL import Image, ImageFont
from pydub import AudioSegment

from prompt_to_video.settings import DATA_STORAGE_PATH, TEMP_AUDIOFILE_PATH

LOGGER = logging.getLogger(__name__)

VIDEO_WIDTH = 1920
FONT_SIZE = 48
FONT_FAMILY = "Arial"
TEXT_COLOR = "yellow"
STROKE_WIDTH = 3
Z_INDEX_IMAGE = 0
Z_INDEX_SUBTITLE = 2
DEFAULT_VOLUME = 1.0
DEFAULT_CODEC = "libx264"
DEFAULT_BITRATE = "50M"
DEFAULT_AUDIO_CODEC = "aac"
DEFAULT_FPS = 60
PRESET = "slow"
CRF = "18"
PIX_FMT = "yuv420p"


class Subtitle(TypedDict):
    start_time: float
    end_time: float
    text: str


def pil_image_to_bytes(image: Image.Image) -> bytes:
    """Convert a PIL image object to JPEG bytes."""
    with BytesIO() as output:
        image.save(output, format="JPEG")
        return output.getvalue()


def audio_segment_to_bytes(audio: AudioSegment) -> bytes:
    """Convert an audio segment to bytes."""
    with BytesIO() as output:
        audio.export(output, format="mp3")
        return output.getvalue()


def _subrip_time_to_seconds(time: pysrt.SubRipTime) -> float:
    return (
        time.hours * 3600
        + time.minutes * 60
        + time.seconds
        + time.milliseconds / 1000.0
    )


def parse_srt(srt_string: str) -> list[Subtitle]:
    """Parse SRT content into timeline-ready subtitles."""
    subtitles: list[Subtitle] = []
    try:
        srt_items = pysrt.from_string(srt_string)
    except (pysrt.Error, ValueError):
        LOGGER.exception("Error parsing SRT")
        return subtitles

    subtitles.extend(
        {
            "start_time": _subrip_time_to_seconds(subtitle.start),
            "end_time": _subrip_time_to_seconds(subtitle.end),
            "text": subtitle.text,
        }
        for subtitle in srt_items
    )
    return subtitles


def calculate_text_width(text: str) -> float:
    """Calculate rendered text width with a fallback font."""
    try:
        font = ImageFont.truetype(FONT_FAMILY, FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()
    return font.getlength(text)


def generate_image_ref(
    image: Image.Image,
    scene_index: int,
    image_index: int,
    start_time: float,
    time_per_image: float,
) -> tuple[AssetReference, object]:
    """Create a timeline reference and asset for one scene image."""
    asset_id = f"scene{scene_index}_img{image_index}"
    asset = create_asset("image", data=pil_image_to_bytes(image), id=asset_id)
    pan_effect = (
        PanLeftEffect(zoom_factor=1.05)
        if image_index % 2 == 0
        else PanRightEffect(zoom_factor=1.05)
    )

    image_start = start_time + image_index * time_per_image
    image_end = start_time + (image_index + 1) * time_per_image
    ref = (
        AssetReference.from_asset(asset)
        .with_start_time(image_start)
        .with_end_time(image_end)
        .with_effects(effects=[pan_effect])
        .with_params(params=ImageAssetParams(z_index=Z_INDEX_IMAGE, as_background=True))
    )
    return ref, asset


def generate_audio_ref(
    audio: AudioSegment,
    start_time: float,
    volume: float = DEFAULT_VOLUME,
    asset_id_appendix: str = "",
) -> tuple[AssetReference, object]:
    """Create a timeline reference and asset for one audio segment."""
    audio_asset = create_asset(
        "audio",
        data=audio_segment_to_bytes(audio),
        id=f"{asset_id_appendix}audio_{start_time}",
    )
    audio_ref = (
        AssetReference.from_asset(audio_asset)
        .with_start_time(start_time)
        .with_end_time(start_time + len(audio) / 1000)
        .with_params(params=AudioAssetParams(volume=volume))
    )
    return audio_ref, audio_asset


def generate_subtitle_ref(subtitle: Subtitle) -> tuple[AssetReference, object]:
    """Create a timeline reference and asset for one subtitle."""
    text_width = calculate_text_width(subtitle["text"])
    x_position = max((VIDEO_WIDTH - text_width) / 2 / VIDEO_WIDTH, 0)
    subtitle_asset = create_asset(
        "text",
        data=subtitle["text"],
        id=f"subtitle_{subtitle['start_time']}",
        params=TextAssetParams(
            font_size=FONT_SIZE,
            font_family=FONT_FAMILY,
            z_index=Z_INDEX_SUBTITLE,
            font_color=TEXT_COLOR,
            stroke_width=STROKE_WIDTH,
            position=RelativePosition(x=x_position, y=0.90),
        ),
    )
    subtitle_ref = (
        AssetReference.from_asset(subtitle_asset)
        .with_start_time(subtitle["start_time"])
        .with_end_time(subtitle["end_time"])
    )
    return subtitle_ref, subtitle_asset


def _gain_for_volume(volume: float) -> float:
    clamped = min(max(volume, 0.0), 1.0)
    if clamped == 0:
        return -120.0
    return 20 * math.log10(clamped)


def add_background_music(
    total_duration: float,
    music_track: AudioSegment,
    music_volume: float = 1.0,
) -> AudioSegment:
    """Loop or trim background music to match the requested duration."""
    total_duration_ms = int(total_duration * 1000)
    if total_duration_ms <= 0:
        msg = "Total duration must be greater than zero."
        raise ValueError(msg)

    if len(music_track) < total_duration_ms:
        loops = total_duration_ms // len(music_track) + 1
        music = (music_track * loops)[:total_duration_ms]
    else:
        music = music_track[:total_duration_ms]

    return music.apply_gain(_gain_for_volume(music_volume))


def _validate_inputs(
    images_per_scene: list[list[Image.Image]],
    audio_per_scene: list[AudioSegment],
) -> None:
    if len(images_per_scene) != len(audio_per_scene):
        msg = "images_per_scene and audio_per_scene must have the same length."
        raise ValueError(msg)
    if not audio_per_scene:
        msg = "At least one audio scene is required."
        raise ValueError(msg)
    if any(not images for images in images_per_scene):
        msg = "Every scene must include at least one image."
        raise ValueError(msg)


def generate_video_from_objects(
    video_title: str,
    images_per_scene: list[list[Image.Image]],
    audio_per_scene: list[AudioSegment],
    srt_content: str | None = None,
    output_path: str | Path = DATA_STORAGE_PATH,
    background_music: AudioSegment | None = None,
    music_volume: float = 1.0,
    fade_duration: int = 0,
) -> str:
    """Generate a video from scene images, narration audio, and optional subtitles."""
    _validate_inputs(images_per_scene, audio_per_scene)

    project = VideoProject(config=VideoProjectConfig(title=video_title))
    scenes: list[Scene] = []
    start_time = 0.0
    subtitles = parse_srt(srt_content) if srt_content else []
    total_audio_length = sum(len(audio) / 1000 for audio in audio_per_scene)

    if background_music is not None:
        music_track = add_background_music(
            total_audio_length,
            background_music,
            music_volume=music_volume,
        )
        if fade_duration > 0:
            fade_ms = int(fade_duration * 1000)
            music_track = music_track.fade_in(fade_ms).fade_out(fade_ms)
        music_ref, music_asset = generate_audio_ref(
            music_track,
            0,
            music_volume,
            asset_id_appendix="background_",
        )
        project.add_assets(music_asset)
        project.add_timeline_events(music_ref)

    for scene_index, (images, audio) in enumerate(
        zip(images_per_scene, audio_per_scene, strict=True),
    ):
        audio_length = len(audio) / 1000
        time_per_image = audio_length / len(images)
        image_refs = []

        for image_index, image in enumerate(images):
            ref, asset = generate_image_ref(
                image,
                scene_index,
                image_index,
                start_time,
                time_per_image,
            )
            image_refs.append(ref)
            project.add_assets(asset)

        audio_ref, audio_asset = generate_audio_ref(audio, start_time)
        project.add_assets(audio_asset)

        subtitle_refs = []
        for subtitle in subtitles:
            if start_time <= subtitle["start_time"] < start_time + audio_length:
                subtitle_ref, subtitle_asset = generate_subtitle_ref(subtitle)
                subtitle_refs.append(subtitle_ref)
                project.add_assets(subtitle_asset)

        scenes.append(Scene(asset_references=[*image_refs, audio_ref, *subtitle_refs]))
        start_time += audio_length

    for scene in scenes:
        project.add_timeline_events(scene)

    output = str(output_path)
    render_video(
        project,
        output,
        overwrite=True,
        codec=DEFAULT_CODEC,
        bitrate=DEFAULT_BITRATE,
        audio_codec=DEFAULT_AUDIO_CODEC,
        fps=DEFAULT_FPS,
        ffmpeg_params=["-preset", PRESET, "-crf", CRF, "-pix_fmt", PIX_FMT],
        temp_audiofile_path=TEMP_AUDIOFILE_PATH,
    )
    LOGGER.info("Final video created at: %s", output)
    return output
