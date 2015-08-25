#!/bin/bash

# STEP 8: Fetch votings using Congress API, based on a local target list
if [ ! -n "$VIRTUAL_HOME" ]; then
	. ../etl_venv/bin/activate
fi
python -m stage_to_neo4j.py