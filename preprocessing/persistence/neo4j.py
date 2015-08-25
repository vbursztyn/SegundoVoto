#!/usr/bin/python
# -*- coding: utf-8 -*-


from py2neo import ServiceRoot


from models import Project, Congressman, Company, Product


class Neo4jPersistence():

	def __init__(self):
		neo4jUri = "http://localhost:7474/"
		self.graph = ServiceRoot(neo4jUri).graph


	def deleteAll(self):
		query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
		self.graph.cypher.execute(query)


	def createProjectNode(self, pType, pId, description):	
		newProjectNode = Project(pType=pType, pId=pId, description=description)
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

	
	def createVote(self, pId, name, position):
		name = name.replace('\'','') # Sanitizing so it doesn't break Cypher
		query = "MATCH (project:Projects { pId: '%s' }), (congressman:Congressmen { name: '%s' }) \
				CREATE (congressman)-[:VOTES { position: '%s' }]->(project)" % (pId, name, position)
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


	def readTopInfluencers(self, pIdStr, positionStr):
		query =  "MATCH (project { pId: '182/2007' })<-[r1 {position: 'YES'}]-(congressman)"
		query += "<-[r2:DONATES]-(company)-[r3:SELLS]->(product)"
		query += " RETURN company.name, sum(r2.value / congressman.total) as total_donation, product.name, product.alternative"
		query += " ORDER BY total_donation DESC"

		results = dict()
		for record in self.graph.cypher.execute(query):
			company = record["company.name"]
			donation = record["total_donation"]
			product = record["product.name"]
			alternative = record["product.alternative"]

			if company not in results:
				results[company] = list()
			
			results[company].append({ "value" : donation, "product" : product, "alternative" : alternative})
		return str(results)