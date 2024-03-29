import copy
import nltk
from nltk.corpus import wordnet
from nltk.wsd import lesk
import shlex
from subprocess import Popen, PIPE
from spacy.en import English
from nltk.corpus import cmudict
import pickle
import numpy as np
from nltk.corpus import brown
import spacy
import copy
from nltk import Tree
from nltk.parse.stanford import StanfordParser
from collections import defaultdict

parent = '/home/ubuntu/stanford/'
eng_model_path = parent + "englishRNN.ser.gz"
my_path_to_models_jar = parent + "tools/stanford-parser-full-2015-12-09/stanford-parser-3.6.0-models.jar"
my_path_to_jar = parent + "tools/stanford-parser-full-2015-12-09/stanford-parser.jar"
parser=StanfordParser(model_path=eng_model_path, path_to_models_jar=my_path_to_models_jar, path_to_jar=my_path_to_jar)


nlp = English()
file1 = open('word_to_rhyme_group.pickle', 'rb')
w2r_data = pickle.load(file1)
file1.close()
file2 = open('rhyme_groups.pickle', 'rb')
rg_data = pickle.load(file2)
file2.close()
print_script = ''
result = []

ngram = defaultdict(lambda: defaultdict(int))
ngram_rev = defaultdict(lambda: defaultdict(int)) #reversed n-grams
corpus = " ".join(str(word) for word in brown.words())

for sentence in nltk.sent_tokenize(corpus):
	tokens = map(str.lower, nltk.word_tokenize(sentence))
	for token, next_token in zip(tokens, tokens[1:]):
		ngram[token][next_token] += 1
	for token, rev_token in zip(tokens[1:], tokens):
		ngram_rev[token][rev_token] += 1
for token in ngram:
	total = np.log(np.sum(ngram[token].values()))
	total_rev = np.log(np.sum(ngram_rev[token].values()))
	ngram[token] = {nxt: np.log(v) - total 
					for nxt, v in ngram[token].items()}
	ngram_rev[token] = {prv: np.log(v) - total_rev 
					for prv, v in ngram_rev[token].items()}

def get_likelihood_score(sent):
	prob = 0.0
	#ngram_rev['jefferson']['thomas'] = -1.7
	#ngram['thomas']['jefferson']
	#for word in indiv['ctx']:
	for i in range(0, len(sent) - 1):
		word = sent[i].lower()
		next = sent[i+1].lower()
		try:
			prob += ngram[word][next]
			#print(prob)
		except:
			#print("dis not in here")
			prob += (-5)
	for i in range(1, len(sent)):
		word = sent[i].lower()
		prev = sent[i-1].lower()
		try:
			prob += ngram_rev[prev][word]
			#print(prob)
		except:
			#print("dis not in here")
			prob += (-5)
	prob = prob/len(sent)
	return 10*(np.exp(prob))

class Node:
	def __init__(self, val):
		self.val = val
		self.children = []
		self.parent = None
		self.tag = None

	def __str__(self):
		return '(val='+str(self.val)+',children='+ (str([child.val for child in self.children])) +',parent='+(str(self.parent.val) if self.parent != None else 'None') +',tag='+str(self.tag)+')'

def posTag(sentence):
	text = nltk.word_tokenize(sentence)
	pos_tags = nltk.pos_tag(text)
	for tag in pos_tags:
		if tag[1] == 'DT':
			continue
	print(pos_tags)

def synonymMaker(word, sent):
	synonyms = []
	synset_word = lesk(sent, word)
	if not synset_word:
		return None

	for syn in synset_word.lemmas():
		synonyms.append(syn.name())
	hypos = synset_word.hyponyms()

	for hyps in hypos:
		for ny in hyps.lemma_names():
			synonyms.append(ny)
	hypers = synset_word.hypernyms()

	for hyps in hypers:
		for ny in hyps.lemma_names():
			synonyms.append(ny)
	if word not in synonyms:
		synonyms.append(word)
	return list(synonyms)

# def synonymMaker(word, sent):
# 	synonyms = []
# 	for syn in wordnet.synsets(word):
# 	    for l in syn.lemmas():
# 	        synonyms.append(l.name())
# 	return list(synonyms)

# def synonymMaker(word, sent, posTag):
# 	synonyms = []
# 	for syn in wordnet.synsets(word):
# 		if syn.pos() == posTag or posTag == '':
# 		    for l in syn.lemmas():
# 		        synonyms.append(l.name())
# 	return list(synonyms)

def createRhymeDictionary():
	d = cmudict.dict()
	rhymesToIdx = {}
	rhyme_groups = []
	word_to_rhyme_group = {}
	curr_idx = 0
	for key in d:
		print(key)
		try:
			rhyme_raw = rhymeMaker2(key)
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

def rhymeMaker2(word):
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

def rhymeMaker(word):
	if word in w2r_data:
		key = w2r_data[word]
		rg = rg_data[key]
		return rg
	return None

def printTree(n, text_of_interest):
	global print_script
	if len(n.children) == 0:
		print_script = print_script +  (n.val) + ' '
	elif n.val == text_of_interest:
		for child in n.children:
			printTree(child, text_of_interest)
		print_script = print_script +  (n.val) + ' '
	elif n.tag == 'NOUN':
		temp_bool = True
		for child in n.children:
			if child.tag == 'ADJ':
				printTree(child, text_of_interest)
				print_script = print_script +  (n.val) + ' '
				temp_bool = False
			else:
				printTree(child, text_of_interest)
		if temp_bool:
			print_script = print_script +  (n.val) + ' '
	elif n.tag == 'VERB':
		temp_bool = True
		for i in range(0,len(n.children)):
			if (n.children[i].tag == 'NOUN' or n.children[i].tag == 'ADV') and temp_bool:
				printTree(n.children[i], text_of_interest)
				print_script = print_script +  (n.val) + ' '
				temp_bool = False
			else:
				printTree(n.children[i], text_of_interest)
	else:
		print_script = print_script +  (n.val) + ' '
		for child in n.children:
			printTree(child, text_of_interest)

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_

def traverseTree(tree):
    tree.set_label(str(tree.label()))
    for i in range(len(tree)):
        if type(tree[i]) == nltk.tree.Tree:
            traverseTree(tree[i])
        else:
        	tree[i] = Tree(str(tree[i]), [])

def traverseTree2(tree, paths, prop_word, num):
	global result
	if len(paths) != 0 :
		paths[-1][1] = num
	if not isinstance(tree, nltk.tree.Tree):
		if tree == prop_word:
			result = paths
			return False
		return True
	paths.append([tree, 0])
	
	for i in range(len(tree)):
		b = traverseTree2(tree[i], paths[:], prop_word, i)
		if (b == False):
			return False
	return True

def propogate(dtree, path):
	global result
	while(len(path) != 0):	
		tree,num = path.pop()
		if num <= len(tree)-1:
			temp = tree.pop(num)
			tree.append(temp)

def dependencyParser2(sentence, prop_word):
	global result
	dep_tree = parser.raw_parse(sentence).next()
	dep_tree.pretty_print()
	paths = []
	result = []
	traverseTree2(dep_tree, paths, prop_word, 0)
	propogate(dep_tree, result)
	dep_tree.pretty_print()
	sent = ''
	for l in dep_tree.leaves():
		sent = sent + l + ' '
	sent = sent[:-1]
	return sent


def dependencyParser(sentence, prop_word):
	global print_script
	nodes = []
	doc = nlp(sentence)
	[to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]
	nltk_tree = None
	for sent in doc.sents:
		nltk_tree = to_nltk_tree(sent.root)
	traverseTree(nltk_tree)
	print("---------------_")
	nltk_tree.chomsky_normal_form()
	for p in nltk_tree.productions():
		print(p)
	print("---------------")
	# [to_nltk_tree(sent.root).chomsky_normal_form().pretty_print() for sent in doc.sents]
	
	for sent in doc.sents:
		r = sent.root
		# emptyNode = spacy.tokens.token.Token(None,None,0)
		# print(emptyNode.text)
		# r.head = emptyNode
		n = Node(r.text)
		n.tag = r.pos_
		running = True
		list_of_nodes = []
		list_of_mynodes = []
		list_of_nodes.append(r)
		list_of_mynodes.append(n)
		while(running and len(list_of_nodes) != 0):
			parent = list_of_nodes.pop(0)
			my_parent = list_of_mynodes.pop(0)
			for child in parent.children:
				nd = Node(child.text)
				nd.tag = child.pos_
				nd.parent = my_parent
				my_parent.children.append(nd)
				list_of_nodes.append(child)
				list_of_mynodes.append(nd)
		# parent = n
		# childs = []
		# for child in r.children:
		# 	newNode = Node(child.text)
		# 	newNode.tag = child.tag
		# 	newNode.parent = child.head.text
		# 	childs.append(newNode)
		# n.children = childs
		text_of_interest = prop_word
		node_of_interest = None
		running = True
		list_of_nodes = []
		list_of_nodes.append(n)
		while(running and len(list_of_nodes) != 0):
			if list_of_nodes[0].val == text_of_interest:
				node_of_interest = list_of_nodes[0]
				running = False
			for child in (list_of_nodes.pop(0)).children:
				if child.val == text_of_interest:
					node_of_interest = child
					running = False
				list_of_nodes.append(child)
		running = True
		while(running and node_of_interest.parent != None):
			parent = node_of_interest.parent
			childs = []
			childs_text = []
			for c in parent.children:
				childs.append(c)
				childs_text.append(c.val)
			if childs_text[-1] != node_of_interest.val:
				index_of_interest = childs_text.index(node_of_interest.val)
				popped = childs.pop(index_of_interest)
				childs.append(popped)
				popped2 = childs_text.pop(index_of_interest)
				childs_text.append(popped2)
			parent.children = childs
			node_of_interest = parent
		print_script = ''
		printTree(n, text_of_interest)
	for sent in doc.sents:
		for token in sent:
			if token.is_alpha:
				print token.head.lemma_, token.tag_, token.orth_
	return print_script

def driverDriver(dict1, dict2):
	ret1, ret2, b = driver(dict1['sent'], dict2['sent'])
	new_dict1 = {}
	new_dict2 = {}
	new_dict1['sent'] = ret1
	new_dict1['ctx'] = dict1['ctx']
	new_dict1['stress'] = dict1['stress']
	new_dict2['sent'] = ret2
	new_dict2['ctx'] = dict2['ctx']
	new_dict2['stress'] = dict2['stress']
	return new_dict1, new_dict2, b

def driver(sentence1, sentence2):
	candidates = []
	firstSentence =  sentence1
	secondSentence = sentence2
	matched_rhymes = []
	for i in range(len(sentence1)):
		sentence1[i] = sentence1[i].lower()
	for i in range(len(sentence2)):
		sentence2[i] = sentence2[i].lower()
	
	# synonyms1 = []
	# synonyms2 = []
	# for i in range(len(firstSentence)):
	# 	synonyms1.append(synonymMaker[firstSentence[i]])
	# for i in range(len(secondSentence)):
	#  	synonyms2.append(synonymMaker[secondSentence[i]])
	sent1_pos = ['', 'n', 'r', 'v', 'r', '', 'a', 'n']
	sent2_pos = ['r', 'n', 'r', 'v', '', '', 'n', 'v', '', 'n']
	for j in range(len(firstSentence)):
		temp = firstSentence[j]
		temp = temp.replace(',', '')
		temp = temp.replace('.', '')
		temp = temp.replace('!', '')
		temp = temp.replace('?', '')
		firstSentence[j] = temp
	for j in range(len(secondSentence)):
		temp = secondSentence[j]
		temp = temp.replace(',', '')
		temp = temp.replace('.', '')
		temp = temp.replace('!', '')
		temp = temp.replace('?', '')
		secondSentence[j] = temp
	for k,word1 in enumerate(firstSentence):
		synonyms1 = synonymMaker(word1, firstSentence)
		if synonyms1 != None:	
			for l,word2 in enumerate(secondSentence):
				#if word1 == word2:
				print(word1 + "*******" + word2)
				if word1 != word2:
					synonyms2 = synonymMaker(word2, secondSentence)
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
													if not ([syn1, syn2] in matched_rhymes) and not ([syn2, syn1] in matched_rhymes) and syn1 != syn2:
														sample_sent1 = firstSentence[:]	
														sample_sent2 = secondSentence[:]
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
														propped_sent1 = dependencyParser2(changed_sent1, syn1)
														propped_sent2 = dependencyParser2(changed_sent2, syn2)
														matched_rhymes.append([syn1, syn2])
														likelihood1 = get_likelihood_score(propped_sent1)
														likelihood2 = get_likelihood_score(propped_sent2)
														print("------------------------------")
														if [propped_sent1, propped_sent2] not in candidates:
															candidates.append([propped_sent1, propped_sent2, likelihood1, likelihood2])
														print(propped_sent1)
														print(propped_sent2)
														print(likelihood1)
														print(likelihood2)
														#print(str(rhymes1[(str(rhymes1)).index('\n'):]) + "     " + str(rhymes2[(str(rhymes2)).index('\n'):]))
														print("------------------------------")
														#print(syn1 + "   " + syn2)
	b = True
	for candidate in candidates:
		print(candidate[0])
		print(candidate[1])
	if len(candidates) == 0:
		b = False
		return sentence1, sentence2, b
	else:
		b = True
		#Did rhyme
		best1 = ''
		best2 = ''
		sum_score = 0
		for candidate_pair in candidates:
			tot_score = get_likelihood_score(candidate_pair[0]) + get_likelihood_score(candidate_pair[1])
			if tot_score > sum_score:
				sum_score = tot_score
				best1 = candidate_pair[0]
				best2 = candidate_pair[1]
		print('Chose: ' + best1)
		print('Chose: ' + best2)
		return best1.split(' '), best2.split(' '), b

if __name__ == '__main__':
	# dependencyParser('The man shot an elephant in his sleep')
	# print(posTag('The ram quickly jumps over the brown log'))
	# print(synonymMaker('ram', 'The ram quickly jumps over the brown log', 'n'))
	# print(rhymeMaker('Hello'))
	# driverDriver({'sent':['The', 'fox', 'quickly', 'jumps', 'over', 'the', 'brown', 'log'], 'ctx':['The', 'fox', 'quickly', 'jumps', 'over', 'the', 'brown', 'log'], 'stress':'030300300'},{'sent':['However,', 'he', 'then', 'realizes', 'that', 'the', 'log', 'was', 'a', 'river.'], 'ctx':['The', 'fox', 'quickly', 'jumps', 'over', 'the', 'brown', 'log'], 'stress':'030300300'})
	# print(driverDriver({'sent':['Who', 'lives', 'in', 'a', 'pineapple', 'under', 'the', 'ocean'], 'ctx':['Who', 'lives', 'in', 'a', 'pineapple', 'under', 'the', 'ocean'], 'stress':'030300300'},{'sent':['He', 'is', 'absorbent', 'and', 'yellow', 'and', 'porous'], 'ctx':['He', 'is', 'absorbent', 'and', 'yellow', 'and', 'porous'], 'stress':'030300300'}))
	
	sent1 = 'He lives in a pineapple under the sea'
	sent2 = 'The old man loves to eat ice cream at the restaurant down the street'
	# He lives in a pineapple under the sea
	# He yellow and absorbent and porous be
	# driverDriver({'sent':sent1.split(), 'ctx':sent1.split(), 'stress':'030300300'},{'sent':sent2.split(), 'ctx':sent2.split(), 'stress':'030300300'})
	# print(dependencyParser2(unicode(sent1), 'brown'))
	print(dependencyParser2(unicode(sent2.lower()), 'man'))
	#print(driverDriver({'sent':sent1.split(), 'ctx':sent1.split(), 'stress':'030300300'},{'sent':sent2.split(), 'ctx':sent2.split(), 'stress':'030300300'}))
	# print(driverDriver({'sent':['The', 'dog', 'played', 'outside', 'until', 'he', 'got', 'tired'], 'ctx':['The', 'dog', 'played', 'outside', 'until', 'he', 'got', 'tired'], 'stress':'030300300'},{'sent':['The', 'cat', 'sat', 'on', 'the', 'couch', 'and', 'licked', 'itself', 'clean'], 'ctx':['The', 'cat', 'sat', 'on', 'the', 'couch', 'and', 'licked', 'itself', 'clean'], 'stress':'030300300'}))

	# driver(['The', 'fox', 'quickly', 'jumps', 'over', 'the', 'brown', 'log'], ['However,', 'he', 'then', 'realizes', 'that', 'the', 'log', 'was', 'a', 'river.'])
	# nodes = dependencyParser("The fox quickly jumps over the brown log")
	# printTree(nodes[0])
	# print("hello world!")
	# createRhymeDictionary()

#sent, ctx, stress
#sent_modded, ctx, stress

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
