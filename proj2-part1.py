import xml.etree.ElementTree as ET
import urllib, urllib2
import base64
import pickle
from collections import defaultdict
import os,sys,subprocess
import re
import json



CATEGORIES = {
	'Root': {'Root/Computers', 'Root/Sports', 'Root/Health'},
	'Root/Computers': {'Root/Computers/Hardware', 'Root/Computers/Programming'},
	'Root/Health': {'Root/Health/Fitness', 'Root/Health/Diseases'},
	'Root/Sports': {'Root/Sports/Basketball', 'Root/Sports/Soccer'}
}

def readCache():
	return pickle.load(open('cache.p', 'rb'))

def writeCache(cache):
	pickle.dump(cache, open('cache.p', 'wb'))

def getNofPages(site, query, accountKey, cache):
	# Check if result is already computed
	if site in cache and ' '.join(query) in cache[site]:
		return cache[site][' '.join(query)]

	# If not, compute result
	bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + site + '%20' + '%20'.join(query) + '%27&$top=10&$format=Atom'
	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	content = response.read()
	
	root = ET.fromstring(content)
	entry = root.find('{http://www.w3.org/2005/Atom}entry')
	result = int(entry[4][0][1].text)

	# Add result to cache
	if site not in cache:
		cache[site] = {}
	cache[site][' '.join(query)] = result

	# Return result
	return result

def probe(C, D, accountKey, cache):
	# Read classifier queries from file
	with open(C.split('/')[-1].lower() + '.txt', 'r') as f:
		read_data = f.read()
	queries = read_data.split('\n')

	# Compute ECoverage(C,D)
	C_hat = {c: 0 for c in CATEGORIES[C]}
	for c in C_hat:
		for query in queries:
			row = query.split(' ')
			if row[0] == c.split('/')[-1]:
				C_hat[c] += getNofPages(D, row[1:], accountKey, cache)
	return C_hat

def classify(C, D, t_es, t_c, S_hat_parent, accountKey, cache):

	print C
	# Initialize result
	result = []

	# Check if C is a leaf node
	if C not in CATEGORIES:
		return [C]

	# Calculate the ECovarage vector
	C_hat = probe(C, D, accountKey, cache)

	# Calculate the ESpecificity vector
	S_hat = {c: S_hat_parent*C_hat[c] / float(sum(C_hat.values())) for c in C_hat}

	# Print information
	for ci in C_hat:
		print "\tCoverage for category:    " + ci + " is " + str(C_hat[ci])
		print "\tSpecificity for category: " + ci + " is " + str(S_hat[ci])
		print

	# Go down the tree
	for ci in CATEGORIES[C]:
		if S_hat[ci] >= t_es and C_hat[ci] >= t_c:
			result += classify(ci, D, t_es, t_c, S_hat[ci], accountKey, cache)

	# Return results
	if len(result) == 0:
		return [C]
	else:
		return result

masterdict = defaultdict(set)
def getTop4url(directory, url, keywords, accountKey):
	url4 = []
	print "####################################"
	print directory, masterdict[directory]
	print "####################################"
	bingUrl ='https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?Query=%27site%3a' \
				+url+ '%20'+ '%20'.join(keywords)+'%27&$top=10&$format=Atom'
	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	#content contains the xml/json response from Bing.
	content = response.read()
	root = ET.fromstring(content)
	entries = root.findall('{http://www.w3.org/2005/Atom}entry')
	n = len(entries)
	i = 0
	
	while i < n and len(url4) < 4:
		url = entries[i][3][0][4].text
		if url.endswith('.PDF') or url.endswith('.PPT') or url.endswith('.pdf') or url.endswith('.ppt'):
			i += 1
			continue
		if url not in masterdict[directory]:
			url4.append(url)
			masterdict[directory].append(url)
		i += 1

	return url4

def summarize(listdir, url, accountKey):
	# For each directory and its sub-directory
	for directory in listdir:
		masterdict[directory] = []
		try:
			f1 = open(directory + '.txt')
		except Exception:
			sys.exit('No such directory')

		# countdict: our word dictionary
		countdict = defaultdict(int)
		print "Operating on : " + directory
		print ".................................."
		
		for lines in f1:
			# Get the top 4 URLs from Bing
			terms = lines.strip().split(" ")
			keywords = terms[1:]			
			url4  = getTop4url(directory, url, keywords, accountKey)

			print keywords

			for eachurl in url4:
				try:
					words = []
					# Fetch the content of the site
					f = os.popen('lynx -dump "' + eachurl + '"')
					for l in f.readlines():
						if l.strip():
							if l.split()[0]=="References":
								break
						l = re.sub(r'\[[^)]*\]', '', l)
						words = words + re.split("\W+|\d|_", l) 

						words = [x.lower() for x in words if x]
						words = list(set(words))
					for word in words:
						countdict[word] += 1
				except Exception:
					print "url not FOUND"
					continue

		f2 = open(directory + '-' +url+ '.txt','w')
		for word,count in sorted(countdict.items()):
			f2.write(word + '#' + str(count) + '\n')

		f1.close()
		f2.close()

def main():
	# Open cache
	cache = readCache()

	# Handle options
	accountKey = sys.argv[1]
	t_es = float(sys.argv[2])
	t_c = int(sys.argv[3])
	host = sys.argv[4]

	# Classify host
	print "\nClassifying ...\n"
	result = classify('Root', host, t_es, t_c, 1, accountKey, cache)
	print result
	print "\nClassification:\n\n\t" + ' and '.join(result) + '\n'

	# Content summary
	listdir = []
	for item in result:
		dirs = item.lower().split("/")
		for d in dirs:
			if d not in listdir:
				listdir.append(d)

	print listdir
	summarize(listdir, host, accountKey)

	# Write cache
	writeCache(cache)

if __name__ == "__main__":
	main()