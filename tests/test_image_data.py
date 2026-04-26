from PIL import Image

from prompt_to_video.core.image import ImageData


def test_image_data_saves_image_and_metadata(tmp_path) -> None:
    image = Image.new("RGB", (4, 4), color="red")
    image_data = ImageData(
        image=image, prompt="Ancient city at sunrise", path=str(tmp_path)
    )

    saved_path = image_data.save_image()

    assert saved_path.exists()
    assert saved_path.parent == tmp_path
    assert "ancient-city-at-sunrise" in saved_path.name
    assert image_data.get_categories()[:3] == ["ancient", "city", "sunrise"]
    assert "Ancient city at sunrise" in image_data.model_dump_json(exclude={"image"})
