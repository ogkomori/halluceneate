import time
import shutil
import os
from dotenv import load_dotenv
from pathlib import Path
from classifier import FileClassifier
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent

load_dotenv()

WATCH_FOLDER = Path(os.getenv("WATCH_FOLDER"))
DATA_FOLDER = Path(os.getenv("DATA_FOLDER"))
DESTINATION_FOLDERS = {
    "Notes": DATA_FOLDER / "Notes",
    "Resumes": DATA_FOLDER / "Resumes",
    "Invoices": DATA_FOLDER / "Invoices",
    "Transcripts": DATA_FOLDER / "Transcripts",
    "Other": DATA_FOLDER / "Other"
}

# Create folders if they don't exist
for folder in DESTINATION_FOLDERS.values():
    folder.mkdir(parents=True, exist_ok=True)

def wait_for_file_ready(file_path: Path, timeout=10, interval=0.5):
    # Wait until the file exists and size is stable
    start = time.time()
    last_size = -1
    while time.time() - start < timeout:
        if not file_path.exists():
            time.sleep(interval)
            continue
        current_size = file_path.stat().st_size
        if current_size == last_size and current_size > 0:
            return True
        last_size = current_size
        time.sleep(interval)
    return False

class FileHandler(FileSystemEventHandler):
    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        if event.is_directory:
            return
        src_path = Path(event.src_path)
        # Ignore temporary files
        if src_path.suffix.lower() == ".tmp":
            return
        # Wait for file to be ready
        if not wait_for_file_ready(src_path):
            print(f"File {src_path.name} not ready, skipping...")
            return

        classifier = FileClassifier()
        label = classifier.classify(src_path)
        dest_folder = DESTINATION_FOLDERS[label]
        # Combine the paths with /
        dest_path = dest_folder / src_path.name
        try:
            shutil.move(str(src_path), str(dest_path))
            print(f'Moved "{src_path.name}" -> "{dest_folder}"')
        except Exception as e:
            print(f'Error in moving "{src_path.name}": {e}')

if __name__ == '__main__':
    observer = Observer()
    handler = FileHandler()
    observer.schedule(handler, str(WATCH_FOLDER), recursive=False)
    observer.start()
    print(f'Started watching folder "{WATCH_FOLDER}"')
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
