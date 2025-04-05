import logging
from io import BytesIO
import pysrt

from mosaico.assets import create_asset
from mosaico.assets.audio import AudioAssetParams
from mosaico.assets.image import ImageAssetParams
from mosaico.assets.reference import AssetReference
from mosaico.assets.text import TextAssetParams
from mosaico.effects.pan import PanLeftEffect, PanRightEffect
from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig
from mosaico.video.rendering import render_video
from mosaico.positioning.relative import RelativePosition
from PIL import Image
from PIL import ImageFont
from pydub import AudioSegment

from prompt_to_video.settings import DATA_STORAGE_PATH

LOGGER = logging.getLogger(__name__)

VIDEO_WIDTH = 1920
FONT_SIZE = 48
FONT_FAMILY = "Arial"
TEXT_COLOR = "yellow"
STROKE_WIDTH = 3
Z_INDEX_IMAGE = 0
Z_INDEX_SUBTITLE = 2
DEFAULT_VOLUME = 1
DEFAULT_CODEC = "libx264"
DEFAULT_BITRATE = "50M"
DEFAULT_AUDIO_CODEC = "aac"
DEFAULT_FPS = 60
TEMP_AUDIOFILE_PATH = "/tmp/"
PRESET = "slow"
CRF = "18"
PIX_FMT = "yuv420p"

# Helper Functions
def pil_image_to_bytes(image: Image.Image) -> bytes:
    """Convert a PIL Image object to bytes."""
    with BytesIO() as output:
        image.save(output, format="JPEG")
        return output.getvalue()

def audio_segment_to_bytes(audio: AudioSegment) -> bytes:
    """Convert an AudioSegment object to bytes."""
    with BytesIO() as output:
        audio.export(output)
        return output.getvalue()

def parse_srt(srt_string: str) -> list:
    """Parse the SRT string into a list of subtitles with start time, end time, and text."""
    subtitles = []
    try:
        srt = pysrt.from_string(srt_string)
        for sub in srt:
            start_time = sub.start.seconds + sub.start.minutes * 60 + sub.start.hours * 3600 + sub.start.milliseconds / 1000.0
            end_time = sub.end.seconds + sub.end.minutes * 60 + sub.end.hours * 3600 + sub.end.milliseconds / 1000.0
            text = sub.text
            subtitles.append({
                "start_time": start_time,
                "end_time": end_time,
                "text": text
            })
    except Exception as e:
        LOGGER.error(f"Error parsing SRT: {e}")
    return subtitles

def calculate_text_width(text: str) -> float:
    """Calculate the width of the text based on the font and font size."""
    font = ImageFont.truetype(FONT_FAMILY, FONT_SIZE)
    return font.getlength(text)

def generate_image_ref(image, scene_index, image_index, start_time, time_per_image):
    """Generate image reference for a scene."""
    asset_id = f"scene{scene_index}_img{image_index}"
    image_data = pil_image_to_bytes(image)
    asset = create_asset("image", data=image_data, id=asset_id)

    zoom_factor = 1.05
    effect = ZoomInEffect(start_zoom=1, end_zoom=1.2) if image_index % 2 == 0 else ZoomOutEffect(start_zoom=1.2, end_zoom=1)
    pan_effect = PanLeftEffect(zoom_factor=zoom_factor) if image_index % 2 == 0 else PanRightEffect(zoom_factor=zoom_factor)

    image_start = start_time + (image_index * time_per_image)
    image_end = start_time + ((image_index + 1) * time_per_image)

    ref = (
        AssetReference.from_asset(asset)
        .with_start_time(image_start)
        .with_end_time(image_end)
        .with_effects(effects=[pan_effect])
        .with_params(params=ImageAssetParams(z_index=Z_INDEX_IMAGE, as_background=True))
    )
    return ref, asset

def generate_audio_ref(audio, start_time, volume=DEFAULT_VOLUME, asset_id_appendix = ""):
    """Generate audio reference for a scene with specified volume."""
    audio_data = audio_segment_to_bytes(audio)
    audio_asset = create_asset("audio", data=audio_data, id=f"{asset_id_appendix}audio_{start_time}")
    audio_ref = (
        AssetReference.from_asset(audio_asset)
        .with_start_time(start_time)
        .with_end_time(start_time + len(audio) / 1000)  # Audio length in seconds
        .with_params(params=AudioAssetParams(volume=volume))  # Ensure volume is set
    )

    return audio_ref, audio_asset

def generate_subtitle_ref(subtitle, start_time, audio_length):
    """Generate subtitle reference for a scene."""
    text_width = calculate_text_width(subtitle["text"])
    x_position = (VIDEO_WIDTH - text_width) / 2 / VIDEO_WIDTH  # Normalize for video width

    subtitle_asset = create_asset(
        "text",
        data=subtitle["text"],
        id=f"subtitle_{subtitle['start_time']}",
        params=TextAssetParams(font_size=FONT_SIZE, font_family=FONT_FAMILY, z_index=Z_INDEX_SUBTITLE, font_color=TEXT_COLOR, stroke_width=STROKE_WIDTH, position=RelativePosition(x=x_position, y=0.90)),
    )

    subtitle_ref = (
        AssetReference.from_asset(subtitle_asset)
        .with_start_time(subtitle["start_time"])
        .with_end_time(subtitle["end_time"])
    )

    return subtitle_ref, subtitle_asset


def add_background_music(total_duration, music_track, music_volume=1.0):
    """Generate a looped background music track with no fade-in or fade-out effects, at full volume."""
    total_duration_ms = int(total_duration * 1000)  # Convert total duration to milliseconds       
    if len(music_track) < total_duration_ms:
        loops = (total_duration_ms // len(music_track)) + 1
        music = (music_track * loops)[:total_duration_ms]  # Repeat and trim
    else:
        music = music_track[:total_duration_ms]  # Trim if longer

    # Ensure music is at full volume
    music = music + (5 * (1 - music_volume))  # Adjust volume (lower means softer)

    return music



def generate_video_from_objects(
    video_title: str,
    images_per_scene: list[list[Image.Image]],
    audio_per_scene: list[AudioSegment],
    srt_content: str = None,
    output_path: str = DATA_STORAGE_PATH,
    background_music: AudioSegment = None,
    music_volume: float = 1,
    fade_duration: int = 1,
) -> str:
    """Generate a video using image objects, audio objects, and an optional SRT string, with background music."""
    project = VideoProject(config=VideoProjectConfig(title=video_title))
    scenes = []
    start_time = 0

    subtitles = parse_srt(srt_content) if srt_content else []
    total_audio_length = sum(len(audio) / 1000 for audio in audio_per_scene)
    time_per_scene = total_audio_length / len(audio_per_scene)

    # Generate background music if provided
    if background_music:
        LOGGER.info(f"Background music loaded: {background_music}")
        LOGGER.info(f"Background music length: {total_audio_length}")
        total_duration = sum(len(audio) / 1000 for audio in audio_per_scene)  # Total video duration
        music_track = add_background_music(total_duration, background_music, music_volume=0.25)  # Set volume to full

        # Create asset and reference for background music
        music_ref, music_asset = generate_audio_ref(music_track, 0, 0.25, asset_id_appendix="background_")  # Full volume
        LOGGER.info(f"Adding background music with reference: {music_ref}")
        project.add_assets(music_asset)
        project.add_timeline_events(music_ref)  # Attach background music to timeline
    
    for scene_index, (images, audio) in enumerate(zip(images_per_scene, audio_per_scene)):
        audio_length = len(audio) / 1000  # Audio length in seconds
        num_images = len(images)
        time_per_image = audio_length / num_images
        image_refs = []

        for i, image in enumerate(images):
            ref, asset = generate_image_ref(image, scene_index, i, start_time, time_per_image)
            image_refs.append(ref)
            project.add_assets(asset)

        audio_ref, audio_asset = generate_audio_ref(audio, start_time,2)
        project.add_assets(audio_asset)

        subtitle_refs = []
        if subtitles:
            scene_subtitles = [sub for sub in subtitles if start_time <= sub["start_time"] < start_time + audio_length]
            for subtitle in scene_subtitles:
                subtitle_ref, subtitle_asset = generate_subtitle_ref(subtitle, start_time, audio_length)
                subtitle_refs.append(subtitle_ref)
                project.add_assets(subtitle_asset)

        scene = Scene(asset_references=[*image_refs, audio_ref, *subtitle_refs])
        scenes.append(scene)
        start_time += time_per_scene


    for scene in scenes:
        project.add_timeline_events(scene)
    


    kwargs = {
        "codec": DEFAULT_CODEC,
        "bitrate": DEFAULT_BITRATE,
        "audio_codec": DEFAULT_AUDIO_CODEC,
        "fps": DEFAULT_FPS,
        "ffmpeg_params": [
            "-preset", PRESET,
            "-crf", CRF,
            "-pix_fmt", PIX_FMT,
        ],
        "temp_audiofile_path": TEMP_AUDIOFILE_PATH,
        
    }

    render_video(project, output_path, overwrite=True, **kwargs)
    LOGGER.info(f"Final video created at: {output_path}")
    return output_path
