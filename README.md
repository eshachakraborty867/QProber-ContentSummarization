# QProber-ContentSummarization

#Content Summarization
This part of the project creates simple content summaries from Deep Web Databases. The content summary of a particular database consists of all words in the database and their corresponding frequencies.

Description of Content Summary Engine:
-------------------------------------
Part (a): Document Sampling
		  This is implemented in the function "getTop4url(url, keywords, accountKey)".
		  This function queries the bing API for the Deep Web Database (eg. 'url': daibetes.org), for the query (stored in keywords). It then returns the top 4 urls obtained from querying the Bing API.
		  Also in this part we have taken care to avoid returning any url that ends with '.pdf' or '.ppt'

Part (b): Content Summary Construction
		  After document sampling for each category node under which we classified a given database, this part implements a "topic content summary" associated with each such sample. The topic content summary contains a list of all the words that appear in the associated document sample, and their frequency in the document sample.

		  Our program prints each topic content summary to a text file, containing all the words in the sample -in dictionary order- together with their respective document frequencies. 

		  The text of a web page is extracted using the command "lynx --dump". After that we parse the obtained contents. Any text beyond 'References' if not considered. We have substituted any character that is not an English alphabet by a ' '(i.e. blank space). After that we have parsed the srtings to obtain words. To avoid case-sensitive issues, all parsed words are converted to lowercase.

		  We maintain a dictionary called 'countword' to store the frequency f each word. In the final step we are printing th sorted dictionary to a text file (eg Root-diabetes.org.txt).

Note
-----
1. We have processed each page that we retrieve before fetching the next page, in order to space our requests. 
2. Multiple-word information in the content summaries have not been included in our implementation
3. Our implementation does not output the <number of matches> field in the content summary.
