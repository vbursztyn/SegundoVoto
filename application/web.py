#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, request, render_template


from werkzeug.datastructures import ImmutableMultiDict


from persistence import MongoPersistence


app = Flask(__name__)


@app.route('/')
def viewHome():
	mdb = MongoPersistence('interface')
	interfaceItems = mdb.getInterface()
	mdb.close()

	return render_template('home.html', items=interfaceItems)


@app.route('/results', methods=['POST'])
def processVotes():
	formVotes = request.form	
	validUserVotes = dict()

	for project, position in formVotes.iteritems():
		if position not in [ u'SIM', u'NÃO' ]:
			continue
		validUserVotes[project] = position

	allResults = getResults(validUserVotes)
	condensedResults = processResults(allResults)

	return str(condensedResults[:30])


def getResults(validUserVotes):
	mdb = MongoPersistence('results')
	allResults = dict()

	oppositePosition = { u'SIM': u'NÃO', u'NÃO': u'SIM' }

	for project, position in validUserVotes.iteritems():
		tokens = project.split('-')
		pType = tokens[0]
		pId = tokens[1]
		year = tokens[2]
		subject = tokens[3]

		allResults[project] = mdb.getResult(pType, pId, year, subject, oppositePosition[position])

	mdb.close()
	return allResults


def processResults(allResults):
	condensedResults = dict()

	for project, result in allResults.iteritems():
		for company, score in result.iteritems():
			if company not in condensedResults:
				condensedResults[company] = score
			else:
				condensedResults[company] += score

	condensedResults = sorted(condensedResults.items(), key=lambda x: x[1], reverse=True)
	return condensedResults


if __name__ == "__main__":
	app.run(debug=True)