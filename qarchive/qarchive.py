import h5py

from qarchive.qarchive_model import QArchive


@classmethod
def from_h5py_file(cls: QArchive, file: h5py.File) -> QArchive:
    file = h5py.File(file, 'r')
    return cls(file)


QArchive.from_h5py_file = from_h5py_file
