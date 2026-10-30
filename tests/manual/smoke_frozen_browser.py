"""Verify the packaged executable starts and closes using disposable data."""

import asyncio
import json
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen

import websockets


async def cdp(endpoint: str, method: str, params: dict | None = None):
    async with websockets.connect(endpoint) as connection:
        await connection.send(json.dumps({"id": 1, "method": method, "params": params or {}}))
        while True:
            message = json.loads(await asyncio.wait_for(connection.recv(), 5))
            if message.get("id") == 1:
                if "error" in message:
                    raise AssertionError(message["error"])
                return message.get("result", {})


def local_json(port: int, path: str):
    with urlopen(f"http://127.0.0.1:{port}/{path}", timeout=3) as response:
        return json.load(response)


async def smoke():
    executable = Path(__file__).resolve().parents[2] / "dist" / "Synthesix" / "Synthesix.exe"
    with TemporaryDirectory() as directory:
        process = subprocess.Popen([str(executable), "--data-dir", directory, "--headless"], close_fds=True)
        browser_endpoint = None
        try:
            for _ in range(100):
                assert process.poll() is None, "Packaged app exited before connecting"
                log = Path(directory) / "logs" / "browser.log"
                text = log.read_text(encoding="utf-8") if log.exists() else ""
                match = re.search(r"--remote-debugging-port=(\d+)", text)
                if match:
                    port = int(match.group(1))
                    try:
                        version = await asyncio.to_thread(local_json, port, "json/version")
                        browser_endpoint = version["webSocketDebuggerUrl"]
                        pages = await asyncio.to_thread(local_json, port, "json/list")
                        page = next((p for p in pages if p["url"].endswith("/index.html")), None)
                        if page:
                            result = await cdp(page["webSocketDebuggerUrl"], "Runtime.evaluate", {"expression": "Boolean(document.querySelector('sx-browser-app')?.model.connected)", "returnByValue": True})
                            if result["result"].get("value"):
                                break
                    except (OSError, TimeoutError):
                        pass
                await asyncio.sleep(.2)
            else:
                raise AssertionError("Packaged home did not connect")
            assert (Path(directory) / "data" / "browser.sqlite").is_file()
            print("Packaged executable: local assets, Lit, CDP and independent data directory OK")
        finally:
            if browser_endpoint:
                try:
                    await cdp(browser_endpoint, "Browser.close")
                except (OSError, websockets.ConnectionClosed):
                    pass
            try:
                await asyncio.to_thread(process.wait, 20)
            except subprocess.TimeoutExpired:
                process.terminate()
                await asyncio.to_thread(process.wait, 5)
        assert process.returncode == 0, process.returncode
        print("Packaged executable: clean browser and application shutdown OK")


if __name__ == "__main__":
    asyncio.run(smoke())
