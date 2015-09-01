#!/bin/bash

# STEP 9: Commit data staged in Neo4j to Production MongoDB
if [ ! -n "$VIRTUAL_HOME" ]; then
	. etl_venv/bin/activate
fi
python -m commit_to_production.py