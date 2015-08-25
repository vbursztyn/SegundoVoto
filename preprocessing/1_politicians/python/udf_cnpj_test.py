#!/usr/bin/python
# -*- coding: utf-8 -*-


@outputSchema('output_cnpj_test:boolean')
def isCnpj(idToTest):
	if len(idToTest) > 11: #123.456.789-01 -> length 11
		return True
	return False