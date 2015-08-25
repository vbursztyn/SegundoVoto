#!/usr/bin/python
# -*- coding: utf-8 -*-

# Congress ETL configuration file. It provides:
# 1. A list of Legal Projects we may target;
# 2. An URL from which we may fetch voting data;
# 3. FROM VotingName TO TSEName: a dictionary that makes data integration possible.

PROJECTS_FILE = 'data/targeted_projects.csv'

CONGRESS_URL = 'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ObterVotacaoProposicao?tipo=%s&numero=%s&ano=%s'

CONGRESS_TO_TSE_FILE = 'data/voting_to_tse.csv'