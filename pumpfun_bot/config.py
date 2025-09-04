import os
import platform


class Settings:
	"""Runtime configuration with sensible defaults for Raspberry Pi and macOS."""

	# Ollama server location (must be running locally unless you point to a remote host)
	OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

	# Prefer a very small instruct model; fall back to tinyllama if unavailable
	OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b-instruct")
	FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "tinyllama:latest")

	# Generation settings
	LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.95"))
	MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "192"))
	TOP_P: float = float(os.getenv("TOP_P", "0.95"))
	TOP_K: int = int(os.getenv("TOP_K", "50"))

	# Spice mode
	SPICE_MAX: bool = os.getenv("SPICE_MAX", "0") not in ("0", "false", "False")

	# TTS settings
	TTS_ENGINE: str = os.getenv("TTS_ENGINE", "")  # autodetect if empty
	ESPEAK_VOICE: str = os.getenv("ESPEAK_VOICE", "en-us+m3")
	ESPEAK_RATE: int = int(os.getenv("ESPEAK_RATE", "140"))  # words per minute
	ESPEAK_PITCH: int = int(os.getenv("ESPEAK_PITCH", "30"))  # 0-99
	ESPEAK_VOLUME: int = int(os.getenv("ESPEAK_VOLUME", "150"))  # 0-200 (amplitude)
	SAY_VOICE: str = os.getenv("SAY_VOICE", "Ralph")  # macOS voice
	SAY_RATE: int = int(os.getenv("SAY_RATE", "140"))  # macOS say WPM

	# Speaking behavior
	SENTENCE_CHARS_PER_CHUNK: int = int(os.getenv("SENTENCE_CHARS_PER_CHUNK", "180"))

	# Content style toggles
	R_RATED: bool = os.getenv("R_RATED", "0") not in ("0", "false", "False")
	CENSOR_TTS: bool = os.getenv("CENSOR_TTS", "0") not in ("0", "false", "False")
	PROFANITY_MASK_CHAR: str = os.getenv("PROFANITY_MASK_CHAR", "*")

	# Motion defaults (Pi)
	ENABLE_MOTION: bool = os.getenv("ENABLE_MOTION", "1") not in ("0", "false", "False")
	LED_PIN: int = int(os.getenv("LED_PIN", "17"))
	SERVO_PIN: int = int(os.getenv("SERVO_PIN", "18"))
	SERVO_FREQ: int = int(os.getenv("SERVO_FREQ", "50"))
	SERVO_MIN_ANGLE: int = int(os.getenv("SERVO_MIN_ANGLE", "35"))
	SERVO_MAX_ANGLE: int = int(os.getenv("SERVO_MAX_ANGLE", "145"))
	SERVO_MIN_DUTY: float = float(os.getenv("SERVO_MIN_DUTY", "2.5"))
	SERVO_MAX_DUTY: float = float(os.getenv("SERVO_MAX_DUTY", "12.5"))


def default_tts_engine() -> str:
	"""Select a platform-appropriate default TTS engine."""
	os_name = platform.system().lower()
	if os_name == "darwin":
		return "say"
	return "espeak-ng"  # Linux / Raspberry Pi

