# prompt_to_video

Python pipeline for turning a video idea into structured script data, image prompts, generated images, narration audio, subtitles, and a rendered video.

## What It Does

- Generates structured video scripts with OpenAI structured outputs.
- Converts script scenes into standalone image prompts.
- Generates images with Hugging Face Diffusers/Flux.
- Generates narration with Edge TTS.
- Optionally calls a local transcription API to create SRT subtitles.
- Renders image/audio/subtitle timelines with Mosaico and FFmpeg.
- Provides a small Streamlit app for interactive image generation.

## Setup

```bash
cp .env.tmpl .env
make env
```

This installs `uv`, syncs the development environment, and installs pre-commit hooks. Edit `.env` with your model/API settings. The most important values are:

```bash
OPENAI_API_KEY="..."
LLM_MODEL="gpt-4o"
IMAGE_MODEL="black-forest-labs/FLUX.1-schnell"
HF_HOME="./hf_cache"
USE_MPS=0
DATA_FOLDER="./data/output.mp4"
```

For Real-ESRGAN upscaling, download the NCNN Vulkan binary and model files into the paths configured by `REALESRGAN_BINARY` and `REALESRGAN_MODEL_PATH`.

## Common Commands

```bash
make lint      # Ruff lint checks
make format    # Ruff format and autofix
make test      # Pytest test suite
make check     # Compile, lint, and test
```

Run the Streamlit app:

```bash
uv run streamlit run src/prompt_to_video/app.py
```

## Project Layout

```text
src/prompt_to_video/
  app.py                         # Streamlit image UI
  settings.py                    # Environment-backed settings with safe defaults
  core/audio/tts.py              # Edge TTS and transcription adapter
  core/image/image_generator.py  # Flux image generation and metadata wrapper
  core/image/upscaling/          # Diffusion and Real-ESRGAN upscalers
  core/prompt/                   # Structured script and prompt generation
  core/video/generate_video.py   # Timeline/rendering helpers
tests/                           # Lightweight unit tests
```

## Development Notes

- Generated media, databases, model caches, zips, and local notebooks should stay out of git.
- The test suite intentionally avoids loading ML models or rendering video; those paths should be integration-tested manually or with mocked adapters.
- `uv.lock` should be committed for reproducible application installs.
