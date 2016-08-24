#!/usr/bin/python

import os
import pymarc
from pymarc import Record, Field

#curr_dir = os.path.dirname(os.getcwd())
#parent_dir = os.chdir("..")

batch_name = 'tp_20160303_bk_ara_171r'
batch_dir = '../submissions/TechPro/'+batch_name+'/'

#INPUT Files
orig_marc_recs = pymarc.MARCReader(file(batch_dir + batch_name + '_pkgd_marc_final.mrc'), to_unicode=True, force_utf8=True)
curr_marc_recs = pymarc.MARCReader(file(batch_dir + 'loaded_to_aleph/ret_20160707_25r/' + batch_name + '_ret_20160707_25r_bsns.mrc'), to_unicode=True, force_utf8=True)

orig_recs_dict = {}
for orig_rec in orig_marc_recs:
	orig_bsn = orig_rec.get_fields('001')[0].value()
	orig_recs_dict[orig_bsn] = orig_rec

bsns_changed = open('bsns_changed.txt', 'w')
bsns_changed.write('BATCH: '+batch_name+'\n--------------------------------------------\n--------------------------------------------\n')

for curr_rec in curr_marc_recs:
	curr_rec.remove_fields('FMT')
	curr_bsn = curr_rec.get_fields('001')[0].value()
	if orig_recs_dict.has_key(curr_bsn):
		
		curr_marc_fields = curr_rec.get_fields()
		curr_tags = []
		for curr_marc_field in curr_marc_fields:
			curr_tags.append(curr_marc_field.tag)
		
		orig_marc_fields = orig_recs_dict[curr_bsn].get_fields()
		orig_tags = []
		for orig_marc_field in orig_marc_fields:
			orig_tags.append(orig_marc_field.tag)
		
		if not curr_tags == orig_tags:
			diff_tags = set(curr_tags) - set(orig_tags)
			diff_tags = sorted(diff_tags)
			print 'BSN '+curr_bsn+' has changed!'
			print 'Original fields: ' + str(orig_tags)
			print 'Current fields: ' + str(curr_tags)
			print 'DIFFERENCE: ' + str(diff_tags)
			print '--------------------------------------------'
			bsns_changed.write('BSN '+curr_bsn+' has changed:\n')
			bsns_changed.write('Original fields: ' + str(orig_tags) + '\n')
			bsns_changed.write('Current fields: ' + str(curr_tags) + '\n')
			bsns_changed.write('DIFFERENCE: ' + str(diff_tags) + '\n')
			bsns_changed.write('--------------------------------------------\n')
	
	else:
		print 'BSN '+curr_bsn+' NOT FOUND in file of original MARC records.'

