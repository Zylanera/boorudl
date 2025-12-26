import os, time, threading
import requests
from bs4 import BeautifulSoup

from .utils import sanitize_filename, guess_extension_from_url, unique_path
from .booru_api import DanbooruAPI
from .parsers import extract_image_url

class Downloader:
    def __init__(self, emit, include_family: bool = False):
        self.emit = emit
        self.include_family = include_family
        self.stop_flag = threading.Event()
        self.api = DanbooruAPI()
        self.html = requests.Session()
        self.html.headers["User-Agent"] = "Mozilla/5.0"

    def stop(self):
        self.stop_flag.set()

    def set_include_family(self, val: bool):
        self.include_family = bool(val)

    def run(self, urls, out_dir):
        queue = []
        seen = set()

        def add_pid(pid: int):
            if pid not in seen:
                seen.add(pid)
                queue.append(pid)

        def add_url(url: str):
            queue.append(url)

        for url in urls:
            if self.stop_flag.is_set():
                break

            pid = self.api.match(url)
            if not pid:
                add_url(url)
                continue

            if not self.include_family:
                add_pid(pid)
                continue

            self.emit("log", f"Family-Modus aktiv → analysiere Post {pid}")
            try:
                data = self.api.get_post(pid)
            except Exception as e:
                self.emit("log", f"  ERROR API: {e}")
                add_pid(pid)
                continue

            parent_id = data.get("parent_id")
            root_parent = int(parent_id) if parent_id else int(pid)

            add_pid(root_parent)

            try:
                root_data = data if root_parent == pid else self.api.get_post(root_parent)
            except Exception as e:
                self.emit("log", f"  ERROR Root-Post: {e}")
                root_data = {}

            if root_data.get("has_children") is True:
                try:
                    children = self.api.get_children(root_parent)
                    for cid in children:
                        add_pid(int(cid))
                    self.emit("log", f"  Familie: parent={root_parent}, children={len(children)}")
                except Exception as e:
                    self.emit("log", f"  ERROR Children-Liste: {e}")
            else:
                self.emit("log", f"  Familie: parent={root_parent}, children=0")

        total = len(queue)
        done = 0

        for i, item in enumerate(queue, 1):
            if self.stop_flag.is_set():
                self.emit("log", "Abort durch Benutzer.")
                break

            if isinstance(item, int):
                self.emit("log", f"[{i}/{total}] Danbooru Post: {item}")
                try:
                    data = self.api.get_post(item)
                    img_url = self.api.image_url(data)
                    char = sanitize_filename(self.api.character_tag(data))
                except Exception as e:
                    self.emit("log", f"  ERROR API: {e}")
                    done += 1
                    self.emit("overall", done / total * 100)
                    continue
            else:
                url = item
                self.emit("log", f"[{i}/{total}] Öffne: {url}")
                try:
                    r = self.html.get(url, timeout=20)
                    r.raise_for_status()
                    soup = BeautifulSoup(r.text, "html.parser")
                    img_url = extract_image_url(url, soup)
                    char = "unknown"
                except Exception as e:
                    self.emit("log", f"  ERROR HTML: {e}")
                    done += 1
                    self.emit("overall", done / total * 100)
                    continue

            if not img_url:
                self.emit("log", "  ERROR: kein Bild gefunden")
                done += 1
                self.emit("overall", done / total * 100)
                continue

            path = unique_path(os.path.join(out_dir, f"{char}{guess_extension_from_url(img_url)}"))
            self.emit("status", "Downloading…")
            self._download(img_url, path)
            try:
                size = os.path.getsize(path)
                self.emit("log", f"  OK: {os.path.basename(path)} ({_fmt_bytes(size)})")
            except Exception:
                self.emit("log", f"  OK: {os.path.basename(path)}")

            done += 1
            self.emit("overall", done / total * 100)

        self.emit("status", "Ready")

    def _download(self, url, path):
        with self.api.session.get(url, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            done = 0
            t0 = time.time()
            with open(path, "wb") as f:
                for chunk in r.iter_content(262144):
                    if self.stop_flag.is_set():
                        return
                    if not chunk:
                        continue
                    f.write(chunk)
                    done += len(chunk)
                    if total:
                        self.emit("current", done / total * 100)
                    dt = time.time() - t0
                    if dt:
                        self.emit("speed", done / dt)
