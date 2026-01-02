import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, Set

SUPPORTED_EXTENSIONS: Set[str] = {".md", ".txt", ".markdown", ".pdf", ".docx"}


class AutoIndexHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback

    def _is_supported(self, path: str) -> bool:
        ext = Path(path).suffix.lower()
        return ext in SUPPORTED_EXTENSIONS

    def on_created(self, event):
        if not event.is_directory and self._is_supported(event.src_path):
            print(f"[Watcher] New file detected: {event.src_path}")
            self.callback(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and self._is_supported(event.src_path):
            print(f"[Watcher] File modified: {event.src_path}")
            self.callback(event.src_path)

class DirectoryWatcher:
    def __init__(self, path: str, callback: Callable[[str], None]):
        self.path = path
        self.callback = callback
        self.observer = Observer()
        self._handler = AutoIndexHandler(callback)

    def start(self):
        if not os.path.exists(self.path):
            print(f"[Watcher] Path does not exist: {self.path}")
            return
            
        self.observer.schedule(self._handler, self.path, recursive=True)
        self.observer.start()
        print(f"[Watcher] Started watching: {self.path}")

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            print("[Watcher] Stopped watching")
