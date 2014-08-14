from setup import *
import parserecommendation
import processevidence
import articledata
import meshbrowser
import querybuilder

# set which recommendation should be used
c = 24


recommendation = recommendations[c]
evidence = evidence_ids[c]
goals = goal_ids[c]



# Final result: query suggested by the system
query = ""

# Create output intro
out = open("results.html", "w")
out.write("""<html>
<head>
	<title>PubMed query results</title>
</head>
<body>""")
out.write("<h1>Results</h1>")
out.write("<h3>recommendation</h3>")
out.write(recommendation)
out.write("<h3>Input papers</h3>")
for id in evidence:
	out.write("<a href=\"" + pubURL + id + "\">" + id + "</a><br />")


related = []

#-------------------------------------------------#
# PART 1: processing text from the recommendation #
#-------------------------------------------------#

# clean up the recommendation string
recommendation = parserecommendation.cleanString(recommendation)

# send to PubMed to see if terms are recognized
recommendationterms = parserecommendation.getMeSHTerms(recommendation)

# remove duplicate terms
recommendationterms = list(set(recommendationterms))

# create list of 'major terms' for evaluation
majorterms = []

# extract MeSH terms
for term in recommendationterms:
	for token in term.split(" OR "):
		if "MeSH" in token:
			majorterms.append(token.split("\"")[1])




#------------------------------------------------------------------#
# PART 2:
# get MeSHterms from all articles in evidence list (variable evidence)
# TODO: subheadings
#------------------------------------------------------------------#

# results dictionary
terms = processevidence.buildMeSHDict(evidence)
"""
# create list of 'major terms' for evaluation
for term in terms.keys():
	if terms[term]["major"] >= 1 or terms[term]["count"] >= (len(evidence) - 1):
		majorterms.append(term.lower())
"""

# Remove MeSH terms that don't exist in the tree
if "female" in majorterms: majorterms.remove("female")
if "male" in majorterms: majorterms.remove("male")
if "humans" in majorterms: majorterms.remove("humans")

out.write("<h3>Major MeSH terms</h3>")
out.write(str(majorterms))
# add the terms that occur in every article			
query2 = ""

# if there is only one article, just extract the 'major' topics
# otherwise, conjunct all terms that occur in at least (#evidence - 1) articles
primaryterms = []
secondaryterms = []
if len(evidence) == 1:
	for term in terms:
		if terms[term]["major"] >= 1:
			primaryterms.append(("(\"" + term + "\"[MeSH Terms] OR \"" + term + "\"[All Fields])"))
else:
	subquery = "" 
	for term in terms:
		# make conjunction of all terms that occur in all articles
		if terms[term]["count"] > (len(evidence) - 1):
			primaryterms.append(("(\"" + term + "\"[MeSH Terms] OR \"" + term + "\"[All Fields])"))
		# all rank 2 terms
		if terms[term]["count"] == (len(evidence) - 1):
			secondaryterms.append(("\"" + term + "\"[MeSH Terms]"))
			
query2 = querybuilder.buildQuery(primaryterms, secondaryterms, 1)
			
# write to results.html
out.write("<h3>Query obtained from input article MeSH terms</h3>")
out.write(query2)


#--------------------------------------
# PART 3: execute (combined) query)
#--------------------------------------
			
# combine with old query
#query +=  (" AND \"" + query2)

# add dates
#query += " 2004:2012 [mhda]"
#query2 += " 2004:2012 [mhda]"

# output: query for PubMed
out.write("<h3>Query1 link</h3>")
out.write("1. <a href=\"http://www.ncbi.nlm.nih.gov/pubmed/?term=" + query.replace(" ", "+").replace("\"", "&quot;") + "\">Link</a><br />")
out.write("2. <a href=\"http://www.ncbi.nlm.nih.gov/pubmed/?term=" + query2.replace(" ", "+").replace("\"", "&quot;") + "\">Link</a><br />")

# QUERY 1
# construct query of appropriate level
query1 = querybuilder.buildQuery(recommendationterms, [], level)
resp, content = h.request(baseURL + "esearch.fcgi?db=pubmed&retmode=xml&sort=relevance&retmax=100&term=" + query.replace(" ", "+"))

# get number of results from response
resultsdict = xmltodict.parse(content)["eSearchResult"]
out.write("<br />Number of results query 1: " + resultsdict["Count"])


searchresults = {}

# If there is only one result, PubMed will return it as a string
# rather than a list. In this case, convert it to a list with one element
try:
	if isinstance(resultsdict["IdList"]["Id"], basestring):
		resultsdict["IdList"]["Id"] = [resultsdict["IdList"]["Id"]]


	# initialize results dictionary and look up article data
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
	print "Query 1 TypeError"
	print "Likely cause: no query results"
	print "Number of results: " + resultsdict["Count"]

# QUERY 2
# perform query
resp, content = h.request(baseURL + "esearch.fcgi?db=pubmed&retmode=xml&sort=relevance&retmax=100&term=" + query2.replace(" ", "+"))

# get number of results from response
resultsdict = xmltodict.parse(content)["eSearchResult"]
try:
	out.write("<br />Number of results query 2: " + resultsdict["Count"])	
except KeyError:
	out.write("<br />No results for query 2.")

	
# add results to dictionary
try:
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
	print "Query 2 TypeError"
	print "Likely cause: no query results"
	print "Number of results: " + resultsdict["Count"]
except KeyError:
	print "Keyerror"
	print "Likely cause: only one result"


#-----------------------------------
# PART 4: Rank results
#-----------------------------------

# create MeSHBrowser object to calculate MeSH distance 
mb = meshbrowser.MeSHBrowser()
# determine relevance	
for res in searchresults.keys():
	titletokens = parserecommendation.cleanString(searchresults[res]["title"])
	abstracttokens = parserecommendation.cleanString(searchresults[res]["abstract"])
	for word in recommendation:
		# compare words from recommendation to title
		if word in titletokens:
			searchresults[res]["grade"] += (10./len(titletokens))*titletokens.count(word)
			searchresults[res]["keywords"].append(word)
		# compare words from recommendation to abstract
		if word in abstracttokens:
			searchresults[res]["grade"] += (8./len(abstracttokens))*abstracttokens.count(word)
			searchresults[res]["keywords"].append(word)
	# calculate MeSH distance
	for term2 in searchresults[res]["meshterms"]:
		d = 0.
		for term1 in majorterms:
			d += mb.getDistance(term1, term2)
		searchresults[res]["meshdistance"] += d/len(majorterms)
	if len(searchresults[res]["meshterms"]) > 0:
		searchresults[res]["meshdistance"] /= len(searchresults[res]["meshterms"])
		searchresults[res]["meshdistance"] = 1/searchresults[res]["meshdistance"]

	
# determine usefulness by Rosenfeld & Shiffman algorithm
# the formula was negated for readability purposes
# Source: Iruetaguena, A., Garcia Adeva, J. J., Pikatza, J. M., Segundo, U.,
# Buenestado, D., & Barrena, R. (2013). Automatic retrieval of current
# evidence to support update of bibliography in clinical guidelines. Expert
# Systems with Applications, 40(6), 2081-2091.
for res in searchresults:
	c1, c2, c3, c4, c5 = False, False, False, False, False
	if (("Randomized Controlled Trial" in searchresults[res]["pubtypes"]) \
		or \
		("Controlled Clinical Trial" in searchresults[res]["pubtypes"]) \
		or \
		("randomized trial" in searchresults[res]["abstract"].lower()) \
		or \
		("trial" in searchresults[res]["title"].lower())):
		c1 = True
	
	if (("randomized" in searchresults[res]["abstract"].lower()) \
		or \
		("randomly" in searchresults[res]["abstract"].lower()) \
		or \
		("placebo" in searchresults[res]["abstract"].lower())):
		c2 = True
	
	# TODO: c3 - 5 and extend the formula
	
	if c1:
		searchresults[res]["strength"] += 5
	
# create sorted list of article evidence
ranking = []
for res in searchresults:
	ranking.append((res, (searchresults[res]["meshdistance"]) + searchresults[res]["strength"] + (searchresults[res]["grade"])) )
ranking = sorted(ranking, key=lambda article: article[1], reverse=True)

# write list of evidence + hyperlinks to results
out.write("<h3>Top results</h3>")
c = 1
for rank in ranking:
	res = rank[0]
	s = str(c) + ". <a href=\"" + pubURL + res + "\">" + res + "</a>, "
	s += str(rank[1])
	s += "<br />Grade: " + str(searchresults[res]["grade"])
	s += "<br />Average inverse MeSH distance: " + \
		str(searchresults[res]["meshdistance"])
	s += "<br />Strength: " + str(searchresults[res]["strength"])
	s += "<br />Keywords: " + str(searchresults[res]["keywords"])
	
	if res in goals:
		s = ("<b><u>" + s + "</u></b>")
		print "Goal article found: " + res
	elif res in evidence:
		s = ("<i>" + s + "</i>")
	out.write(s + "<br /><br />")
	c += 1	


	
out.write("</body></html")

out.close()

