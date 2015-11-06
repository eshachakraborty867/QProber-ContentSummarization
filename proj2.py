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

def readCacheClassif():
	return pickle.load(open('cache_classif.p', 'rb'))

def readCacheDocSample():
	return pickle.load(open('cache_docsample.p', 'rb'))

def readCacheLynx():
	return pickle.load(open('cache_lynx.p', 'rb'))

def writeCacheClassif(cache):
	pickle.dump(cache, open('cache_classif.p', 'wb'))

def writeCacheDocSample(cache):
	pickle.dump(cache, open('cache_docsample.p', 'wb'))

def writeCacheLynx(cache):
	pickle.dump(cache, open('cache_lynx.p', 'wb'))

def getNofPages(host, query, accountKey, cache):
	# Check if result is already computed
	if host in cache and ' '.join(query) in cache[host]:
		return cache[host][' '.join(query)]

	# If not, compute result
	bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + host + '%20' + '%20'.join(query) + '%27&$top=10&$format=Atom'
	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	content = response.read()
	
	root = ET.fromstring(content)
	entry = root.find('{http://www.w3.org/2005/Atom}entry')
	result = int(entry[4][0][1].text)

	# Add result to cache
	if host not in cache:
		cache[host] = {}
	cache[host][' '.join(query)] = result

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

def addTop4url(host, keywords, seen_set, accountKey):
	# Query Bing
	bingUrl ='https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?Query=%27site%3a' \
				+ host + '%20' + '%20'.join(keywords) + '%27&$top=10&$format=Atom'
	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	content = response.read()

	# Process result and Add document to document sample set 
	root = ET.fromstring(content)
	entries = root.findall('{http://www.w3.org/2005/Atom}entry')
	i = 0	
	while i < len(entries) and i < 4:
		url = entries[i][3][0][4].text
		if ~url.endswith('.PDF') and ~url.endswith('.PPT') and ~url.endswith('.pdf') and ~url.endswith('.ppt'):
			seen_set.add(url)
		i += 1

def documentSample(listdir, host, accountKey, cache):
	# Initialize empty sets of documents for each categories
	masterdict = [set({}) for directory in listdir]

	# For each directory and its sub-directory
	for i, directory in enumerate(listdir):

		# Check if documents sample has already been created
		if host in cache and directory in cache[host]:
			masterdict[i] = cache[host][directory]
			continue

		# Else
		try:
			f1 = open(directory + '.txt')
		except Exception:
			sys.exit('No such directory')

		# If root, add all children documents
		if directory == "root" and i > 0:
			for j in range(i):
				for elem in masterdict[j]:
					masterdict[i].add(elem)

		# Iterate over lines of file		
		for lines in f1:
			terms = lines.strip().split(" ")
			keywords = terms[1:]	
			# Get the top 4 URLs from Bing
			addTop4url(host, keywords, masterdict[i], accountKey)

		# Close file
		f1.close()

		# Add set to cache
		if host not in cache:
			cache[host] = {}
		cache[host][directory] = masterdict[i]

	return masterdict

def getLynxSet(buf):
	# Same implementation as the Java code provided
	try:
		end = buf.index('\nReferences\n')
	except ValueError:
		end = len(buf)
	recording = True
	wrotespace = False
	output = ''
	for i in range(end):
		if recording:
			if buf[i] == '[':
				recording = False
				if ~wrotespace:
					output += ' '
					wrotespace = True
				continue
			else:
				if buf[i].isalpha() and ord(buf[i]) < 128:
					output += buf[i].lower()
					wrotespace = False
				else:
					if ~wrotespace:
						output += ' '
						wrotespace = True
		else:
			if buf[i] == ']':
				recording = True
				continue
	return set([w for w in output.split(' ') if w != ''])

def contentSummary(listdir, masterdict, host, cache):
	for i, directory in enumerate(listdir):
		# Print
		print "\n\tSampling and summarizing category: " + directory
		printed = set({})

		# Initialize empty map
		countdict = defaultdict(int)

		# Iterate over URLs
		for index, url in enumerate(masterdict[i]):
			if index * 100/len(masterdict[i]) % 10 == 0 and index * 100/len(masterdict[i]) not in printed:
				print "\t... " + str((index * 100/len(masterdict[i])) + 10) + "% ..."
				printed.add(index * 100/len(masterdict[i]))
			if url in cache:
				for w in cache[url]:
					countdict[w] += 1
			else:
				try:
					f = os.popen('lynx -dump "' + url + '"')
					words = getLynxSet(f.read())
					cache[url] = words
					for w in words:
						countdict[w] += 1
				except:
					print "Problem with URL"
					continue
		# Write to file
		f2 = open(directory[0].upper() + directory[1:] + '-' + host + '.txt','w')
		for word,count in sorted(countdict.items()):
			f2.write(word + '#' + str(float(count)) + '\n')
		f2.close()

def visitedCategories(results):
	listdir = []
	for item in results:
		if "/" in item and item.split("/")[1].lower() not in listdir:
			listdir.append(item.split("/")[1].lower())
	listdir.append("root")
	return listdir

def main():
	# Open caches
	cache_classif = readCacheClassif()
	cache_docsample = readCacheDocSample()
	cache_lynx = readCacheLynx()

	# Handle options
	accountKey = sys.argv[1]
	t_es = float(sys.argv[2])
	t_c = int(sys.argv[3])
	host = sys.argv[4]

	# Classify host
	print "\nClassifying ...\n"
	results = classify('Root', host, t_es, t_c, 1, accountKey, cache_classif)
	print "\nClassification:\n\n\t" + ' and '.join(results) + '\n'

	# Write cache
	writeCacheClassif(cache_classif)

	# Create list of visited categories
	listdir = visitedCategories(results)

	# Create document sample for each visited category 
	print "\nSampling and summarizing ..."
	masterdict = documentSample(listdir, host, accountKey, cache_docsample)

	# Write cache
	writeCacheDocSample(cache_docsample)

	# Content summary construction
	contentSummary(listdir, masterdict, host, cache_lynx)
	print 

	# Write cache
	writeCacheLynx(cache_lynx)

	

if __name__ == "__main__":
	main()