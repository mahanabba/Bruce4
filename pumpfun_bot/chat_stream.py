import asyncio
from typing import AsyncIterator


async def stream_chat(url: str) -> AsyncIterator[str]:
	"""Yield chat text strings from a Pump.fun livestream page.

	This uses Playwright in headless mode to watch for appended chat message nodes.
	Selectors are best-effort and may need adjustment if Pump.fun changes markup.
	"""
	try:
		from playwright.async_api import async_playwright  # type: ignore
	except Exception as e:
		raise RuntimeError("Playwright not installed. pip install playwright && playwright install chromium") from e

	async with async_playwright() as pw:
		browser = await pw.chromium.launch(headless=True)
		context = await browser.new_context()
		page = await context.new_page()
		await page.goto(url, wait_until="domcontentloaded")

		# Heuristic selector candidates for chat container/messages
		container_candidates = [
			"div[role='feed']",
			"[data-testid='chat']",
			".chat, .chat-container, .live-chat",
		]

		container = None
		for sel in container_candidates:
			try:
				el = await page.query_selector(sel)
				if el:
					container = el
					break
			except Exception:
				pass

		if container is None:
			# Fall back to body observer for appended nodes
			container = await page.query_selector("body")

		# Expose a callback to push messages to an async queue
		queue: asyncio.Queue[str] = asyncio.Queue()

		await page.expose_function("__push_msg", lambda txt: queue.put_nowait(str(txt)))

		# Inject MutationObserver in the page to watch for message nodes
		await page.evaluate(
			"""
		(() => {
		  const push = (t) => window.__push_msg && window.__push_msg(t);
		  const container = document.querySelector("div[role='feed']")
		    || document.querySelector("[data-testid='chat']")
		    || document.querySelector('.chat, .chat-container, .live-chat')
		    || document.body;
		  const isMessage = (node) => {
		    if (!node) return false;
		    const el = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
		    if (!el) return false;
		    const txt = el.innerText || '';
		    return txt.trim().length > 0 && el.querySelectorAll('button,input,video').length === 0;
		  };
		  const observer = new MutationObserver((muts) => {
		    for (const m of muts) {
		      for (const n of m.addedNodes) {
		        if (isMessage(n)) {
		          const el = n.nodeType === Node.ELEMENT_NODE ? n : n.parentElement;
		          const txt = el ? (el.innerText || '').trim() : '';
		          if (txt) push(txt);
		        }
		      }
		    }
		  });
		  observer.observe(container, { childList: true, subtree: true });
		})();
		"""
		)

		try:
			while True:
				msg = await queue.get()
				yield msg
		finally:
			await context.close()
			await browser.close()


