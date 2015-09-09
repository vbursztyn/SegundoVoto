#!/usr/bin/env python
# -*- coding: utf-8 -*-


from urlparse import urlparse


import os


import pymongo


import json


class MongoPersistence():

	def __init__(self, collection):
		self.collectionName = collection
		MONGO_URI = os.environ.get('MONGOLAB_URI')
		if MONGO_URI:
			self.client = pymongo.MongoClient(MONGO_URI)
			self.db = self.client[urlparse(MONGO_URI).path[1:]]
		else:
			self.client = pymongo.MongoClient('localhost, 27017')
			self.db = self.client['test']


	def getInterface(self):
		collection = self.db[self.collectionName]
		results = list()

		for result in collection.find():
			results.append(result)

		return results


	def getResult(self, pType, pId, year, subject, position):
		collection = self.db[self.collectionName]
		results = dict()

		for result in collection.find({ 'pType': pType, 'pId': pId, 'year': year, \
										'subject': subject, 'position' : position }):
			for company, values in result['results'].iteritems():
				results[company] = { 'in_favor_count': int(values['in_favor_count']), \
									'against_count': int(values['against_count']) }

		return results


	def getProjectDetails(self, pType, pId, year, subject, position):
		collection = self.db[self.collectionName]
		results = dict()

		for result in collection.find({ 'pType': pType, 'pId': pId, 'year': year, \
										'subject': subject, 'position' : position }):
			for company, congressmen in result['details'].iteritems():
				results[company] = congressmen

		return json.dumps(results, indent=4)


	def getDescription(self, pType, pId, year, subject):
		collection = self.db[self.collectionName]
		return json.dumps(collection.find_one({ 'pType': pType, 'pId': pId, 'year': year, \
												'subject': subject })['description'])


	def close(self):
		self.client.close()

