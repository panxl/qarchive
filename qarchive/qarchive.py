from typing import Union, Optional
from dataclasses import dataclass, field
from numpy import ndarray
import tables


class QArchive:
    """A class for reading Q-Chem archive files."""
    def __init__(self, filename) -> None:
        self.file = tables.open_file(filename, mode='r')

        jobs : list[Job] = []
        for job in self.file.root.job:
            node = job._f_list_nodes()[0]
            job_class = job_class_mapping[node._v_name]
            jobs.append(job_class(node))
        self.jobs = sorted(jobs, key=lambda job: job.sort_index)

    def close(self) -> None:
        """Close the archive file."""
        self.file.close()

    def __enter__(self) -> 'QArchive':
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
    energy_function: list[tables.Group] = field(init=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'sort_index', int(self._node._v_parent._v_name))
        object.__setattr__(self, 'energy_function', self._node.energy_function._f_list_nodes())

    @property
    def energy(self) -> float:
        """Return the energy."""
        return self.energy_function[-1].energy[()]

    @property
    def gradient(self) -> Optional[ndarray]:
        """Return the gradient."""
        if 'gradient' in self.energy_function[-1]:
            return self.energy_function[-1].gradient[()]
        return None

    @property
    def hessian(self) -> Optional[ndarray]:
        """Return the hessian."""
        if 'hessian' in self.energy_function[-1]:
            return self.energy_function[-1].hessian[()]
        return None

    @property
    def mo_coefficients(self) -> ndarray:
        """Return the MO coefficients."""
        return self.energy_function[-1].method.scf.molecular_orbitals.mo_coefficients[()]


@dataclass(frozen=True, order=True)
class GeomOpt:
    """A class for reading geometry optimization calculations from Q-Chem archive files."""
    _node: tables.Group = field(compare=False)
    sort_index: int = field(init=False, repr=False)
    iter: list[SP] = field(init=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'sort_index', int(self._node._v_parent._v_name))
        iters = sorted([SP(iter.sp) for iter in self._node.iter._f_iter_nodes()])
        object.__setattr__(self, 'iter', iters)

    @property
    def energy(self) -> float:
        """Return the energy of the last iteration."""
        return self.iter[-1].energy

    @property
    def gradient(self) -> Optional[ndarray]:
        """Return the gradient of the last iteration."""
        return self.iter[-1].gradient

    @property
    def hessian(self) -> Optional[ndarray]:
        """Return the hessian of the last iteration."""
        return self.iter[-1].hessian

    @property
    def mo_coefficients(self) -> ndarray:
        """Return the MO coefficients of the last iteration."""
        return self.iter[-1].mo_coefficients


Job = Union[SP, GeomOpt]


job_class_mapping : dict[str, type] = {
    "sp": SP,
    "geom_opt": GeomOpt,
    }
