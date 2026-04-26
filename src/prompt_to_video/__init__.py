import logging

LOGGER = logging.getLogger(__name__)


def setup_logging() -> None:
    """Set up default logging configuration for CLI/notebook usage."""
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] - <%(name)s> - %(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler()],
    )


def load_environment_variables() -> str:
    """Load .env values when python-dotenv is installed."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return "python-dotenv is not installed; skipping .env loading."

    if load_dotenv():
        return "Loaded environment variables from .env file."
    return "No .env file found; skipping environment variable loading."


def initialize() -> None:
    """Initialize logging and optional .env loading."""
    setup_logging()
    env_message = load_environment_variables()
    if env_message.startswith("Loaded"):
        LOGGER.info(env_message)
    else:
        LOGGER.debug(env_message)


initialize()
