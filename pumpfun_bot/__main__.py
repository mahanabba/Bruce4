import argparse
import asyncio
import sys

from .llm_client import generate_reply
from .tts import speak
from .motion import MotionController
from .chat_stream import stream_chat


async def _run_stream(no_speak: bool) -> int:
	try:
		from pumpfunpy import api  # type: ignore
	except Exception as e:
		print("Streaming requires 'pumpfunpy'. Install it first: pip install pumpfunpy")
		return 1

	print("[stream] Listening for new Pump.fun replies...")
	async for item in api.stream_new_replies():
		comment_text = (item.get("content") or item.get("comment") or "").strip()
		if not comment_text:
			continue
		reply = generate_reply(comment_text)
		print(f"[in]  {comment_text}")
		print(f"[out] {reply}")
		mover = MotionController()
		try:
			if not no_speak:
				mover.start()
				speak(reply)
		finally:
			mover.stop()
	return 0


async def _run_chat(url: str, no_speak: bool) -> int:
	print(f"[chat] Watching livestream chat: {url}")
	try:
		async for incoming in stream_chat(url):
			comment_text = incoming.strip()
			if not comment_text:
				continue
			reply = generate_reply(comment_text)
			print(f"[chat in]  {comment_text}")
			print(f"[chat out] {reply}")
			mover = MotionController()
			try:
				if not no_speak:
					mover.start()
					speak(reply)
			finally:
				mover.stop()
	except RuntimeError as e:
		print(str(e))
		return 1
	return 0


def main() -> int:
	parser = argparse.ArgumentParser(description="Chaotic Pump.fun reply bot (local LLM + TTS)")
	parser.add_argument("comment", nargs="?", help="Single Pump.fun comment text. If omitted, reads stdin.")
	parser.add_argument("--no-speak", dest="no_speak", action="store_true", help="Do not speak the reply, just print")
	parser.add_argument("--stream", dest="stream", action="store_true", help="Stream live Pump.fun replies (requires pumpfunpy)")
	parser.add_argument("--chat-url", dest="chat_url", help="Livestream page URL to scrape chat (requires Playwright)")
	args = parser.parse_args()

	if args.stream:
		return asyncio.run(_run_stream(args.no_speak))
	if args.chat_url:
		return asyncio.run(_run_chat(args.chat_url, args.no_speak))

	if args.comment:
		comment_text = args.comment
	else:
		comment_text = sys.stdin.read().strip()
		if not comment_text:
			print("No input provided.")
			return 1

	reply = generate_reply(comment_text)
	print(reply)

	# Move while speaking (best-effort)
	mover = MotionController()
	try:
		if not args.no_speak:
			mover.start()
			speak(reply)
	finally:
		mover.stop()
	return 0


if __name__ == "__main__":
	sys.exit(main())


