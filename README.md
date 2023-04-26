# OpenRedRodent
Oracle Database Scanner

Alpha version of this tool available for testing and any suggestions. It is crrently in Python 2.7, its old and hasn't been worked on for a long time. I will pick it up in due course to convert to Python3 and add new functionality. 

This tool attempts to enumerate SIDs and then failing that attempts to find them via SNMP. 

Assuming SIDs are enumerated the tool then attempts to enumerate valid users. It will also test for default username and password combinations. 

if access is gained with DBA privileges then the tool will try to dump all of the user hashes. 


