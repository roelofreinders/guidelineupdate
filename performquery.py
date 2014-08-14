from setup import *
import querybuilder
import xmltodict
retmax = 1000
# construct query of appropriate level
# start with broadest level, then narrow down depending on number
# of results
def searchByCombination(primaryterms, secondaryterms, minresults=10, 
		earlyyear=0, lateyear=3000):

	level = 4
	nr_of_results = -1

	while ((nr_of_results < minresults) and (level > 0)):
		query = querybuilder.buildQuery(primaryterms, secondaryterms, level, \
			 earlyyear, lateyear)
		#print query
		resp, content = h.request(baseURL + \
			"esearch.fcgi?db=pubmed&retmode=xml&sort=relevance&" + \
			"retmax=" + str(retmax) + "&term=" + query.replace(" ", "+"))
		resultsdict = xmltodict.parse(content)["eSearchResult"]
		try:
			nr_of_results = int(resultsdict["Count"])
		except KeyError:
			print "KeyError"
			nr_of_results = 0
		print "Number of results for level %i: %i" \
			% (level, nr_of_results)
		level -= 1

	return query, resultsdict, nr_of_results

def searchByTerms(terms, minresults=10, earlyyear=0, lateyear=3000):
	sortedterms = mb.sortImportance(terms)
	nr_of_results = 0
	while ((nr_of_results < minresults) and (len(sortedterms) > 0)):
		query = querybuilder.buildQuery(sortedterms, [], 4, earlyyear, lateyear)
		resp, content = h.request(baseURL + \
			"esearch.fcgi?db=pubmed&retmode=xml&sort=relevance" + \
			"&retmax=" + str(retmax) + "&term=" + \
			query.replace(" ", "+"))
		resultsdict = xmltodict.parse(content)["eSearchResult"]
		nr_of_results = int(resultsdict["Count"])
		print "Number of results for %i terms: %i" \
			% (len(sortedterms), nr_of_results)
		sortedterms.pop()
	return query, resultsdict, nr_of_results