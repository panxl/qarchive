from typing import List, Union
from collections.abc import Sequence
from dataclasses import dataclass, field
import tables


class QArchive(object):
    def __init__(self, filename):
        self.file = tables.open_file(filename, mode='r')

        jobs = []
        for job in self.file.root.job:
            node = job._f_list_nodes()[0]
            job_class = job_class_mapping[node._v_name]
            jobs.append(job_class(node))
        self.job = Job(jobs)

    def close(self):
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __repr__(self):
        return f'QArchive(\'{self.file.filename}\')'


@dataclass(frozen=True)
class SP(object):
    _node: tables.Group
    energy_function: List[tables.Group] = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'energy_function', self._node.energy_function._f_list_nodes())

    @property
    def energy(self):
        return self.energy_function[-1].energy[()]
    
    @property
    def gradient(self):
        if 'gradient' in self.energy_function[-1]._v_children:
            return self.energy_function[-1].gradient[()]

    @property
    def hessian(self):
        if 'hessian' in self.energy_function[-1]._v_children:
            return self.energy_function[-1].hessian[()]

    @property
    def mo_coefficients(self):
        return self.energy_function[-1].method.scf.molecular_orbitals.mo_coefficients[()]


@dataclass(frozen=True)
class GeomOpt(object):
    _node: tables.Group
    iter: List[SP] = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'iter', [SP(iter.sp) for iter in self._node.iter._f_iter_nodes()])

    @property
    def energy(self):
        return self.iter[-1].energy

    @property
    def gradient(self):
        return self.iter[-1].gradient

    @property
    def hessian(self):
        return self.iter[-1].hessian

    @property
    def mo_coefficients(self):
        return self.iter[-1].mo_coefficients


job_class_mapping = {
    "sp": SP,
    "geom_opt": GeomOpt,
    }


@dataclass(frozen=True)
class Job(Sequence):
    _jobs: List[Union[SP, GeomOpt]]

    def __len__(self):
        return len(self._jobs)

    def __getitem__(self, index):
        return self._jobs[index]
