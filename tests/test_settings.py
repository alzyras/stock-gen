import importlib


def test_settings_have_safe_defaults(monkeypatch) -> None:
    for key in (
        "LLM_MODEL",
        "OPENAI_MODEL",
        "IMAGE_MODEL",
        "USE_MPS",
        "UPSCALE_MODEL",
        "UPSCALER_TYPE",
        "DATA_FOLDER",
    ):
        monkeypatch.delenv(key, raising=False)

    from prompt_to_video import settings

    settings = importlib.reload(settings)

    assert settings.TEXT_GENERATION_MODEL == "gpt-4o"
    assert settings.IMAGE_GENERATION_MODEL == "black-forest-labs/FLUX.1-schnell"
    assert settings.USE_MPS is False
    assert settings.DATA_STORAGE_PATH == "./data/output.mp4"
