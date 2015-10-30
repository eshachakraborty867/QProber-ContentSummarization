from collections import defaultdict
import os,sys,subprocess
import re
import urllib
import json

def getTop4url(query):
	url = "http://api.bing.net/json.aspx?AppId=" + "7Mtcdr7rWaH+3i2WOB4KaKZbAVdwptuX6dG/m7EBCz8" + "&Version=2.2&Market=en-US&Query=" + query + "&Sources=web&Web.Count=20&JsonType=raw"
	temp = urllib.urlopen(url)
	
	url4 = []
	return url4


def summarize(listdir, url):
	for directory in listdir:
		try:
			f1 = open(directory + '.txt','r')
		except Exception:
			sys.exit('No such directory')

	countdict = defaultdict(int)

	for lines in f1:
		terms = line.strip().split(" ")
		keywords = '+'.join(terms[1:])

		url4  = getTop4url(url + keywords)

		for eachurl in url4:
			newproc = subprocess.Popen(['lynx','-dump',url], stdout=subprocess.PIPE)
			data, err 	= fetchProcess.communicate()
			ref = data.find('\nReferences\n')
			before_ref = data[:refPoint].lower()

			wordlist = re.findall('[a-z]+',before_ref)

			for word in wordList:
				countdict[word] += 1


