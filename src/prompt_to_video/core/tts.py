import logging
from pathlib import Path

import edge_tts

# Set up logging to capture the debug information
logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)


class EdgeTTS:
    def __init__(self) -> None:
        """Initializes the class instance."""

    def generate_audio(
        self,
        text: str,
        voice: str,
        output_file: str,
        srt_file: str | None = None,
    ) -> None:
        """Generate audio and optionally subtitles."""
        communicate = edge_tts.Communicate(text, voice)
        submaker = edge_tts.SubMaker()
        with Path(output_file).open("wb") as file:
            for chunk in communicate.stream_sync():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary" and srt_file:
                    submaker.feed(chunk)

        if srt_file:
            with Path(srt_file).open("w", encoding="utf-8") as file:
                file.write(submaker.get_srt())

    @staticmethod
    def list_voices() -> list[str]:
        """Retrieve a list of available voices from the edge_tts library.

        Returns:
            list[str]: A list of voice names available for text-to-speech.
        """
        voices = edge_tts.list_voices()
        return list(voices)


if __name__ == "__main__":
    tts = EdgeTTS()
    tts.generate_audio("Hello World!", "en-GB-SoniaNeural", "test.mp3", "test.srt")
