from setup import *

def addTermToQuery(query, term, operator):
	term = "\"" + term + "\"[MeSH Terms]"
	if len(query) == 0:
		return term
	else:
		return query + " " + operator + " " + term


# Construct a query that can be sent to PubMed
# Arguments:
# 	primaryterms: list of most important terms
#	secondaryterms: list of less important terms
#	mb: instance of meshbrowser class	
#	level: number that indicates how specific the query should be
#		low: very broad
#		high: very specific
#	earliestyear: lowest year allowed
#	latestyear: highest year allowed
def buildQuery(primaryterms, secondaryterms, level, \
		earliestyear = 0, latestyear = 3000):
	# Check valid input parameters
	if (len(primaryterms) + len(secondaryterms)) == 0:
		print "Error in call to buildQuery: no input terms given"
		return ""
	if (level < 0) or (level > 4):
		print "Error in call to buildQuery: invalid value for level:"
		print level
		return ""
	if earliestyear > latestyear:
		print "Error in call to buildQuery: earliest year > latest year: "
		print "%i > %i" % (earliestyear, latestyear)
		return ""
	
	# initialize variable
	query = ""
	
	# create (subquery) from primary terms:
	# level 0: disjunction of primary terms
	# level 1+: conjunction of primary terms
	ptquery = ""
	for term in primaryterms:
		if len(ptquery) == 0:
			ptquery += term
		else:
			if level == 0:
				ptquery += " OR "
			else:
				ptquery += " AND "
			ptquery += term
	
	# level 0: disjunction of primary and secondary terms
	if level == 0:
		# combine lists of terms, remove duplicates
		allterms = list(set(primaryterms + secondaryterms))
		for term in allterms:
			query = addTermToQuery(query, term, "OR")
	# level 1: disjunction of primary terms
	elif level == 1:
		for term in primaryterms:
			query = addTermToQuery(query, term, "OR")

	# level 2: conjunction of primary terms
	elif level == 2: 
		for term in primaryterms:
			query = addTermToQuery(query, term, "AND")
	# level 3: conjunction of primary terms AND disjunction of secondary terms
	elif level == 3:
		for term in primaryterms:
			query = addTermToQuery(query, term, "AND")
		if len(secondaryterms) > 0:
			stquery = ""
			for term in secondaryterms:
				stquery = addTermToQuery(stquery, term, "OR")
			query += (" AND (" + stquery + ")")
	# level 4: conjunction of primary terms AND conjunction of secondary terms
	elif level == 4:
		for term in primaryterms:
			query = addTermToQuery(query, term, "AND")
		if len(secondaryterms) > 0:
			stquery = ""
			for term in secondaryterms:
				stquery = addTermToQuery(stquery, term, "AND")
			query += (" AND " + stquery)


	# add publication years
	if earliestyear > 0 and latestyear < 3000:
		query += (" AND (" + "%i[PDAT] : %i[PDAT])" % (earliestyear, latestyear))
	return query
	

# main function, for testing purposes only
if __name__ == "__main__":
	for i in range(-1, 6):
		print buildQuery(["P1", "P2", "P2", "P3"], ["S1", "S1", "S2", "S3"], i)
