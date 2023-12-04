# Python library for reading Q-Chem archive files

## Convert Q-Chem schema to JSON schema

```bash
bash scripts/codegen.sh qarchive.schema.json
```

## Read a Q-Chem archive file

```python
from qarchive import QArchive

qa = QArchive.from_h5py_file('path/to/archive.h5')
```

## Access the data

```python
# Get energy from the last geometry optimization iteration
 qa.job[0].geom_opt.iter[-1].sp.energy_function[0].energy[()]
 ``````
