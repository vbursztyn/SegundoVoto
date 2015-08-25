#!/usr/bin/python
# -*- coding: utf-8 -*-

# IMPORTANT: to be executed from bash file


import sys, os
sys.path.append(os.path.join(os.getcwd(), '..'))


from persistence.csv import CSVReader


from persistence.neo4j import Neo4jPersistence


politiciansObj = dict()

companiesObj = dict()

pigOut = CSVReader('pig_output/part-r-00000', separator=',').readLines()


for tokens in pigOut:
	internalId = long(tokens[0])

	state = tokens[1]
	party = tokens[2]
	donationValue = float(tokens[5])
	donatorId = long(tokens[6])
	donatorName = tokens[7]
	name = tokens[10]
	total = float(tokens[-1][:-1])
	
	if internalId not in politiciansObj:
		politiciansObj[internalId] = dict()
		politiciansObj[internalId]['state'] = state
		politiciansObj[internalId]['party'] = party
		politiciansObj[internalId]['donations_values'] = list()
		politiciansObj[internalId]['donators_ids'] = list()
		politiciansObj[internalId]['donators_names'] = list()
		politiciansObj[internalId]['name'] = name
		politiciansObj[internalId]['total'] = total

	politiciansObj[internalId]['donations_values'].append(donationValue)
	politiciansObj[internalId]['donators_ids'].append(donatorId)
	politiciansObj[internalId]['donators_names'].append(donatorName)

	if donatorId not in companiesObj:
		companiesObj[donatorId] = donatorName


n4j = Neo4jPersistence()

n4j.deleteAll()

for key, value in companiesObj.iteritems():
	n4j.createCompanyNode(key, value)


for key, value in politiciansObj.iteritems():
	n4j.createCongressmanNode(value['name'], 'Deputado Federal', value['party'], value['state'], value['total'])
	for i in range( len(value['donators_ids']) ):
		n4j.createDonation(value['name'], value['donators_ids'][i], value['donations_values'][i])


