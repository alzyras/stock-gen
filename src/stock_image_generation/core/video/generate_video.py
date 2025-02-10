import os
import logging
from collections import defaultdict
from pydub.utils import mediainfo
from mosaico.assets import create_asset
from mosaico.assets.image import ImageAssetParams
from mosaico.assets.reference import AssetReference
from mosaico.effects.pan import PanLeftEffect, PanRightEffect
from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect
from mosaico.assets.audio import AudioAssetParams
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig
from mosaico.video.rendering import render_video

LOGGER = logging.getLogger(__name__)


class VideoGenerator:
    def __init__(self, project_folder):
        self.project_folder = project_folder
        self.project = VideoProject(config=VideoProjectConfig())
        self.scenes = []
        self.start_time = 0

    def get_audio_length(self, audio_path):
        """Get the length of an audio file in seconds."""
        info = mediainfo(audio_path)
        return float(info["duration"])

    def process_scene(self, scene_folder):
        """Process a single scene: match images and audio, then create scene objects."""
        audio_path = os.path.join(scene_folder, "audio.mp3")
        if not os.path.exists(audio_path):
            LOGGER.info(f"Audio file not found in {scene_folder}. Skipping...")
            return
        
        audio_length = self.get_audio_length(audio_path)
        image_files = sorted(
            [f for f in os.listdir(scene_folder) if f.endswith((".png", ".jpg"))],
            key=lambda x: tuple(map(int, os.path.splitext(x)[0].split("_")))
        )
        
        if not image_files:
            LOGGER.info(f"No images found in {scene_folder}. Skipping...")
            return
        
        num_images = len(image_files)
        time_per_image = audio_length / num_images
        image_refs = []
        
        for i, image_file in enumerate(image_files):
            image_path = os.path.join(scene_folder, image_file)
            asset_id = os.path.splitext(image_file)[0]
            
            try:
                asset = create_asset("image", path=image_path, id=f"{scene_folder}_{asset_id}")
            except Exception as e:
                LOGGER.exception(f"Error creating asset for {image_path}: {e}")
                continue
            
            effect = ZoomInEffect() if i % 2 == 0 else ZoomOutEffect()
            pan_effect = PanLeftEffect() if i % 2 == 0 else PanRightEffect()
            
            image_start = self.start_time + (i * time_per_image)
            image_end = self.start_time + ((i + 1) * time_per_image)
            
            ref = (
                AssetReference.from_asset(asset)
                .with_start_time(image_start)
                .with_end_time(image_end)
                .with_effects(effects=[effect, pan_effect])
                .with_params(params=ImageAssetParams(z_index=0, as_background=True))
            )
            image_refs.append(ref)
            self.project.add_assets(asset)
        
        audio_asset = create_asset("audio", path=audio_path, id=f"audio_{self.start_time}")
        audio_ref = AssetReference.from_asset(audio_asset).with_start_time(self.start_time).with_end_time(self.start_time + audio_length)
        audio_ref = audio_ref.with_params(params=AudioAssetParams(volume=1))
        
        self.project.add_assets(audio_asset)
        scene = Scene(asset_references=image_refs + [audio_ref])
        self.scenes.append(scene)
        self.start_time += audio_length

    def generate_video(self):
        """Iterate through scene folders and build the final video project."""
        scene_folders = sorted(
            [f for f in os.listdir(self.project_folder) if f.isdigit()], key=lambda x: int(x)
        )
        
        for scene_name in scene_folders:
            scene_path = os.path.join(self.project_folder, scene_name)
            if os.path.isdir(scene_path):
                self.process_scene(scene_path)
        
        for scene in self.scenes:
            self.project.add_timeline_events(scene)

        output_path = os.path.join(self.project_folder, "final_video.mp4")
        render_video(self.project, self.project_folder)
        LOGGER.info(f"Final video created at: {output_path}")
        return output_path


if __name__ == "__main__":
    folder = "store/projects/historic_facts/top_5_foods_medieval_england/"
    generator = VideoGenerator(folder)
    generator.generate_video()
