from setup import *
import sys

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
	list = evidence_ids[int(sys.argv[1])]
	list2 = getRelated(list)
	#print list2
	print len(list2)
	#list3 = getRelated(list2)
	#print len(list3)
	#print list3