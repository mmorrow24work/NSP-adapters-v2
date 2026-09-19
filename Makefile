.PHONY: help install test lint verify schema specs mapping all

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-12s %s\n",$$1,$$2}'

install:  ## install the package and dev dependencies
	python3 -m pip install -e ".[dev]"

test:  ## run the full test suite (includes MIB conformance)
	python3 -m pytest tests/ -v

lint:  ## ruff
	python3 -m ruff check src tools tests

verify:  ## check every OID constant against the vendor MIBs
	python3 -m actelis_mediation.cli verify-oids

schema:  ## regenerate the attribute schema CSVs from the OID maps
	python3 tools/build_attribute_schema.py

specs:  ## regenerate row-editor specs from the vendor MIBs
	python3 tools/gen_row_editor_specs.py > src/actelis_mediation/rowedit/specs.py

mapping:  ## regenerate the alarm/PM mapping tables
	python3 tools/build_alarm_pm_mapping.py

all: lint test verify  ## everything CI runs
