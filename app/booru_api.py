import re
import time
import requests

class DanbooruAPI:
    BASE = "https://danbooru.donmai.us"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "BooruDownloader/1.0 (contact: local-user)",
            "Referer": self.BASE + "/"
        })

    @staticmethod
    def match(url: str) -> int | None:
        m = re.search(r"danbooru\.donmai\.us/posts/(\d+)", url)
        if not m:
            m = re.search(r"/posts/(\d+)", url)
        return int(m.group(1)) if m else None

    def _get(self, url: str, timeout: int = 20):
        while True:
            r = self.session.get(url, timeout=timeout)
            if r.status_code == 429:
                time.sleep(2)
                continue
            r.raise_for_status()
            return r

    def get_post(self, post_id: int) -> dict:
        return self._get(f"{self.BASE}/posts/{post_id}.json").json()

    def get_children(self, parent_id: int, limit: int = 200) -> list[int]:
        data = self._get(f"{self.BASE}/posts.json?tags=parent:{parent_id}&limit={limit}").json()
        out = []
        for p in data:
            if p.get("parent_id") == parent_id and p.get("id") is not None:
                out.append(int(p["id"]))
        return out

    @staticmethod
    def image_url(data: dict) -> str | None:
        return data.get("file_url") or data.get("large_file_url")

    @staticmethod
    def character_tag(data: dict) -> str:
        s = (data.get("tag_string_character") or "").strip()
        return s.split(" ")[0] if s else "unknown"
