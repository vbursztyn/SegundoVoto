#!/usr/bin/python
# -*- coding: utf-8 -*-


class CSVReader():

	def __init__(self, path, separator=';'):
		self.path = path
		self.separator = separator


	def readLines(self):
		tokenizedLines = list()

		with open(self.path, 'r') as fIn:
			for line in fIn:
				tokens = line.replace('\n','').split(self.separator)
				if tokens[0][0] == '#':
					continue
				else:
					tokenizedLines.append(tokens)

		return tokenizedLines

