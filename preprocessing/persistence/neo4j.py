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
		query =  "MATCH (project:Projects { pId: '%s', subject: '%s' })<-[vote:VOTES]-(congressman:Congressmen)" % (pId, subject)
		query += "<-[donation:DONATES]-(company:Companies) "
		query += "WHERE ((donation.value / congressman.total) >= 0.05) AND vote.position <> 'ABSTENÇÃO' "
		query += "WITH company.name AS name, collect(vote.position = '%s') AS in_favor " % (position)
		query += "RETURN name, length([x IN in_favor WHERE x = true]) AS in_favor_count,"
		query += "length([x IN in_favor WHERE x = false]) AS against_count,"
		query += "length([x IN in_favor WHERE x = true]) - length([x IN in_favor WHERE x = false]) AS prominent_position "
		query += "ORDER BY prominent_position DESC"

		results = OrderedDict()
		for record in self.graph.cypher.execute(query):
			company = record['name'].replace('.','')
			in_favor_count = record['in_favor_count']
			against_count = record['against_count']
			score = record['prominent_position']

			results[company] = { 'in_favor_count' : in_favor_count, 'against_count' : against_count, 'score' : score }

		return results

