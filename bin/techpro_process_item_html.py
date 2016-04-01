#!/usr/bin/python

import time
import codecs
from xml.dom import minidom
import re
import collections
# import os
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.application import MIMEApplication
# from email.utils import formatdate

batch_name = raw_input('Enter the folder name containing the TechPro or BackStage batch to be analyzed\n(NOTE: the folder should be named in the format [tp/bs]_YYYYMMDD...): ')
batch_type = raw_input('Enter the batch type (i.e., new, corr, or pkgd): ')
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
current_timestamp = time.strftime('%B %d, %Y%t%I:%M:%S %p', time.localtime())

# INPUT FILE(S)
subm_xml = minidom.parse(batch_name+'/'+batch_name+'_'+batch_type+'_submission.xml')
subm_email = subm_xml.getElementsByTagName('email')[0].childNodes[0].nodeValue
firstname = subm_xml.getElementsByTagName('firstname')[0].childNodes[0].nodeValue
lastname = subm_xml.getElementsByTagName('lastname')[0].childNodes[0].nodeValue
subm_batch_name = subm_xml.getElementsByTagName('batch_name')[0].childNodes[0].nodeValue

batch_barcodes_file = codecs.open(batch_name+'/'+batch_name+'_'+batch_type+'_barcodes', 'r')
batch_barcodes_lines = batch_barcodes_file.readlines()
batch_barcodes_file.close()
batch_barcodes = []
for batch_barcode_line in batch_barcodes_lines:
	batch_barcode = batch_barcode_line.strip()
	batch_barcodes.append(batch_barcode)

item_xml_file_nyu50 = codecs.open(batch_name+'/'+batch_name+'_'+batch_type+'_item_xml_nyu50','r')
item_xml_file_nyu51 = codecs.open(batch_name+'/'+batch_name+'_'+batch_type+'_item_xml_nyu51','r')
item_xml_file_nyu52 = codecs.open(batch_name+'/'+batch_name+'_'+batch_type+'_item_xml_nyu52','r')
item_xml_str_all = item_xml_file_nyu50.read() + item_xml_file_nyu51.read() + item_xml_file_nyu52.read()
item_xml_file_nyu50.close()
item_xml_file_nyu51.close()
item_xml_file_nyu52.close()

# split the string of item record xml data into separate elements representing each item based on the XML delimiter tag <section-02>
item_recs = re.findall(r'<section-02>.*?</section-02>', item_xml_str_all, re.S)

# OUTPUT FILE(S)
all_items_analysis_file_html = codecs.open(batch_name+'/'+batch_name+'_'+batch_type+'_report.html', 'w')

item_fields_dict = {
	'<z13u-doc-number>': (0,'BSN'),
	'<z30-hol-doc-number>': (1,'Holdings doc number'),
	'<z30-doc-number>': (2,'Item doc number'),
	'<z30-item-sequence>': (3,'Item seq number'),
	'<z30-barcode>': (4,'Barcode'),
	'<z30-sub-library>': (5,'Sub-Library'),
	'<z30-collection>': (6,'Collection'),
	'<z30-temp-location>': (7,'Temp location'),
	'<z30-material>': (8,'Material type'),
	'<z30-item-status>': (9,'Item status'),
	'<z30-item-process-status>': (10,'Item process status'),
	'<z30-call-no-type>': (11,'Call num type (852 ind1)'),
	'<z30-call-no>': (12,'Call number'),
	'<z30-description>': (13,'Description'),
	'<z30-enumeration-a>': (14,'Enumeration-a'),
	'<z30-note-opac>': (15,'OPAC note'),
	'<z30-cataloger>': (16,'Cataloger'),
	'<z13u-user-defined-2>': (17,'Holdings data')
	}
	

#############################################################
##  Method:  get_field_data()
#############################################################
xml_start_tag_re = re.compile(r'<[zi][^>]*>')
xml_end_tag_re = re.compile(r'</.*>')	
def get_field_data(field_row):
	field_data = xml_start_tag_re.split(field_row)[1]
	field_data = xml_end_tag_re.split(field_data)[0]
	return field_data

#############################################################
##  Main Script
#############################################################
bsns_dict = {}	# stores BSNs as keys with corresponding HOL doc nums and item barcodes as nested dictionaries
bsns_all_list = []
hols_all_list = []
xml_barcodes_all_list = []

error = False
error_cnt = 0
item_cnt = 0
for item in item_recs:
	item_cnt += 1
	item_msg = ''
	item_fields = item.split('\n')
	
	# Get key field data for item
	for i in range(0, len(item_fields)):
		item_field = item_fields[i]
		if item_field.startswith('<z13u-doc-number>'):
			bsn = get_field_data(item_field)
			bsns_all_list.append(bsn)
		if item_field.startswith('<z30-hol-doc-number>'):
			hol_num = get_field_data(item_field)
			if not hol_num=='000000000':
				hols_all_list.append(hol_num)
		if item_field.startswith('<z30-barcode>'):
			xml_barcode = get_field_data(item_field)
			xml_barcodes_all_list.append(xml_barcode)
		if item_field.startswith('<z30-temp-location>'):
			tempLoc = get_field_data(item_field)
		if item_field.startswith('<z30-material>'):
			matType = get_field_data(item_field)
		if item_field.startswith('<z30-item-process-status>'):
			ips = get_field_data(item_field)
	
	# Check for ERRORs
	if hol_num=='000000000':
		item_msg += 'ERROR: Item needs HOLDINGS<br>'
	
	if tempLoc=='No' and not batch_mat=='sc':
		item_msg += 'ERROR: Temp Loc is NOT checked<br>'
	elif tempLoc=='Yes' and batch_mat=='sc':
		item_msg += 'ERROR: Temp Loc IS checked<br>'
	
	if batch_mat=='sc' and not matType=='':
		item_msg += 'ERROR: Mat Type is NOT SCORE<br>'
	
	if xml_barcode not in batch_barcodes:
		barcode_status = '<span style="color:red">NOT in batch</span>'
		item_msg += 'ERROR: '+xml_barcode+' may already be cataloged<br>'
	else:
		barcode_status = ''
	
	if batch_type=='new' and not ips=='Cataloging Hold - TechPro':
		item_msg += 'ERROR: Item IPS is NOT set to HP (Cat Hold-TP)<br>'
	elif batch_type=='pkgd' and not ips=='TechPro':
		item_msg += 'ERROR: Item IPS is NOT set to XM (TechPro)<br>'
	
	# Build nested dictionaries of item record numbers (BSN, Hol num, Barcode) and error messages
	if bsn not in bsns_dict:
		# add bsn/hol/barcode nums to dict
		bsns_dict[bsn] = {hol_num: {xml_barcode: (barcode_status, item_msg)}}
	else:
		# check if hol_num is in bsns dict
		hols_dict = bsns_dict[bsn]
		if hol_num not in hols_dict:
			# add hol/barcode nums to dict
			bsns_dict[bsn][hol_num] = {xml_barcode: (barcode_status, item_msg)}
		else:
			# check if barcode is in hols_dict
			barcodes_dict = hols_dict[hol_num]
			if xml_barcode not in barcodes_dict:
				bsns_dict[bsn][hol_num][xml_barcode] = (barcode_status, item_msg)
	
	if 'ERROR' in item_msg:
		error = True
		error_cnt += 1

not_in_aleph_cnt = 1
for batch_barcode in batch_barcodes:
 	if batch_barcode not in xml_barcodes_all_list:
 		bsns_dict['no bsn-'+str(not_in_aleph_cnt)] = {'no hol-'+str(not_in_aleph_cnt): {batch_barcode: ('<span style="color:red">NOT in Aleph</span>','ERROR: '+batch_barcode+' needs BIB<br>')}}
 		not_in_aleph_cnt += 1
 		error = True
 		error_cnt += 1

bsns_counter = collections.Counter(bsns_all_list)
hols_counter = collections.Counter(hols_all_list)
barcodes_counter = collections.Counter(xml_barcodes_all_list)
items_html_table = '<table style="border-collapse:collapse;" cellpadding=5>'
items_html_table += '<thead><tr style="border-bottom: 1pt solid black;"><th width="70">BSN</th><th width="70">HOL num</th><th width="130">Barcode</th><th width="70">Barcode<br>Status</th><th width="270">Notes/Errors</th></tr></thead><tbody>'
tr_cnt = 0
for bsn, hols_dict in bsns_dict.iteritems():
	mul_copy = False
	mul_vol = False
	fix_mul_vol = False
	if bsns_counter[bsn] > 1:
		bsn = '<span style="color:red">'+bsn+'<br>(mul_copy)</span>'
		bsn_dup = True
	else: bsn_dup = False
	
	all_barcode_statuses_on_bsn = []
	for hol in hols_dict.keys():
		for barcode in hols_dict[hol].keys():
			all_barcode_statuses_on_bsn.append(hols_dict[hol][barcode][0])
	for status in all_barcode_statuses_on_bsn:
		if 'NOT in batch' in status:
			fix_mul_vol = True
	
	for hol_num, barcodes_dict in hols_dict.iteritems():
		if hol_num=='000000000':
			hol_num = '<span style="color:red">'+hol_num+'<br>(unlinked)</span>'
		
		if hols_counter[hol_num] > 1:
			hol_num = '<span style="color:red">'+hol_num+'<br>(mul_vol)</span>'
			hol_dup = True
		else: hol_dup = False
		
		if bsn_dup and not hol_dup:
			mul_copy = True
		elif bsn_dup and hol_dup:
			mul_vol = True
				
		for barcode, value in barcodes_dict.iteritems():
			barcode_status = value[0]
			item_msgs = value[1]
			if mul_copy or fix_mul_vol:
				item_msgs += 'ERROR: Check mul-vol/copy<br>'
				error = True
				error_cnt += 1
			if mul_vol and not fix_mul_vol:
				item_msgs += 'OK - MUL-VOL but all items in batch<br>'
			# items_html_table += '<table style="border-collapse:collapse;" cellpadding=5>'
			items_html_table += '<tr style="border-bottom: 1px solid #ccc; vertical-align: top;"><td width="70">'+bsn+'</td><td width="70">'+hol_num+'</td>'
			items_html_table += '<td width="130">'+barcode
			if 'ERROR' in item_msgs:
				items_html_table += '<br><img src="http://www.barcodesinc.com/generator/image.php?code='+barcode+'&style=196&type=C128A&width=190&height=95&xres=1&font=3" border="0">'
			items_html_table += '</td>'
				
			# items_html_table += '<td width="200">'+barcode+'<br><img src="http://www.barcodesinc.com/generator/image.php?code='+barcode+'&style=196&type=C128A&width=190&height=95&xres=1&font=3" border="0"></td>'
			items_html_table += '<td width="70">'+barcode_status+'</td><td width="270">'+item_msgs+'</td></tr>'
# 			if tr_cnt==5 or (tr_cnt>5 and (tr_cnt-5)%7==0):
# 				items_html_table += '<p style="page-break-after:always;"></p>'
# 				items_html_table += '<table style="border-collapse:collapse;" cellpadding=5>'
# 				items_html_table += '<tr style="border-bottom: 1pt solid black;"><td width="70">BSN</td><td width="70">HOL num</td><td width="200">Barcode</td><td width="70">Barcode<br>Status</td><td width="200">Notes/Errors</td></tr></table>'
			tr_cnt += 1

items_html_table += '</tbody></table>'

all_items_header_html = '<html><head><style>@media print { thead {display: table-header-group;} }</style></head><body>'
# NOTE: the <style>@media print...</style> tag makes the table header display on each page when printing - works in Firefox, not in Chrome
all_items_header_html += '<h3>Outsource Cataloging - Batch Report</h3>'
all_items_header_html += '&nbsp;&nbsp;&nbsp;&nbsp;Vendor: <b>'+vendor+'</b><br>'
all_items_header_html += '&nbsp;&nbsp;&nbsp;&nbsp;Batch: <b>'+batch_name+'_'+batch_type+'</b><br>'
all_items_header_html += '&nbsp;&nbsp;&nbsp;&nbsp;Submitted: <b>'+str(len(batch_barcodes))+' barcodes / '+str(len(bsns_dict))+' BSNs</b><br>'
all_items_header_html += '&nbsp;&nbsp;&nbsp;&nbsp;Report produced: <b>'+current_timestamp+'</b><br>'
all_items_header_html += '&nbsp;&nbsp;&nbsp;&nbsp;Number of Items with Errors: <b>'+str(error_cnt)+'</b><br>'

all_items_analysis_file_html.write(all_items_header_html)
all_items_analysis_file_html.write(items_html_table)
all_items_analysis_file_html.write('</body></html>')
all_items_analysis_file_html.close()

print 'Batch: '+batch_name+'_'+batch_type
print 'Submitted: '+str(len(batch_barcodes))+' barcodes / '+str(len(bsns_dict))+' BSNs'
print 'Number of Items with Errors: '+str(error_cnt)

# email = MIMEMultipart()
# email['Subject'] = 'Processing Request for Outsourced Cataloging - Batch: '+batch_name
# from_email = 'hf36@nyu.edu'
# to_email = 'hf36@nyu.edu, '+subm_email
# email['From'] = from_email
# email['To'] = to_email
# email['Date'] = formatdate(localtime=True)
# 
# email_body = 'Dear '+firstname+' '+lastname+':\n'
# email_body += 'The report for batch '+subm_batch_name+' is attached.\n'
# if error:
# 	email_body += 'There are ERRORS found in the records which need to be corrected.  '
# 	email_body += 'Once all errors are fixed, please resubmit the updated file of BSNs/Barcodes.\n\n'
# else:
# 	email_body = 'NO errors were found in the records, so the batch can be processed for shipment to '+vendor+'.\n\n'
# email_body += 'Please contact Heidi Frank (hf36@nyu.edu) if you have any questions.\n'
# 
# email.attach(MIMEText(email_body, 'plain'))
# 
# curr_dir = os.path.dirname(os.getcwd())
# html_filename = batch_name+'_report.html'
# html_file_dir = curr_dir+'/TechPro/'+batch_name+'/'+html_filename
# 
# part = MIMEApplication(open(html_file_dir).read())
# part.add_header('Content-Disposition','attachment; filename="'+html_file_dir+'"')
# email.attach(part)
# 
# server = smtplib.SMTP('mail.nyu.edu', 25)
# #server.connect()
# server.sendmail(from_email, to_email, email.as_string())
# server.quit()

