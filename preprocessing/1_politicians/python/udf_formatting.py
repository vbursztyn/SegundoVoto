#!/usr/bin/python
# -*- coding: utf-8 -*-


@outputSchema('output_str:chararray')
def removeQuotes(quotedStr):
	return quotedStr.replace('\"','')


@outputSchema('output_float:float')
def formatToFloat(floatStr):
	formattedFloat = None
	try:
		formattedFloat = float(floatStr.replace('\"','').replace(',', '.'))
	except ValueError:
		print 'Unable to convert to float: ' + str(floatStr)
		formattedFloat = 0.0
	return formattedFloat


@outputSchema('output_name:bytearray') # Of type 'bytearray' so to bypass encoding conflicts with 'chararray'
def formatName(nameByteArray):
	nameStr = nameByteArray.tostring().decode('latin-1') # Then we decode input file's bytearray to a Python string
	nameStr = nameStr.replace('\"','')
	formattedName = ''
	skipFormatting = [ 'DE', 'DA', 'DOS', 'DAS', 'NO', 'NA' ]
	for name in nameStr.split(' '):
		if name not in skipFormatting:
			formattedName = formattedName + ' ' + name.capitalize()
		else:
			formattedName = formattedName + ' ' + name.lower()
	return formattedName[1:]