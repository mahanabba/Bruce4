## Pump.fun Chaos Gremlin (Raspberry Pi + local LLM + TTS + Motion)

Chaotic, non-toxic reply bot for Pump.fun comments. Runs a tiny local LLM via Ollama, speaks replies out loud, and wiggles a servo / blinks an LED while talking.

### Features
- Tiny local LLM (e.g., `qwen2.5:0.5b-instruct` or `tinyllama`) through Ollama
- Persona prompt: "TREVV THE TRENCHER" — polarizing, witty, self-grandiose (PG-13)
- TTS: `espeak-ng` on Pi/Linux, `say` on macOS (default voice: grumpy old man)
- Motion: Raspberry Pi GPIO servo + LED animation while speaking

### Hardware (optional but fun)
- Servo (e.g., SG90) on `SERVO_PIN` (default BCM 18, PWM)
- LED + resistor on `LED_PIN` (default BCM 17)

### Raspberry Pi Setup
1) Install Ollama and a tiny model
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull qwen2.5:0.5b-instruct || ollama pull tinyllama:latest
```

2) System packages for TTS and GPIO
```bash
sudo apt update
sudo apt install -y espeak-ng python3-pip python3-venv
```

3) Create venv and install deps
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-pi.txt
```

4) Wiring (BCM numbering)
- `SERVO_PIN` 18 → servo signal (5V, GND to power rails)
- `LED_PIN` 17 → series resistor → LED → GND

### macOS (dev) Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install espeak
ollama serve &
ollama pull qwen2.5:0.5b-instruct || ollama pull tinyllama:latest
```

### Usage
Run from repo root:
```bash
python -m pumpfun_bot "wen moon?"
```

Pipe from stdin:
```bash
echo "chart go brrr" | python -m pumpfun_bot
```

Disable voice or motion:
```bash
python -m pumpfun_bot "gm" --no-speak
```

Stream live Pump.fun replies (requires pumpfunpy):
```bash
python -m pumpfun_bot --stream
```

Experimental: watch a livestream page's chat (requires Playwright):
```bash
# First-time only (installs browser for Playwright)
python -m playwright install chromium

# Then run chat watcher
python -m pumpfun_bot --chat-url "https://pump.fun/live/<some-stream>"
```
Notes: chat scraping is best-effort and may break if Pump.fun changes markup.

### Env Vars (tweak behavior)
- `OLLAMA_HOST` default `http://127.0.0.1:11434`
- `OLLAMA_MODEL` default `qwen2.5:0.5b-instruct` (fallback `tinyllama:latest`)
- `LLM_TEMPERATURE` default `0.95`
- `MAX_TOKENS` default `192`
- `TOP_P` default `0.95`, `TOP_K` default `50`
- `SPICE_MAX` set `1` to intensify tone and sampling (hotter, punchier)
- `TTS_ENGINE`: `say`|`espeak-ng` (auto-detect)
- `ESPEAK_VOICE` default `en-us+m3` (lower, gruffer) | macOS voice via `SAY_VOICE` (default `Ralph`) and `SAY_RATE`
- `SERVO_PIN` default `18`, `LED_PIN` default `17`
- `SERVO_FREQ` default `50`, `SERVO_MIN_ANGLE` `35`, `SERVO_MAX_ANGLE` `145`
- `SERVO_MIN_DUTY` `2.5`, `SERVO_MAX_DUTY` `12.5`
- `SENTENCE_CHARS_PER_CHUNK` default `180`
- `R_RATED` set `1` to allow tasteful profanity (still no slurs/sexual content)
- `CENSOR_TTS` set `1` to mask casual profanity when speaking (mask via `PROFANITY_MASK_CHAR`)

### Notes
- Keep Ollama running: `ollama serve`
- Very small models respond fast on Pi, but stay concise (<40 words).
- Motion controller is best-effort; if GPIO isn’t present, it silently no-ops.

### License
MIT


