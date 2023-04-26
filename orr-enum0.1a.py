#!/usr/bin/python
#Main prototype
#Author: Liam Romanis

import cx_Oracle
import sys, getopt, os
from array import *
import re
import time
import enumsids, enumusers, getHashes

def help():
    	print ('orr_enum.py -i <target ip>  -p <port> ')
        print "Target IP: Target Host by IP"
        print "Port: TCP Port Number of the TNS Listener"
        sys.exit(2)

def opts(argv):
    myip = ''
    myport = ''
    try:
        opts, args = getopt.getopt(argv, 'i:p:h', ['ip=','port=','help'])
    except getopt.GetoptError:
    	print ('orr_enum.py -i <target ip>  -p <port> ')
        os._exit(1)
    for opt, arg in opts:
        if opt == '-h':
        	help()
        	sys.exit()
        elif opt in ('-i', '--ip'):
        	myip = arg
        elif opt in ('-p', '--port'):
        	myport = arg
        else:
	        print ('orr_enum.py -i <target ip>  -p <port> ')
        	os._exit(1)

    return myip, myport

def snmp_enum(myip):
	print "Querying SNMP for SIDs"
	from easysnmp import Session
	retsids=[]
	with open('dict.txt', "r") as ins:
        	communities = []
        	for line in ins:
                	line = line.replace("\n", "")
                	communities.append(line)


	for comm in communities:
        	try:
                	# Create an SNMP session to be used for all our requests
               		session = Session(hostname=myip, community=comm, version=2)

                	# You may retrieve an individual OID using an SNMP GET
                	process_paths = session.walk('1.3.6.1.2.1.25.4.2.1.4')

                	# Each returned item can be used normally as its related type (str or int)
                	# but also has several extended attributes with SNMP-specific information
                	for item in process_paths:
                        	process = '{value}'.format(value=item.value)
                        	if 'q000' in process:
                                	mysid, blah, blah2 = re.split('_', process)
                                	print "SID:%s" % mysid.upper()
					retsids.append(mysid.upper())
        	except:
                	pass
	
	print len(retsids)
	return retsids

def IsDBA(myip,myport,mysid,correct,DBA):
	for account in correct:
		#print account
        	uid, passwd = re.split(':', account)

	        try:
        	        dsnStr = cx_Oracle.makedsn( myip, myport, mysid)
                	con = cx_Oracle.connect(user=uid.upper(), password=passwd.upper(), dsn=dsnStr)
	                print con.version
        	        query = "set role dba"
                	mycur = con.cursor()
	                mycur.execute(query)
			con.close()
	        except cx_Oracle.DatabaseError as e:
        	        error, = e.args 
			if error.code == 1924:
				print "role 'DBA' not granted or does not exist"
				return
			if error.code == 1017:
				print "User: %s is NOT DBA" % uid
				return
			else:
				print "User: %s is DBA - !GAME OVER!.... almost" % uid
				DBA.append(account)
				#getHashes

	return DBA



def getprivs(myip,myport,mysid,right):
	priv = "ANY"
	uid, passwd = re.split(':', right)
	print "Enumerating Privs for USER: %s.\n" %  uid

	try:
		dsnStr = cx_Oracle.makedsn( myip, myport, mysid)
                con = cx_Oracle.connect(user=uid.upper(), password=passwd.upper(), dsn=dsnStr)
                print con.version
		mycur = con.cursor()
                print "SESSION_PRIVS:"
		query4 = "select  privilege from SESSION_PRIVS"
                mycur.execute(query4)
                for result in mycur:
			if priv in str(result):
				print "%s - Potential Priviliege Escalation Vector!" % result
			else:
                        	print "%s" % result
		mycur2 = con.cursor()
                print "SESSION_ROLES:"
         	query5 = "select  privilege from SESSION_ROLES"
		mycur2.execute(query5)
                for result in mycur:
                        print result
        	con.close()
        except cx_Oracle.DatabaseError as e:
                error, = e.args
		if error.code == 904:
			print "No roles assigned to User: %s" % uid
                #print "Error: %s" % error.code
                pass




if __name__ == "__main__":
	myip, myport= opts(sys.argv[1:])
	mysids = []
	snmpsids = []
	success = []
	correct = []
	DBA = []
	isdba = []

	print "Enumerating Common SIDs"
	retsid = []
	
	mysids = enumsids.startenum(myip, myport)
	if len(mysids) < 1:
		snmpsids = snmp_enum(myip)
		print "Number of SIDs identified from SNMP: %s\n" % len(mysids)

		for sid in snmpsids:
			if not sid in mysids:
				mysids.append(sid)

	if len(mysids) > 0:
		for sid in mysids:
			print "\nEnumerating Users in Database Instance %s\n" % sid
			correct = enumusers.enumstart(myip,myport,sid)
			if len(correct) > 0:
				print "\nThe following valid username and password combinations were detected\n"
				for right in correct:
					print "%s." % right
			else:
				os._exit(1)
		
		print "\Testing if accounts are DBA\n"
		isdba = IsDBA(myip,myport,sid,correct,DBA)
#		if len(DBA) > 0: 
#			right = DBA[0]
#			print "\nEnumerating Identified Users' Privileges as DBA\n"
#			getprivs(myip,myport,sid,right)
#		else:
		print "\nEnumerating Identified Users' Privileges using account privileges\n"
		for right in correct:
			getprivs(myip,myport,sid,right)
	else:	
		print "No SIDs identified - BOO!\n"
