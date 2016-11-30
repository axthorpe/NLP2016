import nltk
from nltk.corpus import wordnet
from nltk.wsd import lesk
import shlex
from subprocess import Popen, PIPE
from spacy.en import English
from nltk.corpus import cmudict
import pickle

nlp = English()

# class Node:
# 	def __init__(self, val):
# 		self.val = val
# 		self.left = None
# 		self.right = None
# 		self.parent = None
# 		self.tag = None

# 	def __str__(self):
# 		return '(val='+str(self.val)+',left='+ (str(self.left.val) if self.left != None else 'None') + ',right='+(str(self.right.val) if self.right != None else 'None')+',parent='+(str(self.parent.val) if self.parent != None else 'None') +',tag='+str(self.tag)+')'

def posTag(sentence):
	text = nltk.word_tokenize(sentence)
	pos_tags = nltk.pos_tag(text)
	for tag in pos_tags:
		if tag[1] == 'DT':
			continue
	print(pos_tags)

def synonymMaker(word, sent, posTag):
	synonyms = []
	# antonyms = []
	# synsetWord = (lesk(sent.split(), word,pos='n'))
	# print(synsetWord)
	# for word1 in synsetWord.lemmas():
	# 	synonyms.append(word1.name())
	# for syn in wordnet.synsets(word):
	# 	print(syn, syn.definition())
	for syn in wordnet.synsets(word):
		if syn.pos() == posTag or posTag == '':
		    for l in syn.lemmas():
		        synonyms.append(l.name())
	        # if l.antonyms():
	        #     antonyms.append(l.antonyms()[0].name())
	return list(synonyms)
	# print(set(antonyms))

def createRhymeDictionary():
	d = cmudict.dict()
	rhymesToIdx = {}
	rhyme_groups = []
	word_to_rhyme_group = {}
	curr_idx = 0
	for key in d:
		print(key)
		try:
			rhyme_raw = rhymeMaker(key)
			if rhyme_raw != None:
				rhyme = str(rhyme_raw[((str(rhyme_raw)).index('\n')):])
				if rhyme not in rhymesToIdx:
					rhymesToIdx[rhyme] = curr_idx
					rhyme_groups.append(rhyme)
					curr_idx += 1
				word_to_rhyme_group[key] = rhymesToIdx[rhyme]
		except:
			print(key)

	rhyme_groups_file = open('rhyme_groups.pickle', 'w')
	pickle.dump(rhyme_groups, rhyme_groups_file)
	rhyme_groups_file.close()

	w2r_file = open('word_to_rhyme_group.pickle', 'w')
	pickle.dump(word_to_rhyme_group, w2r_file)
	w2r_file.close()


def rhymeMaker(word):
	digits = ['2','3','4','5','6','7','8','9']
	cmd = 'rhyme ' + word
	if '\'' in word:
		return None
	if word in digits:
		return None
	if word == '0':
		return None
	if word == '1':
		return None
	process = Popen(shlex.split(cmd), stdout=PIPE)
	output = process.communicate()
	exit_code = process.wait()
	if output[0][0] == '*':
		return None
	# split_syllable = output[0].split('\n\n')
	# split_syllable[0] = split_syllable[0][36:] # Remove initial phrase
	# rhymes_syllable = []
	# curr_list = []
	# ret = []
	# for i in range(len(split_syllable)):
	# 	split_syllable[i] = split_syllable[i][3:]
	# 	split_syllable[i] = split_syllable[i].replace('\n', ',')
	# 	temp = split_syllable[i].split(',')
	# 	for j in range(len(temp)):
	# 		temp[j] = temp[j].strip()
	# 		temp[j] = temp[j].translate(None, '()1234567890')
	# 		ret.append(temp[j])
	# 	split_syllable[i] = temp
	# return split_syllable, ret
	return output[0]

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
	# synonyms1 = []
	# synonyms2 = []
	# for i in range(len(firstSentence)):
	# 	synonyms1.append(synonymMaker[firstSentence[i]])
	# for i in range(len(secondSentence)):
	#  	synonyms2.append(synonymMaker[secondSentence[i]])
	sent1_pos = ['', 'n', 'r', 'v', 'r', '', 'a', 'n']
	sent2_pos = ['r', 'n', 'r', 'v', '', '', 'n', 'v', '', 'n']
	for k,word1 in enumerate(firstSentence):
		synonyms1 = synonymMaker(word1, firstSentence, sent1_pos[k])
		if synonyms1 != None:	
			for l,word2 in enumerate(secondSentence):
				#if word1 == word2:
				print(word1 + "*******" + word2)
				synonyms2 = synonymMaker(word2, secondSentence, sent2_pos[l])
				if synonyms2 != None:
					for i in range(len(synonyms1)):
						syn1 = synonyms1[i]
						if '_' in syn1:
							syn1 = syn1[len(syn1) - syn1[::-1].index('_'):]
						rhymes1 = rhymeMaker(syn1)
						if rhymes1 != None:
							if rhymes1.strip() != '':
								for j in range(len(synonyms2)):
									syn2 = synonyms2[j]
									if '_' in syn2:
										syn2 = syn2[len(syn2) - syn2[::-1].index('_'):]
									rhymes2 = rhymeMaker(syn2)
									if rhymes2 != None:
										if rhymes2.strip() != '':
											if str(rhymes1[((str(rhymes1)).index('\n')):]) == str(rhymes2[((str(rhymes2)).index('\n')):]):
												sample_sent1 = firstSentence
												sample_sent2 = secondSentence
												sample_sent1[k] = syn1
												sample_sent2[l] = syn2
												changed_sent1 = ''
												changed_sent2 = ''
												for wd in sample_sent1:
													changed_sent1 = changed_sent1 + wd + ' '
												changed_sent1 = changed_sent1[:-1]
												for wd in sample_sent2:
													changed_sent2 = changed_sent2 + wd + ' '
												changed_sent2 = changed_sent2[:-1]
												print("------------------------------")
												print(syn1)
												print(syn2)
												print(firstSentence)
												print(secondSentence)
												print(changed_sent1)
												print(changed_sent2)
												#print(str(rhymes1[(str(rhymes1)).index('\n'):]) + "     " + str(rhymes2[(str(rhymes2)).index('\n'):]))
												print("------------------------------")
												#print(syn1 + "   " + syn2)
def printTree(n):
	if n.left != None:
		printTree(n.left)
	print(n.val)
	if n.right != None:
		printTree(n.right)
if __name__ == '__main__':
	# print(posTag('The ram quickly jumps over the brown log'))
	# print(synonymMaker('ram', 'The ram quickly jumps over the brown log', 'n'))
	# print(rhymeMaker('Hello'))
	#driver("The fox quickly jumps over the brown log. However, he then realizes that the log was a river. And the river was a ravine.")
	#nodes = dependencyParser("The fox quickly jumps over the brown log")
	# printTree(nodes[0])


	print("hello world!")
	createRhymeDictionary()
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
