"""File watcher that detects changes in model files or the viewer library."""

import os
import threading
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler


class ModelFileHandler(FileSystemEventHandler):
    """Watches model files for changes and sets a flag when they are modified."""
    def __init__(self, filenames):
        self.filenames = {os.path.abspath(f) for f in filenames}
        self.changed = threading.Event()
        self.changed.set()  # trigger initial draw

    def _check(self, event):
        if os.path.abspath(event.src_path) in self.filenames:
            self.changed.set()

    def on_modified(self, event):
        self._check(event)

    def on_created(self, event):
        self._check(event)

    def on_moved(self, event):
        if os.path.abspath(event.dest_path) in self.filenames:
            self.changed.set()


class LibraryFileHandler(FileSystemEventHandler):
    """Watches the viewer package directory and sets a flag on any .py change."""
    def __init__(self):
        self.changed = threading.Event()

    def _check(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            self.changed.set()

    def on_modified(self, event):
        self._check(event)

    def on_created(self, event):
        self._check(event)


def start_watcher(modelfiles):
    """Start file watchers on model files and the viewer package.
    Returns (observer, model_handler, lib_handler).
    """
    model_handler = ModelFileHandler(modelfiles)
    lib_handler = LibraryFileHandler()
    observer = Observer()

    # Watch model files
    watched_dirs = {os.path.abspath(os.path.dirname(f) or '.') for f in modelfiles}
    for d in watched_dirs:
        observer.schedule(model_handler, d, recursive=False)

    # Watch viewer package source
    viewer_dir = os.path.dirname(os.path.abspath(__file__))
    observer.schedule(lib_handler, viewer_dir, recursive=False)

    observer.start()
    return observer, model_handler, lib_handler
