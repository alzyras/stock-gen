import logging
from io import BytesIO

from mosaico.assets import create_asset
from mosaico.assets.audio import AudioAssetParams
from mosaico.assets.image import ImageAssetParams
from mosaico.assets.reference import AssetReference
from mosaico.effects.pan import PanLeftEffect, PanRightEffect
from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig
from mosaico.video.rendering import render_video
from PIL import Image
from pydub import AudioSegment

LOGGER = logging.getLogger(__name__)



def pil_image_to_bytes(image: Image.Image) -> bytes:
    """Convert a PIL Image object to bytes.

    Args:
        image: A PIL Image object.

    Returns:
        The image data as bytes.
    """
    with BytesIO() as output:
        image.save(output, format="JPEG")
        return output.getvalue()

def audio_segment_to_bytes(audio: AudioSegment) -> bytes:
    """Convert an AudioSegment object to bytes in a specific format.

    Args:
        audio: The AudioSegment object.
        format: The desired audio format (default is 'mp3').

    Returns:
        Bytes representing the audio file.
    """
    with BytesIO() as output:
        audio.export(output)
        return output.getvalue()


def generate_video_from_objects(
    video_title: str,
    images_per_scene: list[list[Image.Image]],
    audio_per_scene: list[AudioSegment],
    output_path: str,
) -> str:
    """Generate a video using image objects from PIL and audio objects from pydub.

    Args:
        images_per_scene: A list of lists, where each inner list contains Image objects for a scene.
        audio_per_scene: A list of AudioSegment objects representing the audio per scene.
        output_path: Path where the final video will be saved.

    Returns:
        The path to the final video file.
    """  # noqa: E501
    project = VideoProject(config=VideoProjectConfig())
    scenes = []
    start_time = 0

    for scene_index, (images, audio) in enumerate(
        zip(images_per_scene, audio_per_scene, strict=True)
    ):

        audio_length = len(audio) / 1000  # Convert milliseconds to seconds
        num_images = len(images)
        time_per_image = audio_length / num_images
        image_refs = []

        for i, image in enumerate(images):
            asset_id = f"scene{scene_index}_img{i}"
            image_data = pil_image_to_bytes(image)
            asset = create_asset("image", data=image_data, id=asset_id)

            effect = ZoomInEffect() if i % 2 == 0 else ZoomOutEffect()
            pan_effect = PanLeftEffect() if i % 2 == 0 else PanRightEffect()

            image_start = start_time + (i * time_per_image)
            image_end = start_time + ((i + 1) * time_per_image)

            ref = (
                AssetReference.from_asset(asset)
                .with_start_time(image_start)
                .with_end_time(image_end)
                .with_effects(effects=[effect, pan_effect])
                .with_params(params=ImageAssetParams(z_index=0, as_background=True))
            )
            image_refs.append(ref)
            project.add_assets(asset)
        audio_data = audio_segment_to_bytes(audio)
        audio_asset = create_asset("audio", data=audio_data, id=f"audio_{start_time}")
        audio_ref = (
            AssetReference.from_asset(audio_asset)
            .with_start_time(start_time)
            .with_end_time(start_time + audio_length)
        ).with_params(params=AudioAssetParams(volume=1))

        project.add_assets(audio_asset)
        scene = Scene(asset_references=[*image_refs, audio_ref])
        scenes.append(scene)
        start_time += audio_length

    for scene in scenes:
        project.add_timeline_events(scene)

    render_video(project, output_path)
    LOGGER.info(f"Final video created at: {output_path}")

    return output_path



# Example: Load images and audio
scene1_images = [Image.open("image1.jpg"), Image.open("image2.jpg")]
scene2_images = [Image.open("image3.jpg"), Image.open("image4.jpg")]
scene1_audio = AudioSegment.from_file("audio1.mp3")
scene2_audio = AudioSegment.from_file("audio2.mp3")

# Call the function
generate_video_from_objects(
    images_per_scene=[scene1_images, scene2_images],
    audio_per_scene=[scene1_audio, scene2_audio],
    output_path="",
)
