from dataclasses import dataclass, InitVar
from typing import Mapping
import importlib


@dataclass
class QArchiveBase:
    data: InitVar[Mapping]

    def __post_init__(self, data) -> None:
        qarchive_model = importlib.import_module('qarchive.qarchive_model')
        for key, value in data.items():
            if key in self.__annotations__:
                if isinstance(value, Mapping):
                    type_name = self.__annotations__[key]
                    if type_name.startswith('Optional'):
                        type_name = type_name[9:-1]
                    if type_name.startswith('Sequence'):
                        type_name = type_name[9:-1]
                        field_type = getattr(qarchive_model, type_name)
                        setattr(self, key, [
                            field_type(value[k])
                            for k in sorted(value, key=int)
                        ])
                    else:
                        field_type = getattr(qarchive_model, type_name)
                        setattr(self, key, field_type(value))
                else:
                    setattr(self, key, value)
