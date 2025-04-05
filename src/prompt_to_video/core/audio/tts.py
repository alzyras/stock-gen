import logging
from io import BytesIO

import edge_tts
from pydub import AudioSegment

LOGGER = logging.getLogger(__name__)


def generate_audio(text: str, voice: str) -> AudioSegment:
    """Generate audio and return a pydub AudioSegment object."""
    communicate = edge_tts.Communicate(text, voice)
    audio_data = BytesIO()

    for chunk in communicate.stream_sync():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])

    audio_data.seek(0)
    return AudioSegment.from_file(audio_data, format="mp3")
