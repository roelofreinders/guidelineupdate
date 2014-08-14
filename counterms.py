terms2004 = open("lists/2004.txt", "r").read()
terms2012 = open("lists/2012.txt", "r").read()

terms = terms2012.replace("*", "")
tokens = terms.split("\n")

counts = {}

for term in tokens:
	counts[term] = terms.count(term)
	
score = 4
while score > 0:
	print "- Occurring %i times -" % (score)
	for term in counts:
		if counts[term] == score:
			print term
	score = score - 1