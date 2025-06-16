from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

def safe_open(filepath, retries=5, delay=1):
    for attempt in range(retries):
        try:
            return open(filepath, "r", encoding="utf-8")
        except PermissionError:
            print(f"File locked: {filepath}, retry {attempt + 1}")
            time.sleep(delay)
    raise PermissionError(f"Failed to open file after {retries} retries: {filepath}")

class LogHandler(FileSystemEventHandler):
    def __init__(self, process_log_callback):
        super().__init__()
        self.process_log_callback = process_log_callback
        self.file_positions = {}

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".txt"):
            print(f"New file detected: {event.src_path}")
            self.file_positions[event.src_path] = 0
            self.process_new_lines(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".txt"):
            print(f"File modified: {event.src_path}")
            self.process_new_lines(event.src_path)

    def process_new_lines(self, filepath):
        last_pos = self.file_positions.get(filepath, 0)
        with safe_open(filepath) as f:
            f.seek(last_pos)
            lines = f.readlines()
            if lines:
                self.process_log_callback(filepath, lines)
                self.file_positions[filepath] = f.tell()

def start_watching(folder_path, process_log_callback):
    event_handler = LogHandler(process_log_callback)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    print(f"Started watching folder: {folder_path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
