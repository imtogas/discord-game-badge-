import json, os, re, subprocess, threading, urllib.parse, urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

BASE = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "SteamDiscordLauncher"
BASE.mkdir(parents=True, exist_ok=True)
FAV = BASE / "favorites.json"
HELPER_SRC = "using System; using System.Threading; class Program { static void Main() { while(true) Thread.Sleep(1000); } }"

class App:
    def __init__(self, root):
        self.root = root
        root.title("Steam Discord Launcher — Prototype")
        root.geometry("770x570")
        self.proc = None
        self.results = []
        try:
            self.favorites = json.loads(FAV.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.favorites = []
        wrap = ttk.Frame(root, padding=18)
        wrap.pack(fill="both", expand=True)
        ttk.Label(wrap, text="Steam Discord Launcher", font=("Segoe UI", 19, "bold")).pack(anchor="w")
        ttk.Label(wrap, text="Experimental: Discord recognition and Game Variety credit are not guaranteed.").pack(anchor="w", pady=(0, 12))
        line = ttk.Frame(wrap)
        line.pack(fill="x")
        self.query = tk.StringVar()
        entry = ttk.Entry(line, textvariable=self.query)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda event: self.search())
        ttk.Button(line, text="Search Steam", command=self.search).pack(side="left", padx=8)
        ttk.Button(line, text="Favorites", command=self.show_favorites).pack(side="left")
        self.listbox = tk.Listbox(wrap, height=12, exportselection=False)
        self.listbox.pack(fill="both", expand=True, pady=12)
        self.listbox.bind("<<ListboxSelect>>", self.pick)
        self.game = tk.StringVar()
        self.exe = tk.StringVar()
        for label, variable in (("Selected game:", self.game), ("Executable name:", self.exe)):
            row = ttk.Frame(wrap)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, width=18).pack(side="left")
            ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)
        ttk.Label(wrap, text="Enter the real game executable filename if known (e.g. game.exe).").pack(anchor="w", pady=6)
        actions = ttk.Frame(wrap)
        actions.pack(fill="x", pady=8)
        ttk.Button(actions, text="Start mock process", command=self.start).pack(side="left")
        ttk.Button(actions, text="Stop", command=self.stop).pack(side="left", padx=8)
        ttk.Button(actions, text="Add favorite", command=self.add_favorite).pack(side="left")
        self.status = tk.StringVar(value="Ready. No account credentials needed.")
        ttk.Label(wrap, textvariable=self.status, wraplength=710).pack(anchor="w")
        root.protocol("WM_DELETE_WINDOW", self.close)

    def show_results(self, items):
        self.results = items
        self.listbox.delete(0, "end")
        for item in items:
            self.listbox.insert("end", item["name"])

    def search(self):
        query = self.query.get().strip()
        if not query:
            return
        self.status.set("Searching Steam Store...")
        def work():
            try:
                url = "https://store.steampowered.com/api/storesearch/?" + urllib.parse.urlencode({"term": query, "l": "english", "cc": "us"})
                request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=12) as response:
                    data = json.load(response)
                items = [{"name": item["name"], "exe": ""} for item in data.get("items", [])]
                self.root.after(0, lambda: (self.show_results(items), self.status.set(f"{len(items)} results.")))
            except Exception as error:
                self.root.after(0, lambda: self.status.set(f"Search failed: {error}"))
        threading.Thread(target=work, daemon=True).start()

    def show_favorites(self):
        self.show_results(self.favorites)
        self.status.set("Favorites loaded.")

    def pick(self, event=None):
        selected = self.listbox.curselection()
        if selected:
            item = self.results[selected[0]]
            self.game.set(item["name"])
            self.exe.set(item.get("exe", ""))

    def add_favorite(self):
        name = self.game.get().strip()
        if name:
            item = {"name": name, "exe": self.exe.get().strip()}
            self.favorites = [x for x in self.favorites if x["name"] != name] + [item]
            FAV.write_text(json.dumps(self.favorites, ensure_ascii=False, indent=2), encoding="utf-8")
            self.status.set("Favorite saved.")

    def start(self):
        if os.name != "nt":
            messagebox.showerror("Windows required", "This app requires Windows.")
            return
        name, exe = self.game.get().strip(), self.exe.get().strip()
        if not name or not re.fullmatch(r"[A-Za-z0-9_. -]{1,100}\.exe", exe, re.I):
            messagebox.showwarning("Invalid input", "Choose a game and enter a valid .exe filename.")
            return
        if exe.lower() in {"explorer.exe", "svchost.exe", "discord.exe", "steam.exe"}:
            messagebox.showerror("Invalid name", "Choose a game executable, not a system application.")
            return
        if self.proc and self.proc.poll() is None:
            messagebox.showinfo("Already running", "Stop the previous mock process first.")
            return
        try:
            folder = BASE / "mock"
            folder.mkdir(exist_ok=True)
            target = folder / exe
            if not target.exists():
                source = BASE / "mock_process.cs"
                source.write_text(HELPER_SRC, encoding="utf-8")
                command = "Add-Type -Path '" + str(source).replace("'", "''") + "' -OutputAssembly '" + str(target).replace("'", "''") + "' -OutputType ConsoleApplication"
                result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command], capture_output=True, text=True, timeout=40)
                if result.returncode or not target.exists():
                    raise RuntimeError((result.stderr or result.stdout or "Compilation failed")[-700:])
            self.proc = subprocess.Popen([str(target)], cwd=str(folder), creationflags=subprocess.CREATE_NO_WINDOW)
            self.status.set(f"Started {exe} (PID {self.proc.pid}). Check Discord manually.")
        except Exception as error:
            messagebox.showerror("Start failed", str(error))

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = None
        self.status.set("Stopped.")

    def close(self):
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
