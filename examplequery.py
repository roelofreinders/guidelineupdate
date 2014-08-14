import httplib2
import xmltodict
import string
from nltk.corpus import stopwords

# CONSTANTS + INITIALIZATION
# lists of evidence IDs
ids_ex1 = ["9469327", "12867108", "10683002", "8292119"]
ids_ex2 = ["12867108", "10376613"]
ids_ex3 = ["11794170"]
# goals: new evidence in 2012
goals_ex1 = ["16864166", "20956824", "16801628"]
goals_ex2 = ["20956824", "21398619"]
goals_ex3 = ["17577015"]
# conclusions from guideline
conclusion_ex1 = """Addition of radiotherapy following local excision of DCIS results in a significantly lower risk of local recurrence (this is valid for all subgroups)."""
conclusion_ex2 = """Adjuvant therapy with tamoxifen in breast-conserving treatment of DCIS, removed with tumour-free excision margins, results in limited improvement of local tumour control and no survival benefit."""
conclusion_ex3 = """After a boost the risk of local recurrence is lower. The absolute benefit of a boost following complete resection decreases with patient age."""

# API set-up
# base URL for all Entrez queries
baseURL = "http://eutils.ncbi.nih.gov/entrez/eutils/"
pubURL = "http://www.ncbi.nlm.nih.gov/pubmed/"
# API credentials
creds = "&email=roelofr@gmail.com&tool=reinders"

# HTTP processor
h = httplib2.Http()

# Final result: query suggested by the system
query = ""

# Create output intro
out = open("results.html", "w")
out.write("""<html>
<head>
	<title>PubMed query results</title>
</head>
<body>""")

ids = ids_ex2
conclusion = conclusion_ex2
goals = goals_ex2

out.write("<h1>Results</h1>")
out.write("<h3>Conclusion</h3>")
out.write(conclusion)
out.write("<h3>Input papers</h3>")
for id in ids:
	out.write("<a href=\"" + pubURL + id + "\">" + id + "</a><br />")


related = []

#---------------------------------------------#
# PART 1: processing text from the conclusion #
#---------------------------------------------#

# remove punctuation
conclusion = conclusion.translate(string.maketrans("",""), string.punctuation)

# load NLTK stopword corpus
stop = stopwords.words("english")

# remove stopwords from conclusion
conclusion = [i for i in conclusion.split() if i not in stop]

# convert to string seperated by + signs (for HTTP encoding of spaces)
conclusion = "+".join(conclusion)

# search for conclusion (to see suggested terms)
resp, content = h.request(baseURL + "esearch.fcgi?db=pubmed&term=" + conclusion + creds)
# parse relevant part of response
results = xmltodict.parse(content)["eSearchResult"]

# look at the query translation
searchterms = results["QueryTranslation"].split(" AND ")

# extract all search terms corresponding to recognized MeSH headings
for st in searchterms:
	# extract recognized MeSH terms
	if "MeSH Terms" in st:
		# TODO? fix parentheses
		"""if " OR " in st:
			st = st.replace("(", "")
			st = st.replace(")", "")
			st = "(" + st + ")"""
		# add to results
		if len(query) > 0:
			query = query + " AND "
		query = query + st

out.write("<h3>Query obtained from parsing conclusion</h3>")
out.write(query)

# PART 2:
# get MeSHterms from all articles in evidence list (variable ids)
# TODO: subheadings

# results dictionary
terms = {}

for id in ids:
	# call API for metadata on current article
	resp, content = h.request(baseURL + "efetch.fcgi?db=pubmed&retmode=xml&id=" + id + creds)

	# parse relevant part of XML response to dictionary
	meshdict = xmltodict.parse(content)["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["MeshHeadingList"]["MeshHeading"]

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

# add the terms that occur in every article			
combined = ""

# if there is only one article, just extract the 'major' topics
if len(ids) == 1:
	for term in terms:
		if terms[term]["major"] >= 1:
			combined += (" AND \"" + term + "\"[MeSH Terms]")
else:
	for term in terms:		
		if terms[term]["count"] > (len(ids) - 1):
			combined += (" AND \"" + term + "\"[MeSH Terms]")

out.write("<h3>Query obtained from input article MeSH terms</h3>")
out.write(combined)
			
# combine with old query
query += combined

# output: query for PubMed
out.write("<h3>Query link</h3>")
out.write("<a href=\"http://www.ncbi.nlm.nih.gov/pubmed/?term=" + query.replace(" ", "+").replace("\"", "&quot;") + "\">Link</a>")

# create xml dump for development purposes
outxml = open("out.txt", "w")

# perform query
resp, content = h.request(baseURL + "esearch.fcgi?db=pubmed&retmode=xml&sort=relevance&retmax=100&term=" + query.replace(" ", "+"))
outxml.write(content)
outxml.close()

# get number of results from response
resultsdict = xmltodict.parse(content)["eSearchResult"]
out.write("<br />Number of results: " + resultsdict["Count"])

searchresults = []

# write list of ids + hyperlinks to results
c = 1
out.write("<h3>Top " + resultsdict["RetMax"] + " results</h3>")
for res in resultsdict["IdList"]["Id"]:
	s = str(c) + ". <a href=\"" + pubURL + res + "\">" + res + "</a><br />"
	if res in goals:
		s = ("<b><u>" + s + "</u></b>")
	out.write(s)
	searchresults.append(res)
	c += 1

# get related articles from elink
batch = "id=" 
for id in ids:
	batch += (id + ",")
# remove trailing comma
batch = batch[:-1]

# send elink request for ids
resp, content = h.request(baseURL + "elink.fcgi?db=pubmed&dbfrom=pubmed&" + batch)

related = []

# get related articles from PubMed
linkdict = xmltodict.parse(content)["eLinkResult"]["LinkSet"]
for article in linkdict["LinkSetDb"]:
	for link in article["Link"]:
		related.append(link["Id"])

related = set(related)

# give overview of PubMed related articles		
out.write("<h3>Number of related articles found</h3>")
out.write(str(len(related)))
out.write("<h3>Goals found in related articles</h3>")
for rel in related:
	if rel in goals:
		out.write(rel + "<br />")

out.write("<h3>Overlapping articles</h3>")
for res in searchresults:
	if res in related:
		out.write("<a href=\"" + pubURL + res + "\">" + res + "</a><br />")

out.write("</body></html")

out.close()

