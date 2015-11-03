from collections import defaultdict
import os,sys,subprocess
import re
import urllib
import json

def getTop4url(query):
	bingurl = "http://api.bing.net/json.aspx?AppId=" + "7Mtcdr7rWaH+3i2WOB4KaKZbAVdwptuX6dG/m7EBCz8" + "&Version=2.2&Market=en-US&Query=" + query + "&Sources=web&Web.Count=20&JsonType=raw"
	response = urllib.urlopen(url)
	content = response.read()

	url4 = []

	return url4


def summarize(listdir, url):
	for directory in listdir:
		try:
			f1 = open(directory + '.txt')
			countdict = defaultdict(int)
			countdoc  = defaultdict(int)

			for lines in f1:
				terms = lines.strip().split(" ")
				keywords = '+'.join(terms[1:])

				url4  = getTop4url(url + keywords)

				for eachurl in url4:
					newproc = subprocess.Popen(['lynx','-dump',url], stdout=subprocess.PIPE)
					data, err 	= newproc.communicate()
					ref = data.find('\nReferences\n')
					before_ref = data[:ref].lower()
					wordlist = re.findall('[a-z]+',before_ref)

					if word in wordlist:
						countdoc[word] += 1

					for word in wordlist:
						countdict[word] += 1

			f2 = open('sample-' + directory + '.txt','w')
			for word,count in sorted(countdict.items()):
				f2.write(word + '  ' + str(count) + '  ' + str(countdoc[word])+ '\n')

			f1.close()
			f2.close()

		except Exception:
			sys.exit('No such directory')


