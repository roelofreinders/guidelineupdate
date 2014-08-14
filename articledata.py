from setup import *
import processevidence

requests = 0
lookups = 0

def getData(id):
	# check if data is already stored
	if os.path.isfile("articledata/" + id + ".xml"):
		articlexml = open("articledata/" + id + ".xml", "r")
		content = articlexml.read()
		articlexml.close()
		global lookups 
		lookups += 1
	# if not, get it from the web
	else:
		resp, content = h.request(baseURL + "efetch.fcgi?db=pubmed&retmode=xml&id=" + id + creds)
		# write content to file
		out = open("articledata/" + id + ".xml", "w")
		out.write(content)
		out.close()
		global requests
		requests += 1
	articledata = xmltodict.parse(content)

	# get title
	title = articledata["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"]["ArticleTitle"]
	
	# get date
	date = articledata["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["DateCreated"]["Year"]
	
	# get MeSH terms
	meshterms = processevidence.buildMeSHDict([id]).keys()

	# get publication types
	pubtypes = []
	try:
		base = articledata["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"]["PublicationTypeList"]
		for pubtype in base:
			pubtypes.append(base[pubtype])
	except KeyError:
		print "No publicationtypes found for article " + id
	
	# flatten list: remove sublist that are caused by PubMed results
	if len(pubtypes) > 0:
		if not isinstance(pubtypes[0], basestring):
			pubtypes = [item for sublist in pubtypes for item in sublist]		
	
	# get abstract
	abstract = "" 
	try:
		base = articledata["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"]["Abstract"]
	except KeyError:
		print "KeyError for article " + id
		print "Likely cause: abstract not included, or bad formatting"
		return title, abstract, date, meshterms, pubtypes
	# this part deals with different XML formats between articles
	for abstr in base:
		# check if the abstract is in a subtree
		if isinstance(abstr, basestring):
			# find weird, currently unknown formats
			if "AbstractText" not in abstr:
				print "- Error: Abstracttext not found for article " + id
				print abstr
				break
			# rebranch
			base = base["AbstractText"]
			# sometimes the abstract is already found
			if isinstance(base, basestring):
				abstract += base
				break
			# other times there is a new subtree
			else:
				for part in base:
					try:
						abstract += part["#text"]
					except TypeError:
						print "No abstract for article " + id
					except KeyError:
						print "No abstract for article " + id
				break
		for part in base[abstr]:
			try:
				abstract += part["#text"] + " "
			except TypeError:
				print "No abstract for article " + id
	
	return title, abstract, date, meshterms, pubtypes[0]
