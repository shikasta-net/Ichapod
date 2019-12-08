
from pathlib import Path
import logging

from Episode import Episode

class Record:

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.entries = []
        self.new_entries = []
        if self.file_path.exists():
            with self.file_path.open(mode='r') as record:
                self.entries += [line.rstrip('\n') for line in record]

    def store(self, episode: Episode):
        self.new_entries.append(episode.serialise())

    def check(self, episode: Episode) -> bool:
        return episode.lookup(self.entries)

    def sort(self):
        entries = set(self.entries + self.new_entries)
        temp_file = self.file_path.with_suffix('.tmp')
        with temp_file.open(mode='w+') as record:
            for line in sorted(entries):
                record.write(line+'\n')
        temp_file.replace(self.file_path)
