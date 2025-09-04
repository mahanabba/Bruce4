from typing import Optional

from .config import Settings
from .prompt import build_system_prompt, format_user_message


def generate_reply(
	comment_text: str,
	model: Optional[str] = None,
	temperature: Optional[float] = None,
	max_tokens: Optional[int] = None,
) -> str:
	"""Generate a reply using a local Ollama model with the chaotic persona.

	If the primary model fails, we attempt a fallback model. If everything
	fails (e.g., server not running), we return a safe, short default message.
	"""
	try:
		# Import inside function to keep module import cheap if not used.
		import ollama  # type: ignore
	except Exception:
		return _default_fallback_reply()

	selected_model = model or Settings.OLLAMA_MODEL
	# Intensify sampling if SPICE_MAX
	base_temp = Settings.LLM_TEMPERATURE if temperature is None else temperature
	selected_temperature = min(1.5, (base_temp or 0.95) * (1.25 if Settings.SPICE_MAX else 1.0))
	selected_max_tokens = Settings.MAX_TOKENS if max_tokens is None else max_tokens

	messages = [
		{"role": "system", "content": build_system_prompt()},
		{"role": "user", "content": format_user_message(comment_text)},
	]

	options = {
		"temperature": selected_temperature,
		"top_p": 0.98 if Settings.SPICE_MAX else Settings.TOP_P,
		"top_k": 100 if Settings.SPICE_MAX else Settings.TOP_K,
		"repeat_penalty": 1.08 if Settings.SPICE_MAX else 1.05,
		"num_predict": selected_max_tokens,
	}

	try:
		client = ollama.Client(host=Settings.OLLAMA_HOST)
		resp = client.chat(model=selected_model, messages=messages, options=options)
		content = (resp or {}).get("message", {}).get("content", "").strip()
		if content:
			return content
		# Fall through to fallback if empty
	except Exception:
		pass

	# Fallback attempt
	try:
		resp = client.chat(model=Settings.FALLBACK_MODEL, messages=messages, options=options)  # type: ignore[name-defined]
		content = (resp or {}).get("message", {}).get("content", "").strip()
		if content:
			return content
	except Exception:
		pass

	return _default_fallback_reply()


def _default_fallback_reply() -> str:
	"""Return a safe, short default reply if no model is available."""
	return "BZZT—BRAIN JUICE LOW—BUT WE'RE STILL MOON-WALKING. 🚀🤪"

