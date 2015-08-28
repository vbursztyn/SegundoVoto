#!/usr/bin/python
# -*- coding: utf-8 -*-

# IMPORTANT: to be executed from bash file


import sys, os
sys.path.append(os.path.join(os.getcwd(), '..'))


import untangle, urllib2


from config import PROJECTS_FILE, CONGRESS_URL, CONGRESS_TO_TSE_FILE


from persistence.csv import CSVReader


from persistence.neo4j import Neo4jPersistence


positions = { u'S': 'SIM', u'N': 'NÃO', u'A': 'ABSTENÇÃO', u'O': 'ABSTENÇÃO' }


class VotingToTSE():

	def __init__(self, data):
		self.map = dict()
		for tokens in data:
			self.map[tokens[0]] = tokens[1]


	def toTSE(self, votingName):
		try:
			return self.map[votingName]
		except KeyError as e:
			print 'Unable to find politician: ', e



class ProjectFetcher():

	def __init__(self, tokens):
		self.pType = tokens[0]
		self.pId = tokens[1]
		self.year = tokens[2]
		self.subject = unicode(tokens[3].replace('\"','').decode('utf8'))
		self.description = tokens[4]


	def getURL(self):
		return CONGRESS_URL % (self.pType, self.pId, self.year)


	def fetchContent(self):
		response = urllib2.urlopen(self.getURL())
		self.contentObj = untangle.parse(response.read())

		subjectVoting = None
		for voting in self.contentObj.proposicao.Votacoes.Votacao:
			if voting['ObjVotacao'] == self.subject:
				subjectVoting = voting
				break

		if not subjectVoting:
			raise KeyError('Voting subject ' + self.subject + ' did not match any in ' + self.getURL())

		self.voting = subjectVoting.votos


	def parseVoting(self):
		votingObj = dict()

		for congressman in self.voting.Deputado:
			name = congressman['Nome'].strip().encode('utf8', 'replace')
			vote = congressman['Voto'][0]
			votingObj[name] = positions[vote]

		return votingObj


votingToTSE = VotingToTSE( CSVReader(CONGRESS_TO_TSE_FILE).readLines() )

projects = CSVReader(PROJECTS_FILE).readLines()

n4j = Neo4jPersistence()

for project in projects:
	pType = project[0]
	pId = project[1]
	year = project[2]
	subject = project[3]
	description = project[4]
	n4j.createProjectNode(pType, pId, year, subject, description)

	fetcher = ProjectFetcher(project)
	fetcher.fetchContent()
	votingObj = fetcher.parseVoting() 

	for key, value in votingObj.iteritems():
		n4j.createVote(pId, subject, key, value)

