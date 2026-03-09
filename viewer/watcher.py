"""File watcher that detects changes in model files."""

import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ModelFileHandler(FileSystemEventHandler):
    """Watches model files for changes and sets a flag when they are modified."""
    def __init__(self, filenames):
        self.filenames = {os.path.abspath(f) for f in filenames}
        self.changed = threading.Event()
        self.changed.set()  # trigger initial draw

    def on_modified(self, event):
        if os.path.abspath(event.src_path) in self.filenames:
            self.changed.set()


def start_watcher(modelfiles):
    """Start a file watcher on the given model files.
    Returns (observer, file_handler).
    """
    file_handler = ModelFileHandler(modelfiles)
    observer = Observer()
    watched_dirs = {os.path.abspath(os.path.dirname(f) or '.') for f in modelfiles}
    for d in watched_dirs:
        observer.schedule(file_handler, d, recursive=False)
    observer.start()
    return observer, file_handler
