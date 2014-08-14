from setup import *
import articledata

def processResults(resultsdict, searchresults):
	try:
		if isinstance(resultsdict["IdList"]["Id"], basestring):
			resultsdict["IdList"]["Id"] = [resultsdict["IdList"]["Id"]]
		for res in resultsdict["IdList"]["Id"]:
			if res not in searchresults.keys():
				searchresults[res] = {}
			searchresults[res]["id"] = res
			searchresults[res]["grade"] = 0.0
			searchresults[res]["strength"] = 0.0
			searchresults[res]["meshdistance"] = 0.0
			title, abstract, date, meshterms, pubtypes = articledata.getData(res)
			searchresults[res]["title"] = title
			searchresults[res]["abstract"] = abstract
			searchresults[res]["date"] = date
			searchresults[res]["pubtypes"] = pubtypes
			searchresults[res]["meshterms"] = meshterms
			searchresults[res]["keywords"] = []	
	except TypeError:
		print "TypeError"
		print "Likely cause: no query results"
		print "Number of results: " + resultsdict["Count"]
	except KeyError:
		print "Keyerror"
		print "Likely cause: only one result"

	return searchresults