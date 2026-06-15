import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import os
import sys
import time
import urllib.request
import json
import webbrowser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if sys.platform == "win32":
    _SDIR = os.path.join(SCRIPT_DIR, "scripts", "windows")
    _EXT = ".bat"
else:
    _SDIR = os.path.join(SCRIPT_DIR, "scripts", "linux")
    _EXT = ".sh"
SCRIPTS = {
    "setup": os.path.join(_SDIR, f"setup{_EXT}"),
    "start": os.path.join(_SDIR, f"start{_EXT}"),
    "stop": os.path.join(_SDIR, f"stop{_EXT}"),
    "reset": os.path.join(_SDIR, f"reset{_EXT}"),
}

API_URL = "http://localhost:3000/api/Challenges/?sort=name"
POLL_INTERVAL = 5000

W, H = 960, 700
FONT = "Consolas"
BG = "#0f0f0f"
BG2 = "#171717"
BG3 = "#0b0b0b"
BORDER = "#2a2a2a"
GREEN = "#00e838"
GREEN_DIM = "#1a6629"
GREEN_MID = "#00b82c"
AMBER = "#ffaa00"
RED = "#ff3322"
GREY = "#888888"
TEXT = "#cccccc"

DIFFICULTY_LABEL = {1: "1*", 2: "2*", 3: "3*", 4: "4*", 5: "5*", 6: "6*"}


class ConfirmDialog(tk.Toplevel):
    def __init__(self, parent, title, message, confirm_text="CONFIRM", confirm_color=RED):
        super().__init__(parent)
        self.result = False
        self.title("")
        self.configure(bg=BORDER)
        self.resizable(False, False)
        self.overrideredirect(True)

        DW, DH = 460, 230
        px = parent.winfo_x() + (W - DW) // 2
        py = parent.winfo_y() + (H - DH) // 2
        self.geometry(f"{DW}x{DH}+{px}+{py}")
        self.update_idletasks()

        inner = tk.Frame(self, bg=BG2)
        inner.place(x=1, y=1, width=DW - 2, height=DH - 2)

        tk.Label(inner, text=f"!  {title}", font=(FONT, 12, "bold"),
                 fg=confirm_color, bg=BG2).pack(pady=(26, 10))
        tk.Label(inner, text=message, font=(FONT, 9), fg=TEXT, bg=BG2,
                 justify="center").pack(pady=(0, 26))

        btn_row = tk.Frame(inner, bg=BG2)
        btn_row.pack()
        self._btn(btn_row, "CANCEL", GREY, self._cancel)
        tk.Frame(btn_row, bg=BG2, width=18).pack(side="left")
        self._btn(btn_row, confirm_text, confirm_color, self._confirm)

        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._confirm())

        self.update_idletasks()
        self.update()
        self.grab_set()

    def _btn(self, parent, text, color, cmd):
        outer = tk.Frame(parent, bg=color, cursor="hand2")
        outer.pack(side="left")
        inner = tk.Frame(outer, bg=BG3, cursor="hand2")
        inner.pack(padx=1, pady=1)
        lbl = tk.Label(inner, text=f"  {text}  ", font=(FONT, 10, "bold"),
                       fg=color, bg=BG3, cursor="hand2", pady=8, padx=4)
        lbl.pack()

        def on_enter(e):
            inner.config(bg=color)
            lbl.config(bg=color, fg=BG3)

        def on_leave(e):
            inner.config(bg=BG3)
            lbl.config(bg=BG3, fg=color)

        for w in [outer, inner, lbl]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<ButtonRelease-1>", lambda e, c=cmd: c())

    def _cancel(self):
        self.result = False
        self.destroy()

    def _confirm(self):
        self.result = True
        self.destroy()


class HintDialog(tk.Toplevel):
    def __init__(self, parent, challenge):
        super().__init__(parent)
        self.title("")
        self.configure(bg=BORDER)
        self.resizable(False, False)
        self.overrideredirect(True)

        DW, DH = 540, 300
        px = parent.winfo_x() + (W - DW) // 2
        py = parent.winfo_y() + (H - DH) // 2
        self.geometry(f"{DW}x{DH}+{px}+{py}")

        inner = tk.Frame(self, bg=BG2)
        inner.place(x=1, y=1, width=DW - 2, height=DH - 2)

        header = tk.Frame(inner, bg=BG3)
        header.pack(fill="x")
        name = challenge.get("name", "")
        diff = DIFFICULTY_LABEL.get(challenge.get("difficulty", 1), "?")
        cat = challenge.get("category", "").upper()
        is_solved = challenge.get("solved", False)
        status_color = GREEN if is_solved else AMBER
        status_text = "SOLVED" if is_solved else "OPEN"

        tk.Label(header, text=name, font=(FONT, 11, "bold"),
                 fg=GREEN, bg=BG3).pack(side="left", padx=16, pady=12)
        tk.Label(header, text=f"{diff}  |  {cat}  |",
                 font=(FONT, 8), fg=GREY, bg=BG3).pack(side="left")
        tk.Label(header, text=f"  {status_text}",
                 font=(FONT, 8, "bold"), fg=status_color, bg=BG3).pack(side="left")

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x")

        body = tk.Frame(inner, bg=BG2)
        body.pack(fill="both", expand=True, padx=18, pady=12)

        desc = challenge.get("description", "")
        if desc:
            tk.Label(body, text="DESCRIPTION", font=(FONT, 8, "bold"),
                     fg=GREEN_DIM, bg=BG2).pack(anchor="w", pady=(0, 4))
            tk.Label(body, text=desc, font=(FONT, 9), fg=TEXT, bg=BG2,
                     wraplength=DW - 50, justify="left").pack(anchor="w", pady=(0, 10))
        else:
            tk.Label(body, text="no description available for this challenge.",
                     font=(FONT, 9), fg=GREY, bg=BG2).pack(anchor="w", pady=20)

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x")
        btn_row = tk.Frame(inner, bg=BG2)
        btn_row.pack(pady=14)

        self._btn(btn_row, "CLOSE", GREY, self.destroy)

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self.destroy())

        self.update_idletasks()
        self.update()
        self.grab_set()

    def _btn(self, parent, text, color, cmd):
        outer = tk.Frame(parent, bg=color, cursor="hand2")
        outer.pack(side="left")
        inner = tk.Frame(outer, bg=BG3, cursor="hand2")
        inner.pack(padx=1, pady=1)
        lbl = tk.Label(inner, text=f"  {text}  ", font=(FONT, 10, "bold"),
                       fg=color, bg=BG3, cursor="hand2", pady=8, padx=4)
        lbl.pack()

        def on_enter(e):
            inner.config(bg=color)
            lbl.config(bg=color, fg=BG3)

        def on_leave(e):
            inner.config(bg=BG3)
            lbl.config(bg=BG3, fg=color)

        for w in [outer, inner, lbl]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<ButtonRelease-1>", lambda e, c=cmd: c())


class JuiceShopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Juice Shop Controller")
        self.configure(bg=BORDER)
        self.overrideredirect(True)
        self.geometry(f"{W}x{H}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.update_idletasks()
        sx = (self.winfo_screenwidth() - W) // 2
        sy = (self.winfo_screenheight() - H) // 2
        self.geometry(f"{W}x{H}+{sx}+{sy}")

        if sys.platform == "win32":
            self._setup_win32()

        self._running = False
        self._drag_x = 0
        self._drag_y = 0
        self._challenges = {}
        self._blink_on = True
        self._filter_done = tk.StringVar(value="All")

        self._build_ui()
        self._poll_docker()
        self._poll_challenges()
        self._blink()

    def _setup_win32(self):
        import ctypes
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_APPWINDOW)
        ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)

    def _build_ui(self):
        root = tk.Frame(self, bg=BG)
        root.place(x=1, y=1, width=W - 2, height=H - 2)

        self._build_titlebar(root)

        body = tk.Frame(root, bg=BG)
        body.place(x=0, y=35, width=W - 2, height=H - 37)

        left = tk.Frame(body, bg=BG, width=272)
        left.pack(side="left", fill="y", padx=(14, 6), pady=14)
        left.pack_propagate(False)

        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y", pady=10)

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(8, 14), pady=14)

        self._build_left(left)
        self._build_right(right)

    def _build_titlebar(self, parent):
        bar = tk.Frame(parent, bg=BG2, height=35)
        bar.place(x=0, y=0, width=W - 2)
        bar.bind("<ButtonPress-1>", self._drag_start)
        bar.bind("<B1-Motion>", self._drag_motion)

        tk.Label(bar, text="JUICE SHOP CONTROLLER", font=(FONT, 10, "bold"),
                 fg=GREEN_DIM, bg=BG2).place(x=14, y=9)

        self._status_lbl = tk.Label(bar, text="● OFFLINE", font=(FONT, 10, "bold"),
                                    fg=RED, bg=BG2)
        self._status_lbl.place(x=W // 2 - 52, y=9)

        for txt, xpos, action, hover_fg, hover_bg in [
            (" x ", W - 42, self.destroy, "#ff6644", "#1a0000"),
            (" _ ", W - 76, self._minimize, GREEN, BG3),
        ]:
            b = tk.Label(bar, text=txt, font=(FONT, 11, "bold"),
                         fg=RED if txt.strip() == "x" else GREY, bg=BG2, cursor="hand2")
            b.place(x=xpos, y=7)
            b.bind("<Button-1>", lambda e, a=action: a())
            b.bind("<Enter>", lambda e, w=b, f=hover_fg, bg=hover_bg: w.config(fg=f, bg=bg))
            b.bind("<Leave>", lambda e, w=b, f=(RED if txt.strip() == "x" else GREY): w.config(fg=f, bg=BG2))

        tk.Frame(parent, bg=BORDER, height=1).place(x=0, y=35, width=W - 2)

    def _build_left(self, parent):
        tk.Label(parent, text="CONTROL PANEL", font=(FONT, 9, "bold"),
                 fg=GREEN_DIM, bg=BG).pack(anchor="w", pady=(0, 10))

        for label, sub, color, cmd in [
            ("[ SETUP ]", "pull docker image", AMBER, self._run_setup),
            ("[ START ]", "launch + open browser", GREEN, self._run_start),
            ("[ STOP  ]", "stop container", AMBER, self._run_stop),
            ("[ RESET ]", "wipe container + data", RED, self._run_reset),
        ]:
            self._make_btn(parent, label, sub, color, cmd)

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=14)

        tk.Label(parent, text="SYSTEM LOG", font=(FONT, 9, "bold"),
                 fg=GREEN_DIM, bg=BG).pack(anchor="w", pady=(0, 6))

        log_frame = tk.Frame(parent, bg=BORDER)
        log_frame.pack(fill="both", expand=True)
        log_inner = tk.Frame(log_frame, bg=BG3)
        log_inner.place(x=1, y=1, relwidth=1, relheight=1, width=-2, height=-2)

        self._log = tk.Text(log_inner, bg=BG3, fg=GREEN_MID, font=(FONT, 9),
                            relief="flat", bd=0, state="disabled", wrap="word",
                            padx=8, pady=6, cursor="arrow", spacing1=3)
        self._log.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(log_inner, command=self._log.yview, bg=BG3,
                          troughcolor=BG3, relief="flat", bd=0, width=6)
        sb.pack(side="right", fill="y")
        self._log.config(yscrollcommand=sb.set)

        self._log.tag_config("ok", foreground=GREEN)
        self._log.tag_config("warn", foreground=AMBER)
        self._log.tag_config("err", foreground=RED)
        self._log.tag_config("info", foreground=GREY)
        self._log.tag_config("cmd", foreground=GREEN_MID)
        self._log.tag_config("ts", foreground=GREEN_DIM)
        self._log.tag_config("pr", foreground=GREY)

        self._log_line("ready.", "info")

    def _make_btn(self, parent, label, sub, color, cmd):
        outer = tk.Frame(parent, bg=color, cursor="hand2")
        outer.pack(fill="x", pady=3)
        inner = tk.Frame(outer, bg=BG2, cursor="hand2")
        inner.pack(fill="x", padx=1, pady=1)

        lbl = tk.Label(inner, text=label, font=(FONT, 11, "bold"),
                       fg=color, bg=BG2, cursor="hand2", pady=5)
        lbl.pack()
        slbl = tk.Label(inner, text=sub, font=(FONT, 8),
                        fg=GREY, bg=BG2, cursor="hand2")
        slbl.pack(pady=(0, 6))

        def on_enter(e):
            inner.config(bg=color)
            lbl.config(bg=color, fg=BG)
            slbl.config(bg=color, fg=BG2)

        def on_leave(e):
            inner.config(bg=BG2)
            lbl.config(bg=BG2, fg=color)
            slbl.config(bg=BG2, fg=GREY)

        for w in [outer, inner, lbl, slbl]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", lambda e, c=cmd: c())

    def _build_right(self, parent):
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", pady=(0, 8))

        tk.Label(top, text="CHALLENGES", font=(FONT, 9, "bold"),
                 fg=GREEN_DIM, bg=BG).pack(side="left")

        self._progress_lbl = tk.Label(top, text="0 / 0  (0%)",
                                      font=(FONT, 9), fg=GREEN_MID, bg=BG)
        self._progress_lbl.pack(side="left", padx=18)

        self._prog_bar_var = tk.DoubleVar(value=0)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("G.Horizontal.TProgressbar", troughcolor=BG3,
                        background=GREEN, darkcolor=GREEN, lightcolor=GREEN,
                        bordercolor=BORDER, thickness=10)
        pb = ttk.Progressbar(top, style="G.Horizontal.TProgressbar",
                             variable=self._prog_bar_var, maximum=100, length=140)
        pb.pack(side="left")

        filter_frame = tk.Frame(top, bg=BG)
        filter_frame.pack(side="right")
        tk.Label(filter_frame, text="show:", font=(FONT, 9),
                 fg=GREY, bg=BG).pack(side="left", padx=(0, 6))

        for val, txt in [("All", "all"), ("Pending", "todo"), ("Solved", "done")]:
            rb = tk.Radiobutton(filter_frame, text=txt, value=val,
                                variable=self._filter_done, font=(FONT, 9),
                                fg=GREY, bg=BG, selectcolor=BG, activebackground=BG,
                                activeforeground=GREEN, indicatoron=False, bd=0,
                                padx=7, pady=3, cursor="hand2", command=self._refresh_list)
            rb.pack(side="left", padx=2)

        tree_frame = tk.Frame(parent, bg=BG)
        tree_frame.pack(fill="both", expand=True)

        columns = ("diff", "category", "name", "status")
        self._tree = ttk.Treeview(tree_frame, columns=columns,
                                  show="headings", selectmode="none", cursor="hand2")

        style.configure("Treeview", background=BG3, foreground=TEXT,
                        fieldbackground=BG3, borderwidth=0, rowheight=26,
                        font=(FONT, 9))
        style.configure("Treeview.Heading", background=BG2, foreground=GREEN_DIM,
                        borderwidth=0, font=(FONT, 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", BG2)],
                  foreground=[("selected", GREEN)])
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        self._tree.heading("diff", text="DIFF")
        self._tree.heading("category", text="CATEGORY")
        self._tree.heading("name", text="CHALLENGE")
        self._tree.heading("status", text="STATUS")

        self._tree.column("diff", width=50, anchor="center", stretch=False)
        self._tree.column("category", width=185, anchor="w", stretch=False)
        self._tree.column("name", width=310, anchor="w")
        self._tree.column("status", width=88, anchor="center", stretch=False)

        self._tree.tag_configure("solved", foreground=GREEN)
        self._tree.tag_configure("pending", foreground="#999999")

        self._tree.bind("<ButtonRelease-1>", self._on_challenge_click)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        style.configure("Vertical.TScrollbar", background=BG2, troughcolor=BG3,
                        arrowcolor=GREY, bordercolor=BG3)
        self._tree.configure(yscrollcommand=vsb.set)

        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def _on_challenge_click(self, event):
        item_id = self._tree.identify_row(event.y)
        if not item_id:
            return
        try:
            cid = int(item_id)
        except ValueError:
            return
        challenge = self._challenges.get(cid)
        if challenge:
            dlg = HintDialog(self, challenge)
            self.wait_window(dlg)

    def _refresh_list(self, challenges=None):
        if challenges is not None:
            self._challenges = challenges

        self._tree.delete(*self._tree.get_children())

        filt = self._filter_done.get()
        items = sorted(self._challenges.values(),
                       key=lambda c: (c.get("difficulty", 9), c.get("category", ""), c.get("name", "")))

        solved_count = sum(1 for c in items if c.get("solved"))
        total = len(items)
        pct = int(solved_count / total * 100) if total else 0
        self._progress_lbl.config(text=f"{solved_count} / {total}  ({pct}%)")
        self._prog_bar_var.set(pct)

        for c in items:
            is_solved = c.get("solved", False)
            if filt == "Solved" and not is_solved:
                continue
            if filt == "Pending" and is_solved:
                continue

            cid = c.get("id")
            diff = DIFFICULTY_LABEL.get(c.get("difficulty", 1), "?")
            cat = c.get("category", "")
            name = c.get("name", "")
            status = "[SOLVED]" if is_solved else "[ open ]"
            tag = "solved" if is_solved else "pending"

            self._tree.insert("", "end", iid=str(cid), values=(diff, cat, name, status), tags=(tag,))

    def _poll_challenges(self):
        threading.Thread(target=self._fetch_challenges, daemon=True).start()
        self.after(POLL_INTERVAL, self._poll_challenges)

    def _fetch_challenges(self):
        try:
            req = urllib.request.Request(API_URL, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=4) as r:
                data = json.loads(r.read().decode())

            challenges = {}
            for item in data.get("data", []):
                cid = item.get("id")
                if cid:
                    challenges[cid] = {
                        "id": cid,
                        "name": item.get("name", ""),
                        "category": item.get("category", ""),
                        "difficulty": item.get("difficulty", 1),
                        "solved": item.get("solved", False),
                        "description": item.get("description", ""),
                    }

            prev_solved = {k for k, v in self._challenges.items() if v.get("solved")}
            new_solved = {k for k, v in challenges.items() if v.get("solved")}
            newly_done = new_solved - prev_solved

            for cid in newly_done:
                name = challenges[cid]["name"]
                self.after(0, self._log_line, f"[SOLVED] {name}", "ok")

            self.after(0, self._refresh_list, challenges)
        except Exception:
            pass

    def _log_line(self, text, tag="cmd"):
        self._log.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        self._log.insert("end", f"[{ts}]", "ts")
        self._log.insert("end", " > ", "pr")
        self._log.insert("end", text + "\n", tag)
        self._log.see("end")
        self._log.config(state="disabled")

    def _poll_docker(self):
        threading.Thread(target=self._check_docker, daemon=True).start()
        self.after(4000, self._poll_docker)

    def _check_docker(self):
        try:
            kwargs = {"capture_output": True, "text": True, "timeout": 5}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            r = subprocess.run(
                ["docker", "ps", "--filter", "name=juiceshop", "--format", "{{.Names}}"],
                **kwargs
            )
            online = "juiceshop" in r.stdout
            self.after(0, self._update_docker_status, online)
        except Exception:
            self.after(0, self._update_docker_status, False)

    def _update_docker_status(self, online):
        if online:
            self._status_lbl.config(text="● ONLINE", fg=GREEN)
        else:
            self._status_lbl.config(text="● OFFLINE", fg=RED)

    def _minimize(self):
        if sys.platform == "win32":
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            ctypes.windll.user32.ShowWindow(hwnd, 6)
        else:
            self.iconify()

    def _drag_start(self, e):
        self._drag_x = e.x_root - self.winfo_x()
        self._drag_y = e.y_root - self.winfo_y()

    def _drag_motion(self, e):
        self.geometry(f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    def _blink(self):
        self._blink_on = not self._blink_on
        txt = self._status_lbl.cget("text")
        if "ONLINE" in txt and "OFFLINE" not in txt:
            self._status_lbl.config(fg=GREEN if self._blink_on else BG2)
        else:
            self._status_lbl.config(fg=RED if self._blink_on else BG2)
        self.after(900, self._blink)

    def _run_script(self, key, label):
        if self._running:
            return
        path = SCRIPTS[key]
        if not os.path.exists(path):
            self._log_line(f"script not found: {path}", "err")
            return

        self._running = True
        self._log_line(f"running {label}...", "info")

        def run():
            try:
                if sys.platform == "win32":
                    cmd = ["cmd", "/c", path]
                    enc = "cp850"
                    kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW}
                else:
                    cmd = ["bash", path]
                    enc = "utf-8"
                    kwargs = {}

                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding=enc, errors="replace", **kwargs
                )

                for line in proc.stdout:
                    line = line.rstrip()
                    if not line:
                        continue
                    up = line.upper()
                    if any(x in up for x in ["ERROR", "FAILED"]):
                        tag = "err"
                    elif any(x in up for x in ["[OK]", "READY", "DONE"]):
                        tag = "ok"
                    elif any(x in up for x in ["WARN", "WAITING"]):
                        tag = "warn"
                    else:
                        tag = "cmd"
                    self.after(0, self._log_line, line.lower(), tag)

                proc.wait()
                msg = "done." if proc.returncode == 0 else f"exit code {proc.returncode}"
                tag = "ok" if proc.returncode == 0 else "err"
                self.after(0, self._log_line, f"{label.lower()} -- {msg}", tag)
            except Exception as ex:
                self.after(0, self._log_line, f"exception: {ex}", "err")
            finally:
                self._running = False

        threading.Thread(target=run, daemon=True).start()

    def _run_setup(self):
        self._run_script("setup", "SETUP")

    def _run_start(self):
        self._run_script("start", "START")

    def _run_stop(self):
        self._run_script("stop", "STOP")

    def _run_reset(self):
        dlg = ConfirmDialog(
            self,
            title="DESTRUCTIVE ACTION",
            message="This will stop and remove the container and permanently\n"
                    "delete the Docker volume (all challenge progress).\n\n"
                    "This cannot be undone.",
            confirm_text="WIPE ALL DATA",
            confirm_color=RED,
        )
        self.wait_window(dlg)
        if dlg.result:
            self._run_script("reset", "RESET")


if __name__ == "__main__":
    app = JuiceShopApp()
    app.mainloop()
