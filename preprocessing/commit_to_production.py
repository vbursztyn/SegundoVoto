#!/usr/bin/python
# -*- coding: utf-8 -*-

# IMPORTANT: to be executed from bash file


from config import PRODUCTION_MONGODB, PROJECTS_FILE, PROJECTS_COLLECTION, INFLUENCERS_COLLECTION, DETAILS_COLLECTION


from persistence.mongodb import MongoPersistence


from persistence.csv import CSVReader


from persistence.neo4j import Neo4jPersistence


n4j = Neo4jPersistence()

mdbInterface = MongoPersistence(PRODUCTION_MONGODB, PROJECTS_COLLECTION)
mdbInterface.deleteAll()

mdbResults = MongoPersistence(PRODUCTION_MONGODB, INFLUENCERS_COLLECTION)
mdbResults.deleteAll()

mdbDetails = MongoPersistence(PRODUCTION_MONGODB, DETAILS_COLLECTION)
mdbDetails.deleteAll()

projects = CSVReader(PROJECTS_FILE).readLines()


for project in projects:
	pType = project[0]
	pId = project[1]
	year = project[2]
	subject = project[3]
	description = project[4]
	mdbInterface.createProject(pType, pId, year, subject, description)

	for position in ['SIM', 'NÃO']:
		results = n4j.readTopInfluencers(pId, subject, position)
		mdbResults.createTopInfluencers(pType, pId, year, subject, position, results)
		details = n4j.readTopInfluencersDetails(pId, subject, position)
		mdbDetails.createTopInfluencersDetails(pType, pId, year, subject, position, details)


mdbInterface.close()

mdbResults.close()

mdbDetails.close()

