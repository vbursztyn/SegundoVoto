--IMPORTANT: to be executed from bash file

REGISTER 'python/udf_formatting.py' USING org.apache.pig.scripting.jython.JythonScriptEngine AS customFormatting;

REGISTER 'python/udf_cnpj_test.py' USING org.apache.pig.scripting.jython.JythonScriptEngine AS customTests;

--Refer to raw_donations/LEIAME.pdf to details on metadata.
raw_donations = LOAD 'raw_donations/receitas_candidatos_2014_*.txt' USING PigStorage(';') AS (election_id, election_desc, timestamp, recipient_id, TSE_candidate_id:chararray, state:chararray, party:chararray, campaign_number, title:chararray, candidate_fullname:bytearray, candidate_id, electoral_receipt, document_number, donator_id, donator_name, donator_IRS_name, donator_state, donator_party_number, donator_candidate_number, donator_sector_id, donator_sector, donation_date, donation_value:chararray, donation_mean, donation_source, resource_type, resource_desc, original_donator_id:chararray, original_donator_name:bytearray, original_donator_type:chararray, original_donator_sector, original_donator_IRS_name);

--Refer to raw_candidates/LEIAME.pdf to details on metadata.
raw_candidates = LOAD 'raw_candidates/consulta_cand_2014_*.txt' USING PigStorage(';') AS (date, time, election_year, turn, election_desc, state_1, state_2, state_2_desc, title_id, title_desc, candidate_fullname, TSE_candidate_id:chararray, campaign_number, candidate_id, candidate_name:bytearray, campaign_status_id, campaign_status_desc, party_number, party, party_name, TSE_legend_id, legend, legend_composition, legend_name, occupation_id, occupation_desc, birth, electoral_id_candidate, age, gender_id, gender_desc, education_id, education_desc, marital_status_id, marital_status_desc, race_id, race_desc, nationality_id, nationality_desc, state_at_birth, city_at_birth_id, city_at_birth_desc, max_expense, status_id, status_desc, email);

--First application-related filter: congressmen only.
congressmen_only = FILTER raw_donations BY (title == '"Deputado Federal"');

--From the original data, select a few columns of interest.
extracted_columns_1 = FOREACH congressmen_only GENERATE customFormatting.removeQuotes(TSE_candidate_id) AS TSE_candidate_id, customFormatting.removeQuotes(state) AS state, customFormatting.removeQuotes(party) AS party, customFormatting.removeQuotes(title) AS title, customFormatting.formatName(candidate_fullname) AS candidate_fullname, (FLOAT) customFormatting.formatToFloat(donation_value) AS donation_value, customFormatting.removeQuotes(original_donator_id) AS original_donator_id, customFormatting.formatName(original_donator_name) AS original_donator_name, customFormatting.removeQuotes(original_donator_type) AS original_donator_type;

--Group donations by recipient campaign, so we can calculate each campaign's total.
grouped_by_campaign = GROUP extracted_columns_1 BY TSE_candidate_id;
total_donations = FOREACH grouped_by_campaign GENERATE group, SUM(extracted_columns_1.donation_value);

--From the original data, select a few columns of interest.
extracted_columns_2 = FOREACH raw_candidates GENERATE customFormatting.removeQuotes(TSE_candidate_id) AS TSE_candidate_id, customFormatting.formatName(candidate_name) AS candidate_name;

--Filter out all donations we can say for sure do not originate from companies.
filter_out_citizens = FILTER extracted_columns_1 BY (original_donator_type != 'F');

--Join with campaign data, so we can retrieve each candidate's campaign name.
joined_data_1 = JOIN filter_out_citizens BY TSE_candidate_id, extracted_columns_2 BY TSE_candidate_id;

--Join with campaign's total.
joined_data2 = JOIN joined_data_1 BY $0, total_donations BY $0;

--Filter out whoever filled "null" as donator type, but provided a company id.
final = FILTER joined_data2 BY customTests.isCnpj(original_donator_id);

STORE final INTO 'pig_output' USING PigStorage(',');