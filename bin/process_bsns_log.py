#!/usr/bin/python

import os
import time
import csv
import pymarc
from pymarc import Record, Field
import operator

#current_timestamp = time.strftime('%B %d, %Y%t%I:%M:%S %p', time.localtime())
current_timestamp = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
print current_timestamp

process = raw_input('Enter the process (e.g., add new batch, send to vendor, return from vendor, load to Aleph): ')
batch_name = raw_input('Enter the batch name (e.g., tp_20160121_bk_gre_14r): ')
vendor_code = batch_name.split('_')[0]
if vendor_code == 'tp':
	vendor = 'TechPro'
elif vendor_code == 'bs':
	vendor = 'BackStage'
else:
	vendor = 'NOTE:  Not Assigned'
batch_date = batch_name.split('_')[1]
batch_mat = batch_name.split('_')[2]
language = batch_name.split('_')[3]
batch_rec_cnt = batch_name.split('_')[4]
batch_rec_cnt = int(batch_rec_cnt[:-1])
parent_dir = os.path.dirname(os.getcwd())
batch_folder = parent_dir+'/submissions/'+vendor+'/'+batch_name+'/'

bsns_lines = []
# Read all current data from the bsns_log.csv file
bsns_csv_file_in = open(parent_dir+'/bsns_log.csv', 'rb')
bsns_log_in = csv.reader(bsns_csv_file_in)
bsns_lines.extend(bsns_log_in)
bsns_csv_file_in.close()

# Method: Add new batch of BSNs to log file
if process == 'add new batch':
	new_bsns_file = open(batch_folder+batch_name+'_new_bsns', 'r')
	new_bsns = new_bsns_file.readlines()
	for new_bsn in new_bsns:
		new_row = [new_bsn.rstrip(),batch_name,'',current_timestamp,'','','']
		bsns_lines.append(new_row)

	
# Method: Add status date for when BSNs are processed and "sent to vendor"
if process == 'send to vendor':
	final_marc_recs = pymarc.MARCReader(file(batch_folder+batch_name+'_pkgd_marc_final.mrc'), to_unicode=True, force_utf8=True)
	for f_marc_rec in final_marc_recs:
		f_marc_rec_001 = f_marc_rec.get_fields('001')[0].value() + 'NYU01'
		for line in bsns_lines:
			if line[0] == f_marc_rec_001:
				line[4] = current_timestamp

# Method: Match returned file of vendor BSNs and add status date for when BSNs are processed as "returned from vendor" or as "loaded to Aleph"
if process == 'return from vendor' or process == 'load to Aleph':
	batch_filenames = os.listdir(batch_folder)
	for filename in batch_filenames:
		if filename.endswith('.mrc'):
			print filename
	vendor_filename = raw_input('Enter the vendor .mrc filename for this batch: ')
	vendor_marc_recs = pymarc.MARCReader(file(batch_folder+vendor_filename), to_unicode=True, force_utf8=True)
	for v_marc_rec in vendor_marc_recs:
		v_marc_rec_001 = v_marc_rec.get_fields('001')[0].value() + 'NYU01'
		for line in bsns_lines:
			if line[0] == v_marc_rec_001:
				if process == 'return from vendor':
					line[2] = vendor_filename
					line[5] = current_timestamp
				elif process == 'load to Aleph':
					line[6] = current_timestamp

bsns_lines_header = bsns_lines.pop(0)
bsns_lines_sorted = sorted(bsns_lines, key=operator.itemgetter(6, 5, 4, 3, 1))
for line in bsns_lines_sorted:
	print line

# Write out lines to bsns_log.csv file, replacing rows with updated statuses
bsns_csv_file_out = open(parent_dir+'/bsns_log.csv', 'wb')
bsns_log_out = csv.writer(bsns_csv_file_out)
bsns_log_out.writerow(bsns_lines_header)
bsns_log_out.writerows(bsns_lines_sorted)
bsns_csv_file_out.close()



