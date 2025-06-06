from datetime import datetime
import logging
import time
from utils.settings import settings
import os
import shutil

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename="backup.log",
                    filemode="a",
                    )

logs = logging.getLogger(__name__)

class backupSystem:
    def __init__(self, folder_paths : list = [], schedule_seconds : int = 120, backup_destination : str = ""):
        self.folder_paths = folder_paths
        self.folders_state_dict = {}
        self.schedule_seconds = schedule_seconds
        self.backup_destination = backup_destination
        self.backup_path = None

    def _get_state_folder(self, folder_path : str = ""):
        state = {}

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                currently_path = os.path.join(root, file)
                try:
                    state[currently_path] = {
                        "size": os.path.getsize(currently_path),
                        "mtime": os.path.getmtime(currently_path)
                        }
                except FileNotFoundError:
                    continue
        return state

    def _archive_folder(self, folder_path : str = ""):

        timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
        folder_name = os.path.basename(folder_path.rstrip("/\\"))
        archive_name = f"{folder_name}_{timestamp}"

        archive_currently_path = os.path.join(self.backup_path, archive_name)
        shutil.make_archive(archive_currently_path, "zip", folder_path)

    def _monitoring_folder(self, folder_path : str = ""):

        status_archiving = False

        current_state = self._get_state_folder(folder_path)

        prev_state = self.folders_state_dict.get(folder_path, {})
        added = set(current_state.keys()) - set(prev_state.keys())
        deleted = set(prev_state.keys()) - set(current_state.keys())
        modifed = {path for path in current_state.keys() & prev_state.keys() if current_state[path] != prev_state[path]}

        self.folders_state_dict[folder_path] = current_state

        for path in added:
            logs.info(f'[+] ADDED {path}')
            status_archiving = True

        for path in deleted:
            logs.info(f'[-] DELETED {path}')
            status_archiving = True

        for path in modifed:
            logs.info(f'[-] MODIFED {path}')
            status_archiving = True

        if status_archiving:
            self._archive_folder(folder_path=folder_path)

    def run(self):

        timestamp = datetime.now().strftime("%Y_%m_%d")
        backup_path = os.path.join(self.backup_destination, timestamp)
        os.makedirs(backup_path, exist_ok=True)
        self.backup_path = backup_path

        while True:
            try:
                for folder_path in self.folder_paths:
                    self._monitoring_folder(folder_path=folder_path)
                time.sleep(self.schedule_seconds)
            except KeyboardInterrupt:
                logs.info("Пользователь завершил работу программы.")
            
def main():
    st = settings()
    setting = st._load_settings()
    bs = backupSystem(folder_paths=setting.get("backup_folders"), schedule_seconds=setting.get("schedule_seconds"), backup_destination=setting.get("backup_destination"))
    logs.info(f"Settings: {setting}")
    bs.run()

if __name__ == "__main__":
    main()
