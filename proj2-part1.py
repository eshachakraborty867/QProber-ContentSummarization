import xml.etree.ElementTree as ET
import urllib2
import base64
import pickle
from collections import defaultdict
import os,sys,subprocess
import re
import urllib
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
	# Initialize result
	result = []

	# Check if C is a leaf node
	if C not in CATEGORIES:
		return [C]

	# Calculate the ECovarage vector
	C_hat = probe(C, D, accountKey, cache)

	# Calculate the ESpecificity vector
	S_hat = {c: S_hat_parent*C_hat[c] / float(sum(C_hat.values())) for c in C_hat}
	print C_hat
	print S_hat

	# Go down the tree
	for ci in CATEGORIES[C]:
		if S_hat[ci] >= t_es and C_hat[ci] >= t_c:
			result += classify(ci, D, t_es, t_c, S_hat[ci], accountKey, cache)

	# Return results
	if len(result) == 0:
		return [C]
	else:
		return result


def main():
	# Open cache
	cache = readCache()

	# Handle options
	accountKey = sys.argv[1]
	t_es = float(sys.argv[2])
	t_c = int(sys.argv[3])
	host = sys.argv[4]

	# Classify host
	result = classify('Root', host, t_es, t_c, 1, accountKey, cache)
	print
	print result
	print

	# Write cache
	writeCache(cache)

if __name__ == "__main__":
	main()