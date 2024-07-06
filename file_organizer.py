import os
import time
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Define the paths for your folders
downloads_folder = "/Users/dakshesh/Downloads"
documents_folder = "/Users/dakshesh/Documents"
images_folder = "/Users/dakshesh/Images"
videos_folder = "/Users/dakshesh/Videos"
others_folder = "/Users/dakshesh/Others"

def is_download_complete(file_path):
    # Ignore hidden and temporary files
    if os.path.basename(file_path).startswith('.') or file_path.endswith('.crdownload'):
        return False
    try:
        # Check if the file size is stable
        initial_size = os.path.getsize(file_path)
        time.sleep(1)
        final_size = os.path.getsize(file_path)
        if initial_size != final_size:
            return False
    except FileNotFoundError:
        return False
    return True

def move_file(file_path):
    if not is_download_complete(file_path):
        logger.info(f'Skipping incomplete download: {file_path}')
        return

    file_name, file_extension = os.path.splitext(file_path)
    logger.info(f'Moving file: {file_path}')

    if file_extension in ['.txt', '.pdf', '.docx', '.xlsx']:
        destination = documents_folder
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
        destination = images_folder
    elif file_extension in ['.mp4', '.mkv', '.avi']:
        destination = videos_folder
    else:
        destination = others_folder

    if not os.path.exists(destination):
        os.makedirs(destination)

    try:
        shutil.move(file_path, os.path.join(destination, os.path.basename(file_path)))
        logger.info(f'File moved to: {destination}')
    except FileNotFoundError:
        logger.warning(f'File not found: {file_path}')

class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            move_file(event.src_path)

# Create an event handler
event_handler = DownloadHandler()

# Set up the observer
observer = Observer()
observer.schedule(event_handler, downloads_folder, recursive=False)

# Start the observer
observer.start()
logger.info('Observer started')

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    logger.info('Observer stopped')

observer.join()

