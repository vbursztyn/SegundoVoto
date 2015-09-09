#!/usr/bin/env python
# -*- coding: utf-8 -*-


from urlparse import urlparse


import pymongo


class MongoPersistence():

	def __init__(self, PRODUCTION_URI, collection):
		self.collectionName = collection
		self.client = pymongo.MongoClient(PRODUCTION_URI)
		self.db = self.client[urlparse(PRODUCTION_URI).path[1:]]
		

	def deleteAll(self):
		collection = self.db[self.collectionName]
		collection.drop()


	def createProject(self, pType=None, pId=None, year=None, subject=None, description=None):
		if all([ pType, pId, year, subject, description ]):
			collection = self.db[self.collectionName]
			saveObj = { 'pType' : pType, 'pId' : pId, 'year' : year, \
					 'subject' : subject, 'description' : description }
			collection.save(saveObj)
		else:
			raise ValueError('Could not register Project to interface collection: missing core data')
	

	def createTopInfluencers(self, pType=None, pId=None, year=None, subject=None, position=None, results=None):
		if all([ pType, pId, year, subject, position, results ]):
			collection = self.db[self.collectionName]
			saveObj = { 'pType' : pType, 'pId' : pId, 'year' : year, \
					 'subject' : subject, 'position' : position, 'results' : results }
			collection.save(saveObj)
		else:
			raise ValueError('Could not register result to results collection: missing core data')


	def createTopInfluencersDetails(self, pType=None, pId=None, year=None, subject=None, position=None, details=None):
		if all([ pType, pId, year, subject, position, details ]):
			collection = self.db[self.collectionName]
			saveObj = { 'pType' : pType, 'pId' : pId, 'year' : year, \
					 'subject' : subject, 'position' : position, 'details' : details }
			collection.save(saveObj)
		else:
			raise ValueError('Could not register result to results collection: missing core data')


	def close(self):
		self.client.close()

