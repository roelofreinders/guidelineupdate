from setup import *
import math
import xmltodict
import glob
import json
from parserecommendation import cleanString

def parseabstract(base):
	abstract = ""
	for abstr in base:
		try:
			if isinstance(abstr, basestring):
			# find weird, currently unknown formats
				if "AbstractText" not in abstr:
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
						abstract += part["#text"]
				break
			for part in base[abstr]:
				abstract += part["#text"] + " "
		except KeyError:
			return ""
		except TypeError:
			return ""

	return abstract

def builddflib(filelist):
	doccount = {}

	idf = {}
	errcount = 0
	nr_of_documents = 0
	for f in filelist:
		if not os.path.isfile(f):
			id = f[12:-4]
			print "Getting articledata for PMID " + id
			resp, content = h.request(baseURL + "efetch.fcgi?db=pubmed&retmode=xml&id=" + id + creds)
			out = open(f, "w")
			out.write(content)
			out.close()
		doc = open(f, "r")
		articledata = xmltodict.parse(doc)
		try:
			base = articledata["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"]["Abstract"]
			abstract = parseabstract(base)
			if abstract == "":
				errcount += 1
			else:
				nr_of_documents += 1
				words = cleanString(abstract)
				# word counts in current file
				for word in set(words):
					doccount[word] = doccount.setdefault(word, 0) +	1
					

		except KeyError:
			errcount += 1
		doc.close()

	# calculate idf
	idf = {}
	for word in doccount.keys():
		idf[word] = math.log(nr_of_documents/doccount[word])

	print "# processed succesfully: " + str(nr_of_documents)
	print "# errors: " + str(errcount)
	
	return idf

def getRelated(ids):
	# get related articles from elink 
	batch = "id=" 
	for id in ids:
		batch += (id + ",")
	# remove trailing comma
	batch = batch[:-1]

	# send elink request for ids
	resp, content = h.request(baseURL + "elink.fcgi?db=pubmed&dbfrom=pubmed&" + batch + creds)

	related = []

	# get related articles from PubMed
	linkdict = xmltodict.parse(content)["eLinkResult"]["LinkSet"]
	for article in linkdict["LinkSetDb"]:
		for link in article["Link"]:
			try:
				related.append(link["Id"])
			except TypeError:
				print "TypeError was thrown"

	related = set(related)
	return related


if __name__ == "__main__":
	flist = glob.glob("articledata/*.xml")
	print flist[0]
	print "Number of articles in /articledata/: " + str(len(flist))
	idf = builddflib(flist)
	out = open("idflib.json", "w")	
	out.write(json.dumps(idf))
	print "Wrote dictionary to idflib.json"
	out.close()