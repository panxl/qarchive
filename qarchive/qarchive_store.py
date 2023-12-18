from collections.abc import Mapping

from qarchive.qarchive_base import QArchiveBase
from qarchive.qarchive_model import QArchiveRoot


class QArchiveStore(Mapping):
    def __init__(self, data: QArchiveRoot) -> None:
        self.data = {}
        self.add_data(data)

    def add_data(self, data) -> None:
        for key, value in vars(data).items():
            if isinstance(value, list):
                for v in value:
                    self.add_data(v)
            elif isinstance(value, QArchiveBase):
                self.add_data(value)
            else:
                if self.data.get(key) is None:
                    self.data[key] = [value]
                else:
                    self.data[key].append(value)

    def __getitem__(self, key):
        return [v[()] for v in self.data[key]]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
