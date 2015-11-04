from collections import defaultdict
import os,sys,subprocess
import re
import urllib
import json

def getTop4url(query):
	bingurl = "https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?" + query + "=%27site%3afifa.com%20premiership%27&$top=10&$format=Atom"
	response = urllib.urlopen(url)
	content = response.read()
	##parse to get the results		TODO

	url4 = []
	i=0
	while len(url4) < 4:
		#url = content [i]			TODO
		if url.endswith('pdf') or url.endswith('ppt'):
			continue
		else:
			url4.append(url)
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


					for word in wordlist:
						countdict[word] += 1

			f2 = open('sample-' + directory + '.txt','w')
			for word,count in sorted(countdict.items()):
				f2.write(word + '#' + str(count) + '\n')

			f1.close()
			f2.close()

		except Exception:
			sys.exit('No such directory')


