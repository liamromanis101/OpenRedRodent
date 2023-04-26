#!/usr/bin/python
#connect prototype

import cx_Oracle
from array import *
import multiprocessing
import os

def enumsids( ip, port, sid ):
	try:
       		dsnStr = cx_Oracle.makedsn(ip, port, sid)
        	con = cx_Oracle.connect(user="cannot", password="exist", dsn=dsnStr)
       		con.close()
	except cx_Oracle.DatabaseError as e:
		error, = e.args
		if error.code == 12519:
        	        print "\n[-]TNS:no appropriate service handler found"
         		print "[-]The listener could not find any available service handlers that are appropriate for the client connection"
			time.sleep(2)
			return("0")	
			con.close()
		if error.code == 1403:
			print "No rows returned. Error Code:", error.code  
			return("0")
			con.close()
		if error.code == 1017:
			print "Found: ", sid
			return(sid)
			con.close()
		if error.code == 12505:
			return("0")
			con.close()
		if error.code == 1034:
			return("0")
			con.close()
		else:
			return("0")
			con.close()

def enumsids_helper(args):
    return enumsids(*args)

def startenum(ip,port):
	mysids = []
	with open('sid.txt', "r") as ins:
		sids = []
		for line in ins:
			sids.append(line)

	number_of_processes = 2
	jobargs = [(ip,port,sid) for sid in sids]
	results = multiprocessing.Pool(number_of_processes).map(enumsids_helper,jobargs)
	outputs = [result[0] for result in results]
	result.join(outputs)

	for item in results:
		if "0" not in item:
			print item
			mysids.append(item[:-1])


	if len(mysids) > 0:
		return mysids
	else:
		print "No SIDs Found :("
		os._exit(1)
