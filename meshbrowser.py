class MeSHBrowser:
	# dictionary of the type {<MeSH term>: <Tree Branch>}
	items = {}
	importanttrees = ["A", "B", "C", "D", "E", "F", "M", "N"]
	treeranking = ["C", "D", "A", "B", "M","N", "E", "F", "G", "H", \
		"I", "J", "K", "V", "L", "Z"] 
	def __init__(self, filepath="MeSH/mtrees2014.txt"):		
		# read input file and parse to dict
		treefile = open(filepath, "r")
		for line in treefile.readlines():
			[name, branch] = line.split(";")
			self.items[name.lower()] = branch.strip("\n")
		treefile.close()
	
	# return a number that indicates the importance of a MeSH term
	# based on what subtree it is part of
	def importance(self, term):
		return len(self.treeranking) -  \
			self.treeranking.index(self.getBranch(term)[0])
	
	# sort a list of MeSH terms by important (most important term first)
	def sortImportance(self, terms):
		return sorted(terms, key=self.importance, reverse=True)
	
	# check whether or not a term is important:
	# whether it's in an important subtree
	def isImportant(self, term):
		return self.getBranch(term)[0] in self.importanttrees
		
	# given a list of terms, remove all in 'unimportant' subtrees
	def filterImportant(self, terms):
		importantterms = []
		for term in terms:
			if self.isImportant(term):
				importantterms.append(term)
		return importantterms
	
	# given a name, returns the corresponding branch
	def getBranch(self, name):
		try:
			return self.items[name.lower()]
		except KeyError:
			# TODO: find proper workaround
			# print "Error: no branch found for %s" % (name)
			return name
	
	# calculate the number of branches between %name1 and %name2
	def getDistance(self, name1, name2):
		branch1 = self.getBranch(name1.lower())
		branch2 = self.getBranch(name2.lower())
		
		# check if the terms are identical
		if branch1 == branch2:
			return 0
		
		# check if both terms are part of the same subtree
		# if not, return -1
		if branch1[0] != branch2[0]:
			return -1
		
		# chop into list
		branch1 = branch1.split(".")
		branch2 = branch2.split(".")
		
		# calculate number of common nodes at the start of each branch
		while (branch1[0] == branch2[0]):
			del branch1[0]
			del branch2[0]
			if not ((len(branch1) > 0) and (len(branch2) > 0)):
				break
		
		
		return len(branch1) + len(branch2)
		
# main method, used only for testing purposes
if __name__ == "__main__":
	mb = MeSHBrowser()
	print mb.getBranch("Heel")
	print mb.getBranch("Hip")
	print mb.getBranch("Tongue")

	print mb.sortImportance(["Metacarpus", "Independent State of Samoa", "Hip"])
	print mb.importance("Metacarpus")
	print mb.importance("Independent State of Samoa")
	print mb.getBranch("Metacarpus")
	# verify output of MeSHBrowser.getBranch
	assert (mb.getBranch("Metacarpus") == "A01.378.800.667.572")
	assert (mb.getBranch("Independent State of Samoa") == \
		"Z01.639.760.815.800.400")
	# verify output of MeSHBrowser.getDistance
	assert (mb.getDistance("Body Regions", "Anatomic Landmarks") == 1)
	assert (mb.getDistance("Heel", "Hip") == 3)
	assert (mb.getDistance("Metacarpus", "Independent State of Samoa") == -1)
	assert (mb.getDistance("Body Regions", "Independent State of Samoa") == -1)
	assert (mb.getDistance("Heel", "Heel") == 0)
	
	print (mb.getDistance("Human", "Human"))
	
	print "All tests passed succesfully!"
