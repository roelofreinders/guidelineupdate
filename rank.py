from setup import *
import parserecommendation
import json

def calculateRelevance(searchresults, recommendation, majorterms):
	idflib = open("idflib.json", "r")
	idf = json.loads(idflib.read())
	idflib.close()
	useIDF = True


	for res in searchresults.keys():
		try:
			titletokens = parserecommendation.cleanString(searchresults[res]["title"])
			abstracttokens = parserecommendation.cleanString(searchresults[res]["abstract"])
		except KeyError:
			titletokens = []
			abstracttokens = []
		for word in recommendation:
			if useIDF:
				titletokens.append(abstracttokens)
				if (word in titletokens) and (word in idf):
					searchresults[res]["grade"] += idf[word] / len(recommendation)
					searchresults[res]["keywords"].append(word)
			else:
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
		termcount = 0
		for term1 in majorterms:
			termdist = mb.getDistance(term1, term2)
			# check if term is from the same subtree
			if termdist > -1:
				d += termdist
				termcount += 1
		if termcount > 0:
			searchresults[res]["meshdistance"] += d/termcount
	if len(searchresults[res]["meshterms"]) > 0:
		searchresults[res]["meshdistance"] /= len(searchresults[res]["meshterms"])
		if searchresults[res]["meshdistance"] > 0:
			searchresults[res]["meshdistance"] = 1/searchresults[res]["meshdistance"]

	return searchresults

# determine usefulness by Rosenfeld & Shiffman algorithm
# the formula was negated for readability purposes
# Source: Iruetaguena, A., Garcia Adeva, J. J., Pikatza, J. M., Segundo, U.,
# Buenestado, D., & Barrena, R. (2013). Automatic retrieval of current
# evidence to support update of bibliography in clinical guidelines. Expert
# Systems with Applications, 40(6), 2081-2091.
def calculatestrength(searchresults):
	for res in searchresults:
		c1, c2, c3, c4, c5 = False, False, False, False, False
		try: 
			# c1
			if (("Randomized Controlled Trial" in searchresults[res]["pubtypes"]) \
				or \
				("Controlled Clinical Trial" in searchresults[res]["pubtypes"])):
				
				c1 = True
			
			# c2
			if (("randomized" in searchresults[res]["abstract"].lower()) \
				or \
				("randomly" in searchresults[res]["abstract"].lower()) \
				or \
				("placebo" in searchresults[res]["abstract"].lower())):
				c2 = True
			
			# c3
			if "trial as topic" in searchresults[res]["meshterms"]:
				c3 = True
				
			# c4
			if "trial" in searchresults[res]["title"].lower():
				c4 = True
			
			# c5
			if "animals" in searchresults[res]["meshterms"]:
				c5 = True

			
			if not (c5 or (not (c1 or c2 or c3 or c4))):
				searchresults[res]["strength"] += 5
		except KeyError:
			print "No abstract/pubtypes for article %s" % (res)
	return searchresults


# rank the results and return output as html string
def rank(searchresults, evidence, goals):
	outputstring = ""
	ranking = []
	# calulate ranking
	for res in searchresults:
		ranking.append((res, (searchresults[res]["meshdistance"]) \
			+ searchresults[res]["strength"] + (searchresults[res]["grade"])) )
	ranking = sorted(ranking, key=lambda article: article[1], reverse=True)

	# write list of evidence + hyperlinks to results
	outputstring += "<h3>Top results</h3>"
	c = 1
	goals_found = 0.
	top25 = 0.
	for rank in ranking:
		res = rank[0]
		s = str(c) + ". <a href=\"" + pubURL + res + "\">" + res + "</a>, "
		s += str(rank[1])
		s += "<br />Grade: " + str(searchresults[res]["grade"])
		s += "<br />Average inverse MeSH distance: " + \
			str(searchresults[res]["meshdistance"])
		s += "<br />Strength: " + str(searchresults[res]["strength"])
		# s += "<br />Keywords: " + str(searchresults[res]["keywords"])
		
		if res in goals:
			s = ("<b><u>" + s + "</u></b>")
			goals_found += 1
			if c < 26:
				print "Goal article found in top 25: " + res
				top25 += 1
			else:
				print "Goal article found: " + res
		elif res in evidence:
			s = ("<i>" + s + "</i>")
		outputstring += (s + "<br /><br />")
		c += 1
	return outputstring, c, goals_found, top25	