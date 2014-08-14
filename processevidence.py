from setup import *

# method buildMeSHDict
# input: list of PubMed evidence
# output: dictionary containing combined counts for MeSH terms, and
# indicators of whether they are major or not
# output format: terms["MeSH terms"]["count"/"major"]
def buildMeSHDict(evidence):
	terms = {}
	for id in evidence:
		# get for metadata on current article
		# if the filedata is in the articledata folder, get it from there
		if os.path.isfile("articledata/" + id + ".xml"):
			f = open("articledata/" + id + ".xml")
			content = f.read()
			f.close()
			resp = ("articledata/" + id + ".xml")
		# if not, get it from the web and store it in a file
		else:
			resp, content = h.request(baseURL + "efetch.fcgi?db=pubmed&retmode=xml&id=" + id + creds)
			out = open("articledata/" + id + ".xml", "w")
			out.write(content)
			out.close()

		# parse relevant part of XML response to dictionary
		# on bad return, write response to error.xml (NOT TESTED YET)
		try:
			meshdict = xmltodict.parse(content)["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["MeshHeadingList"]["MeshHeading"]
		except KeyError:
			print "No MeSH terms found for article " + id
			return terms

		# add the MeSH terms for the current article to the results
		for term in meshdict:
			name = term["DescriptorName"]["#text"] 
		
			# if the term is new, create a new entry in the dict
			if name not in terms:
				terms[name] = {}
				terms[name]["count"] = 0
				terms[name]["major"] = 0
			# update count for term
			terms[name]["count"] += 1
			if term["DescriptorName"]["@MajorTopicYN"] == "Y":
				terms[name]["major"] += 1
	
	return terms

# if there is only one article, just extract the 'major' topics
# otherwise, conjunct all terms that occur in at least (#evidence - 1) articles
def sortTerms(terms, evidence):
	primaryterms = []
	filteredprimaryterms = []
	secondaryterms = []
	for term in terms:
		#termstring = "(\"" + term + "\"[MeSH Terms] OR \"" + term + "\"[All Fields])"
		if len(evidence) == 1:
			if (terms[term]["major"] >= 1) or (mb.isImportant(term)):
				primaryterms.append(term)
				if mb.isImportant(term):
					filteredprimaryterms.append(term)
		else:
			subquery = "" 
			# make conjunction of all terms that occur in all articles
			if terms[term]["count"] > (len(evidence) - 1):
				primaryterms.append(term)
				if mb.isImportant(term):
					filteredprimaryterms.append(term)
			# all rank 2 terms
			if terms[term]["count"] == (len(evidence) - 1):
				secondaryterms.append(term)

	return primaryterms, filteredprimaryterms, secondaryterms