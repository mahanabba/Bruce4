import platform
import shlex
import shutil
import subprocess
from typing import Iterable

from .config import Settings, default_tts_engine


def _chunk_text(text: str, max_len: int) -> Iterable[str]:
	text = text.strip()
	if not text:
		return []
	if len(text) <= max_len:
		yield text
		return

	# Try to chunk by sentence terminators first
	separators = [". ", "! ", "? ", "; ", ", "]
	remaining = text
	while remaining:
		if len(remaining) <= max_len:
			yield remaining
			break
		# Find the last separator under the limit
		cut = -1
		for sep in separators:
			idx = remaining.rfind(sep, 0, max_len)
			if idx > cut:
				cut = idx + len(sep)
		if cut <= 0:
			# Hard cut
			cut = max_len
		chunk, remaining = remaining[:cut].strip(), remaining[cut:].strip()
		if chunk:
			yield chunk


def speak(text: str) -> None:
	"""Speak text using espeak-ng on Linux/Pi or say on macOS.

	Splits long text into chunks for better latency and stability.
	"""
	engine = Settings.TTS_ENGINE or default_tts_engine()
	if Settings.CENSOR_TTS:
		text = _mask_profanity(text, Settings.PROFANITY_MASK_CHAR)
	if engine == "say":
		_returncode = _speak_macos(text)
		return
	# default to espeak-ng
	_speak_espeak(text)


def _speak_espeak(text: str) -> None:
	cmd_base = [
		"espeak-ng",
		"-v",
		Settings.ESPEAK_VOICE,
		"-s",
		str(Settings.ESPEAK_RATE),
		"-p",
		str(Settings.ESPEAK_PITCH),
		"-a",
		str(Settings.ESPEAK_VOLUME),
	]
	if not shutil.which("espeak-ng"):
		# Try espeak as a fallback
		cmd_base[0] = "espeak"
		if not shutil.which("espeak"):
			return

	for chunk in _chunk_text(text, Settings.SENTENCE_CHARS_PER_CHUNK):
		subprocess.run(cmd_base + [chunk], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _speak_macos(text: str) -> int:
	voice = ["-v", Settings.SAY_VOICE] if Settings.SAY_VOICE else []
	rate = ["-r", str(Settings.SAY_RATE)] if Settings.SAY_RATE else []
	return subprocess.run([
		"say",
		*voice,
		*rate,
		text,
	], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode


def _mask_profanity(text: str, mask: str) -> str:
	"""Very lightweight profanity masking. Intentional minimal list.

	This avoids slurs/sexual content; target casual profanity only.
	"""
	bad = {
		"fuck": "f{m}{m}k",
		"shit": "s{m}{m}t",
		"bitch": "b{m}{m}ch",
		"asshole": "a{m}{m}hole",
	}
	out = text
	for k, v in bad.items():
		out = out.replace(k, v.replace("{m}", mask))
		out = out.replace(k.capitalize(), v.replace("{m}", mask).capitalize())
	return out


