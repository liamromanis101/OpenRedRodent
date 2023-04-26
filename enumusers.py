import cx_Oracle
from array import *
import multiprocessing
import os, re

locked = []
success = []

def enum_def_users(myip,myport,mysid,myaccount):

	try:
               	uid, passwd = re.split(',',myaccount)
		if not uid in success:
			if not uid in locked:
               			dsnStr = cx_Oracle.makedsn( myip, myport, mysid)
                		con = cx_Oracle.connect(user=uid.upper(), password=passwd.upper(), dsn=dsnStr)
       	        		print con.version
               			print "[+] Success %s:%s \n" % (uid,passwd)
				success.append("%s:%s" % (uid,passwd))
				return("%s:%s\n" % (uid,passwd))
               			con.close()
			else:
				return("0")
		else:
			return("0")
	except cx_Oracle.DatabaseError as e:
                error, = e.args
       	        if error.code == 12519:
               	        print "TNS:no appropriate service handler found"
                       	print "The listener could not find any available service handlers that are appropriate for the client connection"
			return("0")
               	if error.code == 1403:
                       	print "No rows returned. Error Code:", error.code
			return("0")
                if error.code == 28000:
       	                print "Account Locked: %s \n" % uid
			locked.append(uid)
			return("0")
               	if error.code == 1017:
               #       	print "invalid logon"
			return("0")
               	if error.code == 9275:
                       	print "CONNECT INTERNAL is no longer supported for DBA connections."
                        print "Please try to connect AS SYSDBA or AS SYSOPER."
			return("0")
		if error.code == 00000:
			print  "[+] Success %s:%s\n" % (uid,passwd)
			success.append(uid)
			return("%s:%s\n" % (uid,passwd))
		else:
			print "Error: %s" % error.code
			return("0")



def enumusers_helper(args):
    return enum_def_users(*args)

def enumstart(ip,port,sid):
	myusers = []
	result = []
	results = []
	print "Enumerating Default Users ...."

	with open('default_users-passwords.txt', "r") as ins:
		defaults = []
		for line in ins:
			line = line.replace("\n", "")
			defaults.append(line)


	number_of_processes = 4
	jobargs = [(ip,port,sid,user) for user in defaults]
	for result in multiprocessing.Pool(number_of_processes).map(enumusers_helper,jobargs):
		results.append(result)	

	print "users discovered:"
	for item in results:
		if item != "0":
			print item
			myusers.append(item[:-1])

	return myusers
	


