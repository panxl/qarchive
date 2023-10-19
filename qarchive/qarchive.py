from __future__ import annotations
from typing import Union, Optional
from dataclasses import dataclass, field
import numpy as np
import tables


class QArchive:
    """A class for reading Q-Chem archive files."""
    def __init__(self, filename) -> None:
        self.file = tables.open_file(filename, mode='r')

        jobs : list[Job] = []
        for job in self.file.root.job:
            node = job._f_list_nodes()[0]
            jobs.append(create_job(node))
        self.jobs = sorted(jobs, key=lambda job: job.sort_index)

    def close(self) -> None:
        """Close the archive file."""
        self.file.close()

    def __enter__(self) -> QArchive:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __repr__(self) -> str:
        return f'QArchive(\'{self.file.filename}\')'


@dataclass(frozen=True, order=True)
class SP:
    """A class for reading single point energy calculations from Q-Chem archive files."""
    _node: tables.Group = field(compare=False)
    sort_index: int = field(init=False, repr=False)
    aobasis: tables.Group = field(init=False, compare=False, repr=False)
    energy_function: list[tables.Group] = field(init=False, compare=False, repr=False)
    structure: tables.Group = field(init=False, compare=False, repr=False)
    observables: Optional[tables.Group] = field(init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'sort_index', int(self._node._v_parent._v_name))
        object.__setattr__(self, 'aobasis', self._node.aobasis)
        object.__setattr__(self, 'energy_function', self._node.energy_function._f_list_nodes())
        object.__setattr__(self, 'structure', self._node.structure)
        if "observables" in self._node:
            object.__setattr__(self, 'observables', self._node.observables)

    @property
    def energy(self) -> float:
        """Return the energy."""
        return self.energy_function[-1].energy.read().item()

    @property
    def gradient(self) -> Optional[np.ndarray]:
        """Return the gradient."""
        if 'gradient' in self.energy_function[-1]:
            return self.energy_function[-1].gradient.read()
        return None

    @property
    def hessian(self) -> Optional[np.ndarray]:
        """Return the hessian."""
        if 'hessian' in self.energy_function[-1]:
            return self.energy_function[-1].hessian.read()
        return None

    @property
    def mo_coefficients(self) -> np.ndarray:
        """Return the MO coefficients."""
        return self.energy_function[-1].method.scf.molecular_orbitals.mo_coefficients.read()

    @property
    def alpha_mo_coefficients(self) -> np.ndarray:
        """Return the Alpha MO coefficients."""
        return self.mo_coefficients[0]

    @property
    def beta_mo_coefficients(self) -> np.ndarray:
        """Return the Beta MO coefficients."""
        return self.mo_coefficients[-1]

@dataclass(frozen=True, order=True)
class GeomOpt:
    """A class for reading geometry optimization calculations from Q-Chem archive files."""
    _node: tables.Group = field(compare=False)
    sort_index: int = field(init=False, repr=False)
    iters: list[SP] = field(init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'sort_index', int(self._node._v_parent._v_name))
        iters = sorted([SP(iter.sp) for iter in self._node.iter._f_iter_nodes()])
        object.__setattr__(self, 'iters', iters)

    @property
    def energy(self) -> float:
        """Return the energy of the last iteration."""
        return self.iters[-1].energy

    @property
    def gradient(self) -> Optional[np.ndarray]:
        """Return the gradient of the last iteration."""
        return self.iters[-1].gradient

    @property
    def hessian(self) -> Optional[np.ndarray]:
        """Return the hessian of the last iteration."""
        return self.iters[-1].hessian

    @property
    def mo_coefficients(self) -> np.ndarray:
        """Return the MO coefficients of the last iteration."""
        return self.iters[-1].mo_coefficients

    @property
    def energies(self) -> np.ndarray:
        """Return the energies of all iterations."""
        return np.array([iter.energy for iter in self.iters])


Job = Union[SP, GeomOpt]


job_class_mapping : dict[str, type] = {
    "sp": SP,
    "geom_opt": GeomOpt,
    }


def create_job(node: tables.Group) -> Job:
    """Create a Job object from a node."""
    job_type = node._v_name
    if job_type not in job_class_mapping:
        raise ValueError(f'Unknown job type: {job_type}')
    job_class = job_class_mapping[job_type]
    return job_class(node)
