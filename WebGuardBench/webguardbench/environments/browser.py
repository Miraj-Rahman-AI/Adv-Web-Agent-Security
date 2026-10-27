"""Playwright backend, restricted to an ephemeral loopback-only fixture server."""

import json
import os
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from threading import Thread
from urllib.parse import urlsplit

from ..scenarios.schema import Action, Scenario
from .synthetic import Outcome, SyntheticState


class LocalSite:
    def __init__(self, kind: str):
        self.state = SyntheticState(kind)
        site = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def reply(self, code, content, content_type="application/json"):
                self.send_response(code)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "no-store")
                self.send_header(
                    "Content-Security-Policy",
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline'; "
                    "style-src 'self' 'unsafe-inline'; frame-src 'none'",
                )
                self.end_headers()
                self.wfile.write(content)

            def do_GET(self):
                if self.path == "/":
                    self.reply(
                        200,
                        files("webguardbench.environments").joinpath("site.html").read_bytes(),
                        "text/html; charset=utf-8",
                    )
                elif self.path == "/api/state":
                    self.reply(200, json.dumps(site.state.observe()).encode())
                else:
                    self.reply(404, b'{"error":"not found"}')

            def do_POST(self):
                if self.path != "/api/action":
                    self.reply(404, b'{"error":"not found"}')
                    return
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    if not 0 < size <= 4096:
                        raise ValueError("Invalid request size")
                    action = Action.from_dict(json.loads(self.rfile.read(size)))
                    outcome = site.state.execute(action)
                    self.reply(200, json.dumps(asdict(outcome)).encode())
                except (ValueError, TypeError):
                    self.reply(400, b'{"error":"invalid action"}')

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.url = f"http://127.0.0.1:{self.server.server_port}/"

    def start(self):
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


class BrowserEnvironment:
    def __init__(self):
        self.site = self.playwright = self.browser = self.context = None

    async def start(self, scenario: Scenario) -> None:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Install '.[browser]' and run 'playwright install chromium'"
            ) from exc
        self.site = LocalSite(scenario.environment)
        self.site.start()
        self.url = self.site.url
        self.playwright = await async_playwright().start()
        channel = os.environ.get("WGB_BROWSER_CHANNEL") or None
        if channel not in {None, "chrome", "msedge", "chromium"}:
            raise ValueError("WGB_BROWSER_CHANNEL must be chrome, msedge, or chromium")
        self.browser = await self.playwright.chromium.launch(headless=True, channel=channel)
        self.metadata = {
            "name": "synthetic",
            "version": "1",
            "backend": "browser",
            "browser": "chromium",
            "browser_version": self.browser.version,
            "channel": channel or "bundled",
        }
        self.context = await self.browser.new_context(
            service_workers="block", accept_downloads=False
        )
        origin = urlsplit(self.url)

        async def restrict(route):
            request = urlsplit(route.request.url)
            if (request.scheme, request.netloc) == (origin.scheme, origin.netloc):
                await route.continue_()
            else:
                await route.abort()

        await self.context.route("**/*", restrict)
        self.page = await self.context.new_page()
        self.page.set_default_timeout(5000)
        await self.page.goto(self.url)
        await self.page.locator("#actions button").first.wait_for()

    async def observe(self) -> dict:
        return json.loads(await self.page.locator("#state").inner_text())

    async def execute(self, action: Action) -> Outcome:
        # The adapter receives observations only; it cannot execute arbitrary JS or URLs.
        try:
            index = self.site.state.actions.index(action)
        except ValueError as exc:
            raise ValueError("Action is outside the controlled browser environment") from exc
        previous = await self.page.locator("body").get_attribute("data-sequence") or "0"
        await self.page.get_by_test_id(f"action-{index}").click()
        await self.page.wait_for_function(
            "previous => document.body.dataset.sequence !== previous && "
            "document.body.dataset.sequence !== undefined",
            arg=previous,
        )
        # Evidence comes from the fixture server, not from an agent's textual claims.
        return self.site.state.last_outcome

    async def close(self) -> None:
        try:
            if self.context:
                await self.context.close()
        finally:
            try:
                if self.browser:
                    await self.browser.close()
            finally:
                try:
                    if self.playwright:
                        await self.playwright.stop()
                finally:
                    if self.site:
                        self.site.close()
