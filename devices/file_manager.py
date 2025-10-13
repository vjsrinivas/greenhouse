import os
import sys
import numpy as np
from typing import *
from datetime import datetime
import time


class FileManager:
    def __init__(self, root: str, probe_time_secs=10, size_limit_mb=10000):
        self.root_folder = root
        self.probe_time_secs = probe_time_secs  # seconds
        self.last_datetime = datetime.now()
        self.size_limit = size_limit_mb

    def generate_file_paths(self, root: str) -> List:
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

    def probe(self):
        current_time = datetime.now()

        if (current_time - self.last_datetime).total_seconds() > self.probe_time_secs:
            all_files, file_sizes, file_modified = self.generate_file_paths(
                self.root_folder
            )
            sorted_file_modified = dict(
                sorted(file_modified.items(), key=lambda item: item[1], reverse=True)
            )
            total_size = sum(list(file_sizes.values()))
            if total_size > self.size_limit:
                i = 0
                files = list(sorted_file_modified.keys())
                while total_size > self.size_limit:
                    _file = files[i]
                    os.remove(sorted_file_modified[_file])
                    i += 1

                    if i > len(files):
                        raise ValueError(
                            "Iterator shouldn't exceed total size of entire directory"
                        )


if __name__ == "__main__":
    file_manager = FileManager("./camera_data/")
    while True:
        file_manager.probe()
        time.sleep(3600)
