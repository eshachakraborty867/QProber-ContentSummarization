import contentsummary

if __name__=="__main__":
	
	tc = raw_input("\n Enter the coverage threshold: \n")
	tc = float(tc)

	tc = raw_input("\n Enter the specificity threshold: \n")
	ts = float(ts)

	#QProber Implementation
	#generate listdir split by "/"
	#eg. root/health : listdir=['root', 'health']
	contentsummary.summarize(listdir,url)
