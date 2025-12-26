import os, re
from urllib.parse import urlparse

INVALID_FS_RE = re.compile(r'[<>:"/\\|?*]')

def sanitize_filename(name: str, fallback="unknown"):
    name = (name or "").strip() or fallback
    return INVALID_FS_RE.sub("_", name)

def unique_path(path):
    base, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(path):
        path = f"{base}-{i}{ext}"
        i += 1
    return path

def guess_extension_from_url(url):
    ext = os.path.splitext(urlparse(url).path)[1]
    return ext if ext else ".jpg"
