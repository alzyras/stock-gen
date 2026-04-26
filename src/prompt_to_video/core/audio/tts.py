import logging
from io import BytesIO
from pathlib import Path

import edge_tts
import requests
from pydub import AudioSegment

from prompt_to_video.settings import REQUEST_TIMEOUT_SECONDS, TRANSCRIBER_URL

LOGGER = logging.getLogger(__name__)


class TranscriptionError(RuntimeError):
    """Raised when the local transcription service fails."""


def generate_audio(text: str, voice: str = "en-US-JennyNeural") -> AudioSegment:
    """Generate speech audio and return it as a pydub segment."""
    communicate = edge_tts.Communicate(text, voice)
    audio_data = BytesIO()

    for chunk in communicate.stream_sync():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])

    audio_data.seek(0)
    return AudioSegment.from_file(audio_data, format="mp3")


def transcribe_audio(
    audio_segment: AudioSegment,
    words_per_sentence: int = 5,
    transcriber_url: str = TRANSCRIBER_URL,
) -> str:
    """Send audio to the configured transcription API and return SRT content."""
    audio_bytes = BytesIO()
    audio_segment.export(audio_bytes, format="mp3")
    audio_bytes.seek(0)

    response = requests.post(
        transcriber_url,
        files={"file": ("audio.mp3", audio_bytes, "audio/mpeg")},
        data={"words_per_sentence": str(words_per_sentence)},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if response.status_code != requests.codes.ok:
        msg = f"Transcription failed with HTTP {response.status_code}: {response.text}"
        raise TranscriptionError(msg)
    return response.text


def send_audiosegment_to_transcriber(
    audio_segment: AudioSegment,
    words_per_sentence: int = 5,
    output_path: str | Path = "output.srt",
) -> str:
    """Transcribe audio, write the SRT file, and return the SRT text."""
    srt_content = transcribe_audio(audio_segment, words_per_sentence)
    Path(output_path).write_text(srt_content, encoding="utf-8")
    LOGGER.info("Transcription saved to %s", output_path)
    return srt_content


class EdgeTTS:
    """Small adapter used by the asset pipeline."""

    def generate_audio(
        self,
        text: str,
        voice: str,
        output_file: str | Path,
        srt_file: str | Path | None = None,
        words_per_sentence: int = 5,
    ) -> AudioSegment:
        """Generate audio and optionally write subtitles via the transcriber API."""
        audio = generate_audio(text, voice)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        audio.export(output_path, format="mp3")
        LOGGER.info("Audio saved to %s", output_path)

        if srt_file is not None:
            try:
                send_audiosegment_to_transcriber(audio, words_per_sentence, srt_file)
            except requests.RequestException:
                LOGGER.exception("Could not reach transcription service")
            except TranscriptionError:
                LOGGER.exception("Transcription service returned an error")

        return audio
