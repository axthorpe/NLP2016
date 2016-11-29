import nltk
from nltk.corpus import wordnet
import shlex
from subprocess import Popen, PIPE
from spacy.en import English

nlp = English()

class Node:
	def __init__(self, val):
		self.val = val
		self.left = None
		self.right = None
		self.parent = None
		self.tag = None

	def __str__(self):
		return '(val='+str(self.val)+',left='+ (str(self.left.val) if self.left != None else 'None') + ',right='+(str(self.right.val) if self.right != None else 'None')+',parent='+(str(self.parent.val) if self.parent != None else 'None') +',tag='+str(self.tag)+')'

def synonymMaker(word):
	synonyms = []
	# antonyms = []

	for syn in wordnet.synsets(word):
	    for l in syn.lemmas():
	        synonyms.append(l.name())
	        # if l.antonyms():
	        #     antonyms.append(l.antonyms()[0].name())
	return set(synonyms)
	# print(set(antonyms))

def rhymeMaker(word):
	cmd = 'rhyme ' + word
	process = Popen(shlex.split(cmd), stdout=PIPE)
	output = process.communicate()
	exit_code = process.wait()
	print(str(output[0]))

def dependencyParser(sentence):
	nodes = []
	doc = nlp(unicode(sentence, 'utf-8'))
	for sent in doc.sents:
		r = sent.root
		print('root: ' + r.text)
		print('parent: ' + r.head.text)
		for child in r.children:
			print(str('child: ' + child.text))

def driver(sentence1):
	candidates = []
	doc = nlp(unicode(sentence1, 'utf-8'))
	docInfo = []
	for sent in doc.sents:
		splitted = (str(sent)).split()
		docInfo.append(splitted)
	firstSentence =  docInfo[0]
	secondSentence = docInfo[1]
	for word1 in firstSentence:
		synonyms1 = synonymMaker(word1)
		if synonyms1 != None:	
			for word2 in secondSentence:
				synonyms2 = synonymMaker(word2)
				if synonyms2 != None:
					for syn1 in synonyms1:
						rhymes1 = rhymeMaker(syn1)
						if rhymes1 != None:
							for syn2 in synonyms2:
								if syn2 in rhymes1:
									print(syn1 + "   " + syn2)

def printTree(n):
	if n.left != None:
		printTree(n.left)
	print(n.val)
	if n.right != None:
		printTree(n.right)
if __name__ == '__main__':
	driver("The fox quickly jumps over the brown log. However, he then realizes that the log was a river. And the river was a ravine.")
	#nodes = dependencyParser("The fox quickly jumps over the brown log")
	# printTree(nodes[0])



# def dependencyParser(sentence)
	# for sent in doc.sents:
	# 	for token in sent:
	# 		if token.is_alpha:
	# 			print token.head.lemma_, token.tag_, token.orth_
	# 			n1 = str(token.head.lemma_)
	# 			n2 = str(token.orth_)
	# 			tag = str(token.tag_)
	# 			if tag != 'VBP' and tag != 'MD':
	# 				n1_in_nodes = False
	# 				second = None
	# 				n1New = None
	# 				first = None
	# 				for r in nodes:
	# 					if r.val == n2 and tag != 'DT':
	# 						second = r
	# 					if r.val == n1 and tag != 'DT':
	# 						first = r
	# 				if first == None:
	# 					newNode = Node(n1)
	# 					nodes.append(newNode)
	# 					first = newNode
	# 					n1New = newNode
	# 				if second == None:
	# 					newNode = Node(n2)
	# 					second = newNode
	# 					nodes.append(second)
	# 				second.tag = tag
	# 				# for n in nodes:
	# 				# 	if n == first:
	# 				if first.left == None and second.left == None:
	# 					second.parent = first
	# 					first.left = second
	# 				elif first.right == None:
	# 					second.parent = first
	# 					first.right = second
	# 				if not n1_in_nodes:
	# 					second.parent = n1New