#!/bin/bash

echo "Script for loading Outsource Cataloging vendor records (TechPro and BackStage)"
echo ""
ls -l /exlibris/aleph/u22_2/nyu01/scratch/outsrc_cat*.mrc
echo ""
echo "Enter email address to notify: "
read emsub
emsub1=$emsub
echo ""
echo "Enter base name of vendor input file WITHOUT EXTENSION (MRC): "
read fname1
echo "File name entered is $fname1"
fname2=$fname1
cd $aleph_proc
pwd
rm oclctploadrpt
# break 
csh -f p_file_01 NYU01,$fname2.mrc,$fname2.in,04,
csh -f p_file_02 NYU01,$fname2.in,$fname2.q,01,
csh -f p_manage_37 NYU01,ALEPH_SEQ,$fname2.q,000000000,000000000,$fname2.qfixed,OCLCT,N,FRANKH,OCLCTP,20,
csh -f p_manage_36 NYU01,$fname2.qfixed,$fname2.new,$fname2.unq,$fname2.mul,DB001,977,
if [ -s "/exlibris/aleph/u22_2/nyu01/scratch/$fname2.new" ]
  then
  echo "Record not found- " > oclctploadrpt
  egrep ' 001| 245| 250| 260| 300' /exlibris/aleph/u22_2/nyu01/scratch/$fname2.new >> oclctploadrpt
fi
csh -f p_manage_18 NYU01,$fname2.unq,$fname2.reject,$fname2.log,OLD,,,FULL,MERGE,M,,OCLCTP806,OCLCTP,20,
echo "Outsource Cataloging $fname2 file loaded" >> oclctploadrpt
cat /exlibris/aleph/u22_2/alephe/scratch/$fname2.log >> oclctploadrpt
wc -l /exlibris/aleph/u22_2/alephe/scratch/$fname2.log >> oclctploadrpt
mailx -s "Outsource Cataloging records loaded- $fname2" aleph.notifications-group@nyu.edu,$emsub1 -- -f aleph.notifications-group@nyu.edu < oclctploadrpt
echo "Base filename is $fname2"
ls -lt /exlibris/aleph/u22_2/alephe/scratch/$fname2*
pwd
cat oclctploadrpt
echo "This Outsource Cataloging load is done."
