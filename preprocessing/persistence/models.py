#!/usr/bin/python
# -*- coding: utf-8 -*-


class Project(object):

	def __init__(self, pType=None, pId=None, year=None, subject=None, description=None):
		self.type = pType
		self.pId = pId
		self.year = year
		self.subject = subject
		self.description = description


	def toCypher(self):
		return "CREATE (project:Projects { pType: '%s', pId: '%s', year: '%s', \
				subject: '%s', description: '%s' })" % (self.type, self.pId, self.year, self.subject, self.description)


class Congressman(object):

	def __init__(self, name=None, title=None, party=None, state=None, total=None):
		self.name = name.replace('\'','') # Sanitizing so it doesn't break Cypher
		self.title = title
		self.party = party
		self.state = state
		self.total = float(total)


	def toCypher(self):
		return "CREATE (congressman:Congressmen { name: '%s', title: '%s', party: '%s', \
				state: '%s', total: %f })" % (self.name, self.title, self.party, self.state, self.total)


class Company(object):

	def __init__(self, cId=None, name=None):
		self.cId = cId
		self.name = name.replace('\'','') # Sanitizing so it doesn't break Cypher
		

	def toCypher(self):
		return "CREATE (company:Companies { cId: '%s', name: '%s' })" % (self.cId, self.name)


class Product(object):

	def __init__(self, name=None, alternative=None):
		self.name = name
		self.alternative = alternative
		

	def toCypher(self):
		return "CREATE (product:Products { name: '%s', alternative: '%s' })" % (self.name, self.alternative)

