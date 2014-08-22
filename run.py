from setup import *
import rank
import sys
import parserecommendation
import processevidence
import processresults
import articledata
import querybuilder
import performquery
import tfidf

# set which recommendation should be used from commandline
if len(sys.argv) > 1:
	c = int(sys.argv[1])
else:
	c = 11

recommendation = recommendations[c]
evidence = evidence_ids[c]
goals = goal_ids[c]
earlyyear = earlyyears[c-1]
lateyear = lateyears[c-1]

print "Running for recommendation #%i:" % (c)
print recommendation
print "Earliest year: %i, latest year: %i" % (earlyyear, lateyear)

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
out.write("<h3>Rsecommendation</h3>")
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
#------------------------------------------------------------------#

# results dictionary
terms = processevidence.buildMeSHDict(evidence)


# Remove MeSH terms that don't exist in the tree
if "female" in majorterms: majorterms.remove("female")
if "male" in majorterms: majorterms.remove("male")
if "humans" in majorterms: majorterms.remove("humans")


# add the terms that occur in every article			

# if there is only one article, just extract the 'major' topics
# otherwise, conjunct all terms that occur in at least (#evidence - 1) articles
primaryterms, filteredprimaryterms, secondaryterms = \
	processevidence.sortTerms(terms, evidence)


#--------------------------------------
# PART 3: execute query
#--------------------------------------


searchresults = {}
resultcount = 0

print "Executing Query 1"
query1, resultsdict, nr_of_results = \
	performquery.searchByCombination(majorterms, [], 50, earlyyear, lateyear)


out.write("<h3>Query 1, number of results: %i</h3>" % (nr_of_results))
# output: query for PubMed
out.write("<a href=\"http://www.ncbi.nlm.nih.gov/pubmed/?term=" + \
	query1.replace(" ", "+").replace("\"", "&quot;") + "\">Link</a><br />")
out.write(query)


# If there is only one result, PubMed will return it as a string
# rather than a list. In this case, convert it to a list with one element
searchresults = processresults.processResults(resultsdict, searchresults)
resultcount += nr_of_results

#-----------------------------------
# PART 4: Rank results
#-----------------------------------

# determine relevance	
searchresults = rank.calculateRelevance(searchresults, recommendation, majorterms)

# calculate scientific strength
searchresults = rank.calculatestrength(searchresults)
	
# create sorted list of article evidence
outstring, c, goals_found, top25 = rank.rank(searchresults, evidence, goals)

out.write(outstring)
print "Total number of search results: " + str(resultcount)
print "Percentage of goal articles found:"
print str((goals_found/len(goals)) * 100) + "%"

print "Percentage of found goal articles in top 25: "
if goals_found == 0:
	print "NA"
else:
	print str((top25/goals_found * 100)) + "%"
	
out.write("</body></html")

out.close()

