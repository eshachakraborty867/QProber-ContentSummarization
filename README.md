# QProber-ContentSummarization



TEAM
======
Alice Berard (aab2227)
Esha Chakraborty (ec3074)


Files we are submitting
=========================
- proj2.py (our main implementation)
- cache_classif.p (pickle object containing our cached results)
- cache_docsample.p (idem)
- cache_lynx.p (idem)
- root.txt, health.txt, computers.txt, sports.txt (the provided files containing queries)


To run the program
===================
python proj2.py <BING_ACCOUNT_KEY> <t_es> <t_ec> <host>

Note: If the results are not in the cache, please allow about 5 minutes to the sampling and summarization steps to run.
You should see a percentage indicating you how much of the category is already processed.


Bing Account Search Key
========================


Description
=============

# Database Classification

This is implemented in the following functions:
	- classify(C, D, t_es, t_c, S_hat_parent, accountKey, cache)
	- probe(C, D, accountKey, cache)
	- getNofPages(host, query, accountKey, cache)

The algorithm follows closely the one described in the QProber paper. It recursively calls the classify function until the category either is a leaf, or no longer exceeds the target specificity and/or coverage.

getNofPages: This function returns the number of matches on the given host for the given query.

probe: This function returns the ECoverage vector estimated by issuing queries to the Bing API using the function getNofPages.

classify: This functions recursively classifies a given database, for a given category node, using t_es and t_c as well as the parent ESpecficity.

In order to avoid querying the Bing API for the same information queries after queries, we implemented a cache system. The cache is a Python dictionary where the keys are the host names (yahoo.com, fifa.com, etc.) and the values are again dictionaries, where keys are the queries and value is an integer corresponding to the number of hits for this query on this host. 
This cache is stored in the pickle object cache_classif.p


# Document Sampling

This is implemented in the following functions:
	- documentSample(listdir, host, accountKey, cache)
	- addTop4url(host, keywords, seen_set, accountKey)

addTop4url: This function queries the bing API for the Deep Web Database as entered by the user for the value for <host> (eg. 'url': diabetes.org), for the query (stored in 'keywords'). It then adds the top 4 URLs obtained from querying the Bing API to the set of URLs already seen for this category node. Also in this part we have taken care to avoid returning any url that ends with '.pdf' or '.ppt'.

documentSample: This function creates a document sample (represented as a Python set) for each category node that we have traversed. We take care to add all the documents already seen in the children categories when going up to the parents (i.e. to the root).
To make sure that we are processing first the children, and then the root, we created an array called listdir that has all the category nodes for which we have to create a document sample ORDERED from children to root. Thus when we process the root, we are sure that we have already processed its children and we can add their document sampls to the root's one. Then, for each query in the current node, we cann the function addTop4url to add the Top-4 retrieved URLs to the set. The function returns a list of sets. There's one set per category node processed.

Again, we have used a cache system for this part, such that we don't query the Bing API for a given host and query if we have already done so. The structure of the cache is almost identical to the previous one, and it is stored in the pickle object cache_docsample.p


# Content Summarization

This part of the project creates simple content summaries from Deep Web Databases. The content summary of a particular database consists of all words in the database and their corresponding frequencies.

This is implemented in the following functions:
	- contentSummary(listdir, masterdict, host, cache)
	- getLynxSet(buf)

contentSummary: After document sampling, for each category node under which we classified a given database, this part implements a "topic content summary" associated with each such sample. The topic content summary contains a list of all the words that appear in the associated document sample, and their frequency in the document sample.
Our program prints each topic content summary to a text file, containing all the words in the sample -in dictionary order- together with their respective document frequencies. 

getLynxSet: The text of a web page is extracted using the command "lynx --dump". After that we parse the obtained contents. Any text beyond 'References' is not considered. We have substituted any character that is not an English alphabet by a ' '(i.e. blank space). After that we have parsed the strings to obtain words. To avoid case-sensitive issues, all parsed words are converted to lowercase.
We maintain a dictionary called 'countword' to store the frequency of each word. In the final step we are printing the sorted dictionary to a text file (eg Root-diabetes.org.txt).

Again, we have used a cache system, even if this part does not require to call the Bing API. This is because the "lynx --dump" command can take some time, so we found that it was more convenient to use a cache also.


Notes
-----
1. We have processed each page that we retrieve before fetching the next page, in order to space our requests. 
2. Multiple-word information in the content summaries have not been included in our implementation
