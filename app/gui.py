import os, queue, threading, time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .downloader import Downloader

def _fmt_rate(bps: float) -> str:
    """
    Formatiert Bytes pro Sekunde zu KB/s oder MB/s
    """
    try:
        bps = float(bps)
    except Exception:
        return "0 KB/s"

    kb = bps / 1024.0
    if kb < 1024:
        return f"{kb:.1f} KB/s"

    mb = kb / 1024.0
    return f"{mb:.2f} MB/s"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Booru Downloader")
        self.geometry("900x650")
        self.q = queue.Queue()

        self.family_var = tk.BooleanVar(value=False)
        self.downloader = Downloader(self.emit, include_family=self.family_var.get())

        self.status = tk.StringVar(value="Ready")
        self.speed = tk.StringVar(value="0 KB/s")

        self._ui()
        self.after(100, self.poll)

    def emit(self, kind, payload):
        self.q.put((kind, payload))

    def _ui(self):
        f = ttk.Frame(self, padding=10)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Links (1 per line)").pack(anchor="w")
        self.text = tk.Text(f, height=10)
        self.text.pack(fill="x")

        row = ttk.Frame(f)
        row.pack(fill="x", pady=5)

        self.out = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        ttk.Entry(row, textvariable=self.out).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Folder", command=self.pick).pack(side="left")

        ttk.Checkbutton(
            f,
            text="PaChi Mode (Parent+Child)",
            variable=self.family_var,
            command=lambda: self.downloader.set_include_family(self.family_var.get())
        ).pack(anchor="w", pady=(2,6))

        btns = ttk.Frame(f)
        btns.pack(anchor="w", pady=6)
        ttk.Button(btns, text="Download", command=self.start).pack(side="left")
        ttk.Button(btns, text="Abort", command=self.abort).pack(side="left", padx=6)

        ttk.Label(f, text="Current download").pack(anchor="w")
        self.pb1 = ttk.Progressbar(f, maximum=100)
        self.pb1.pack(fill="x", pady=(2, 8))

        ttk.Label(f, text="Overall progress").pack(anchor="w")
        self.pb2 = ttk.Progressbar(f, maximum=100)
        self.pb2.pack(fill="x", pady=(2, 6))

        stat = ttk.Frame(f)
        stat.pack(fill="x")
        ttk.Label(stat, textvariable=self.status).pack(side="left")
        ttk.Label(stat, text="Speed:").pack(side="right")
        ttk.Label(stat, textvariable=self.speed).pack(side="right", padx=(6,0))

        self.log = tk.Text(f, state="disabled")
        self.log.pack(fill="both", expand=True)

    def pick(self):
        d = filedialog.askdirectory()
        if d:
            self.out.set(d)

    def start(self):
        urls = [l.strip() for l in self.text.get("1.0", "end").splitlines() if l.strip()]
        if not urls:
            messagebox.showwarning("Fehler", "Keine Links")
            return
        os.makedirs(self.out.get(), exist_ok=True)

        self.downloader.set_include_family(self.family_var.get())
        threading.Thread(target=self.downloader.run, args=(urls, self.out.get()), daemon=True).start()

    def abort(self):
        self.downloader.stop()

    def poll(self):
        try:
            while True:
                k, p = self.q.get_nowait()
                if k == "log":
                    self.log.configure(state="normal")
                    self.log.insert("end", f"[{time.strftime('%H:%M:%S')}] {p}\n")
                    self.log.configure(state="disabled")
                    self.log.see("end")
                elif k == "status":
                    self.status.set(p)
                elif k == "current":
                    self.pb1["value"] = p
                elif k == "overall":
                    self.pb2["value"] = p
                elif k == "speed":
                    self.speed.set(_fmt_rate(float(p)))
        except queue.Empty:
            pass
        self.after(100, self.poll)
