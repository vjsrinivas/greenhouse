import os
import sys
sys.path.append("./")
import numpy as np
from typing import *
from datetime import datetime
import time
from devices.database import DatabaseHandler
from pathlib import Path
from loguru import logger

class FileManager:
    def __init__(self, root: str, probe_time_secs=10, size_limit_mb=10000):
        self.root_folder = root
        self.probe_time_secs = probe_time_secs  # seconds
        self.last_datetime = datetime.now()
        self.size_limit = size_limit_mb

    def generate_file_paths(self, root: str) -> Tuple:
        all_files = []
        file_sizes = {}
        file_modified = {}
        for root, dirs, files in os.walk(root):
            for file in files:
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path):
                    all_files.append(full_path)
                    file_sizes[full_path] = self.find_size_datetime(full_path)
                    file_modified[full_path] = self.find_created_datetime(full_path)
        return all_files, file_sizes, file_modified

    def find_created_datetime(self, filename: str):
        # NOTE: ctime isn't always creation time; could be modification time
        timestamp = os.path.getctime(filename)
        return datetime.fromtimestamp(timestamp)

    def find_size_datetime(self, filename: str):
        size_bytes = os.path.getsize(filename)  # Gets size in bytes
        size_mb = size_bytes / (1024 * 1024)
        return size_mb

    def probe(self, db_handler:Optional[DatabaseHandler]=None):
        current_time = datetime.now()

        if (current_time - self.last_datetime).total_seconds() > self.probe_time_secs:
            all_files, file_sizes, file_modified = self.generate_file_paths(
                self.root_folder
            )

            sorted_file_modified = dict(
                sorted(file_modified.items(), key=lambda item: item[1], reverse=False)
            )

            total_size = sum(list(file_sizes.values()))
            if total_size > self.size_limit:
                i = 0
                files = list(sorted_file_modified.keys())
                while total_size > self.size_limit:
                    _file = files[i]
                    _file_stem = Path(_file).name

                    if db_handler:
                        db_handler.record_delete_image(_file_stem)

                    logger.info(f"Removing image {_file_stem}")
                    os.remove(_file)

                    del file_sizes[_file]
                    #print(len(file_sizes))
                    #del sorted_file_modified[_file]

                    i += 1

                    if i > len(files):
                        raise ValueError(
                            "Iterator shouldn't exceed total size of entire directory"
                        )
                    
                    total_size = sum(list(file_sizes.values()))
                    #print(total_size)
            else:
                logger.info(f"Files not big enough: {total_size}")
            self.last_datetime = current_time


def exec_manager(image_folder:str, db_handler: DatabaseHandler):
    file_manager = FileManager(image_folder)
    while True:
        file_manager.probe(db_handler=db_handler)
        time.sleep(3600)

if __name__ == "__main__":
    db_handler = DatabaseHandler("./logs/internal.db")
    file_manager = FileManager("./camera_data/", size_limit_mb=1)
    while True:
        file_manager.probe(db_handler=db_handler)
        time.sleep(3600)
