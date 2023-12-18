import h5py

from qarchive.qarchive_model import QArchiveRoot
from qarchive.qarchive_store import QArchiveStore


class QArchive:
    def __init__(self, file) -> None:
        self.file = h5py.File(file, "r")
        self.root = QArchiveRoot(self.file["/"])
        self.store = QArchiveStore(self.root)

    def close(self) -> None:
        self.file.close()
