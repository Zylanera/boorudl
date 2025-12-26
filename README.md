# Booru Downloader — Danbooru & Co.

A **-booru downloader**: paste links → download files → done.

* Focus: **Danbooru** (via the JSON API, stable & fast)
* Fallback: other boorus via HTML (best effort)
* Clean UI: progress, speed, log

> Note: Respect the terms of service of the respective website.

---

## Features

### GUI

* Paste **links (1 per line)**
* Start **download**
* **Cancel** (stops after the current chunk)
* **Current download** progress
* **Overall progress** across all queue items
* **Live speed**
* **Log**

### Danbooru (API)

* Regular post links work (e.g. `https://danbooru.donmai.us/posts/7520078?...`)
* Tool internally maps to: `/posts/<id>.json`
* **403 protection:** API-compliant User-Agent is set
* **Original file:** prefers `file_url` (original), otherwise fallback to `large_file_url`

---

## PaChi Mode (Parent + Child)

**PaChi Mode** stands for **Parent + Child**.

When enabled, for each pasted Danbooru link:

* **If you paste a parent post:**
  → downloads the **parent + all direct children** of that parent

* **If you paste a child post:**
  → downloads the **parent** of that child **+ all children** (i.e. the “siblings”)
  → plus optionally the child itself (which is already part of the children list)

---

## Installation (Development)

### Requirements

* Python **3.10+**

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
python -m app.main
```

---

## Usage

1. Start the program
2. Paste links (1 per line)
3. Choose the target folder
4. Optional: enable **PaChi Mode**
5. Click **Download**

In the log you’ll see per file:

* Source (post ID / URL)
* Result (file name)
* **Size** in KB / MB / GB

---

## File Naming

For Danbooru, the default attempt is:

* first character tag (`tag_string_character`)
* if none exists: `unknown`

If multiple files have the same name, they are automatically numbered:

* `name.png`
* `name-1.png`
* `name-2.png`

---

## Building an EXE (Windows)

### 1) Install PyInstaller

```bash
pip install pyinstaller
```

### 2) Build

From the project root:

```bash
pyinstaller --onefile --noconsole -n BooruDownloader run.py
```

Result:

* `dist\BooruDownloader.exe`

Optional icon:

```bash
pyinstaller --onefile --noconsole --icon app.ico -n BooruDownloader run.py
```

---

## Troubleshooting

### Danbooru API: 403

* This project sets an API-compliant User-Agent.
* If you still get 403:

  * Check firewall / VPN / proxy
  * Test in a browser whether Danbooru is reachable
  * Danbooru may temporarily rate-limit more aggressively

### “Too many” files are being downloaded

* Check whether **PaChi Mode** is enabled.
* PaChi downloads the entire parent family (parent + children).

---

## Project Structure

```
project/
  run.py           # needed for .exe build
  requirements.txt # python requirements
  app/
    gui.py         # UI
    downloader.py  # Worker (thread)
    booru_api.py   # Danbooru API
    parsers.py     # HTML fallback
    utils.py       # helpers
```

---

## License

see LICENCE.md
