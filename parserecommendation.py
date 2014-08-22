from setup import *
import meshbrowser

# This file contains several methods that are used for part 1 of the project:
# parsing the recommendation to obtain useful MeSH terms


# method cleanString
# input: a string containing punctuation, common words, etc
# returns: a list of words in the string
def cleanString(recommendation):
	# convert to lower case
	recommendation = recommendation.lower()
	
	# remove punctuation TODO: fix
	#recommendation = recommendation.translate(string.maketrans("",""), string.punctuation)
	exclude = set(string.punctuation)
	recommendation = ''.join(ch for ch in recommendation if ch not in exclude)

	# remove stopwords from recommendation
	recommendation = [i for i in recommendation.split()] # if i not in stop]
	
	return recommendation

# method getMeSHTerms
# input: a (cleaned up) recommendation
# returns: a list of all recognized MeSH terms in the recommendation,
# as strings, and containing disjuntion operators
# example input: "tamoxifen"
# example output: ["tamoxifen"]
def getMeSHTerms(recommendation):
	# convert to string seperated by + signs (for HTTP encoding of spaces)
	recommendation = "+".join(recommendation)

	# search for recommendation (to see suggested terms)
	resp, content = h.request(baseURL + "esearch.fcgi?db=pubmed&term=" + recommendation + creds)
	# parse relevant part of response
	results = xmltodict.parse(content)["eSearchResult"]

	# look at the query translation
	searchterms = results["QueryTranslation"].split(" AND ")
	
	# initialize return variable
	terms = []
	# extract all search terms corresponding to recognized MeSH headings
	for st in searchterms:
		# remove parentheses to prevent mismatching
		st = str(st)
		st = st.translate(None, "()")
		st = "(" + st + ")"
		# extract recognized MeSH terms
		if "MeSH Terms" in st:
			# TODO? fix parentheses
			# add to results
			terms.append(st)
	return terms
