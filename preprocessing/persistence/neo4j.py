#!/usr/bin/python
# -*- coding: utf-8 -*-


from collections import OrderedDict


from py2neo import ServiceRoot


from models import Project, Congressman, Company, Product


class Neo4jPersistence():

	def __init__(self):
		neo4jUri = 'http://localhost:7474/'
		self.graph = ServiceRoot(neo4jUri).graph


	def deleteAll(self):
		query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
		self.graph.cypher.execute(query)


	def createProjectNode(self, pType, pId, year, subject, description):	
		newProjectNode = Project(pType=pType, pId=pId, year=year, subject=subject, description=description)
		self.graph.cypher.execute(newProjectNode.toCypher())


	def createCongressmanNode(self, name, title, party, state, total):
		newCongressmanNode = Congressman(name=name, title=title, party=party, state=state, total=total)
		self.graph.cypher.execute(newCongressmanNode.toCypher())


	def createCompanyNode(self, cId, name):
		newCompanyNode = Company(cId=cId, name=name)
		self.graph.cypher.execute(newCompanyNode.toCypher())


	def createProductNode(self, name, alternative):
		newProductNode = Product(name=name, alternative=alternative)
		self.graph.cypher.execute(newProductNode.toCypher())

	
	def createVote(self, pId, subject, name, position):
		name = name.replace('\'','') # Sanitizing so it doesn't break Cypher
		query = "MATCH (project:Projects { pId: '%s', subject: '%s' }), (congressman:Congressmen { name: '%s' }) \
				CREATE (congressman)-[:VOTES { position: '%s' }]->(project)" % (pId, subject, name, position)
		self.graph.cypher.execute(query)


	def createDonation(self, name, cId, value):
		name = name.replace('\'','') # Sanitizing so it doesn't break Cypher
		query = "MATCH (congressman:Congressmen { name: '%s' }), (company:Companies { cId: '%s' }) \
				CREATE (company)-[:DONATES { value: %f }]->(congressman)" % (name, cId, value)
		self.graph.cypher.execute(query)


	def createB2CRelationship(self, cId, name):
		query = "MATCH (company:Companies { cId: '%s' }), (product:Products { name: '%s' }) \
				CREATE (company)-[:SELLS]->(product)" % (cId, name)
		self.graph.cypher.execute(query)


	def readTopInfluencers(self, pId, subject, position):
		# Since the influences we are looking for are the ones when opposers outweigh allies,
		# we set up the score with allies count, subtract opposers count, then sort it in descending order.
		results = dict()
		oppositePosition = { 'SIM': 'NÃO', 'NÃO': 'SIM' }

		query =  "MATCH (project:Projects { pId: '%s', subject: '%s' })<-[vote:VOTES { position: '%s' }]-" % (pId, subject, position)
		query += "(congressman:Congressmen)<-[donation:DONATES]-(company:Companies)"
		query += " WITH SUM(donation.value) AS company_donations, company.name AS company_name, congressman.name AS congressman_name, congressman.total AS total"
		query += " WHERE (company_donations / total >= 0.05) RETURN company_name, COUNT(DISTINCT congressman_name) AS score ORDER BY score DESC"

		for record in self.graph.cypher.execute(query):
			company = record['company_name'].replace('.','')
			in_favor_count = record['score']
			results[company] = { 'in_favor_count' : in_favor_count, 'against_count' : 0, 'score' : (in_favor_count * (-1)) }

		query =  "MATCH (project:Projects { pId: '%s', subject: '%s' })<-[vote:VOTES { position: '%s' }]-" % (pId, subject, oppositePosition[position])
		query += "(congressman:Congressmen)<-[donation:DONATES]-(company:Companies)"
		query += " WITH SUM(donation.value) AS company_donations, company.name AS company_name, congressman.name AS congressman_name, congressman.total AS total"
		query += " WHERE (company_donations / total >= 0.05) RETURN company_name, COUNT(DISTINCT congressman_name) AS score ORDER BY score DESC"

		for record in self.graph.cypher.execute(query):
			company = record['company_name'].replace('.','')
			against_count = record['score']
			if company not in results:
				results[company] = { 'in_favor_count' : 0, 'against_count' : against_count, 'score' : against_count }
			else:
				results[company]['against_count'] = against_count
				results[company]['score'] += against_count

		return OrderedDict( sorted(results.items(), key=lambda x: x[1]['score'], reverse=True) )


	def readTopInfluencersDetails(self, pId, subject, position):
		results = dict()

		query = "MATCH (project:Projects { pId: '%s', subject: '%s' })<-[vote:VOTES { position: '%s' }]-" % (pId, subject, position)
		query += "(congressman:Congressmen)<-[donation:DONATES]-(company:Companies)"
		query += " WITH SUM(donation.value) AS company_donations, company.name AS company_name, (congressman.name + ' - ' + congressman.party) AS congressman_name, congressman.total AS total"
		query += " WHERE (company_donations / total >= 0.05) RETURN company_name, COLLECT(DISTINCT congressman_name) AS congressmen"

		for record in self.graph.cypher.execute(query):
			company = record['company_name'].replace('.','')
			details = record['congressmen']
			results[company] = details

		return results

