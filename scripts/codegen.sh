#!/bin/bash

python scripts/to_jsonschema.py $1 > qarchive_schema.json

datamodel-codegen \
    --input qarchive_schema.json \
    --input-file-type jsonschema \
    --output qarchive/qarchive_model.py \
    --output-model-type dataclasses.dataclass \
    --base-class qarchive.qarchive_base.QArchiveBase \
    --use-generic-container-types \
    --use-field-description \
    --field-extra-keys-without-x-prefix x-init x-repr \
    --disable-timestamp \
    --use-schema-description \
    --class-name QArchiveRoot
