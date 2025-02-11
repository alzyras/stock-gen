from uuid import uuid4

from PIL.Image import Image
from pydantic import BaseModel

from prompt_to_video.settings import IMAGE_STORE


class ImageData(BaseModel):
    prompt: str
    image: Image
    identifier: str = str(uuid4())
    path_pattern: str | None = "{image_store}/{identifier}.png"

    def save_image(self) -> None:
        """Save the image to the specified path."""
        path = self.path_pattern.format(
            image_store=IMAGE_STORE, identifier=self.identifier
        )
        self.image.save(path)
