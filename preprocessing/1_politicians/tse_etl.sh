#!/bin/bash

# STEP 1: Download donations
if [ ! -f "prestacao_final_2014.zip" ]; then
	echo "Downloading 2014 donations from TSE:"
	curl --remote-name http://agencia.tse.jus.br/estatistica/sead/odsele/prestacao_contas/prestacao_final_2014.zip
else
	echo "2014 donations already downloaded from TSE."
fi

# STEP 2: Unzip donations
if [ ! -d "raw_donations" ]; then
	echo "Unzipping prestacao_final_2014.zip:"
	unzip prestacao_final_2014.zip -d raw_donations
else
	echo "2014 donations already unzipped."
fi

# STEP 3: Download campaign names
if [ ! -f "consulta_cand_2014.zip" ]; then
	echo "Downloading 2014 candidates from TSE:"
	curl --remote-name http://agencia.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2014.zip
else
	echo "2014 candidates already downloaded from TSE."
fi

# STEP 4: Unzip campaign names
if [ ! -d "raw_candidates" ]; then
	echo "Unzipping consulta_cand_2014.zip:"
	unzip consulta_cand_2014.zip -d raw_candidates
else
	echo "2014 candidates already unzipped."
fi

# STEP 5: Run ETL with Apache Pig + Python UDFs
if [ ! -n "$PIG_HOME" ]; then
	echo "Apache Pig is not installed. Please install it before re-running tse_etl.sh"
else
	echo "Apache Pig is installed. Proceeding to ETL on TSE data:"
	pig -x local pig/tse_etl.pig
fi

# STEP 6: Start Neo4j
if [ ! -n neo4j ]; then
	echo "Neo4j is not installed. Please install it before re-running tse_etl.sh"
else
	echo "Neo4j is installed. Starting it:"
	neo4j start
fi

# STEP 7: Setup Python to persist ETL results on Neo4j
if [ ! -n virtualenv ]; then
	echo "Virtualenv is not installed. Please install it before re-running tse_etl.sh"
else
	echo "Virtualenv is installed. Persisting TSE ETL results on Neo4j:"
	cd ..
	if [ ! -d "etl_venv" ]; then
		virtualenv etl_venv
	fi
	. etl_venv/bin/activate
	pip install -r requirements.txt
	cd 1_politicians
	python -m python.stage_to_neo4j.py
fi
