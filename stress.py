import nltk
import editdistance
import wikipedia
from nltk.corpus import cmudict
import string
from sets import Set
import pylast

puncts = Set(string.punctuation)
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
d = cmudict.dict()

def getStress(word):
	bin = ''
	for pr in d[word][0]:
		if '0' in pr:
			bin += '0'
		elif '1' in pr:
			bin += '1'
		elif '2' in pr:
			bin += '1'
	return bin

def getBeatFromSentence(sent):
	ans = ''
	words = []
	tokens = nltk.word_tokenize(sent)
	for tok in tokens:
		word = tok.lower()
		if word in d:
			stress = getStress(word.lower())
			ans += (stress + ' ')
			words.append(word)
		#else:
			#print(word)
	return words, ans.strip()

def getBeatFromParagraph(paragraph):
	sentences = tokenizer.tokenize(paragraph)
	ans = ''
	all_words = []
	for sent in sentences:
		words, stresses = getBeatFromSentence(sent)
		all_words.extend(words)
		ans += (stresses + ' ')
	return [ans.strip().split(' '), all_words, sentences]

def concat(phrase):
	return ''.join(phrase.split(' '))


def numValid(tokenized):
	num_valid = 0
	for token in tokenized:
		#print(token)
		if token.lower() in d:
			num_valid += 1
	return num_valid

def splitBeats(tup, nums):
	ans = []
	i = 0
	idx = 0
	num_idx = 0
	sentence_idx = 0
	word_count = 0
	sub = []
	curr_sentence = nltk.word_tokenize(tup[2][0])
	#print(numValid(curr_sentence))
	#print(curr_sentence)

	#print(curr_sentence)
	while (i < len(tup[0])):
		idx += len(tup[0][i])

		sub.append([tup[0][i], tup[1][i], tup[2][sentence_idx]]) #our thing seems to be off by 1 somewhere, but not a big deal
		if idx >= max(nums[num_idx] - 2,1):
			num_idx += 1
			if (num_idx == len(nums)):
				num_idx = 0
			ans.append(sub)
			sub = []
			idx = 0
		i += 1
		#print(i)
		if word_count == (numValid(curr_sentence)):
			word_count = 0
			sentence_idx += 1
			#print(sentence_idx)
			curr_sentence = nltk.word_tokenize(tup[2][sentence_idx])
		word_count += 1
	return ans

def tupToDict(tup, idx):
	t_dict = {}
	t_dict['stress'] = []
	t_dict['sent'] = []
	t_dict['ctx'] = []

	for word in tup[idx]:
		t_dict['stress'].append(word[0].lower())
		t_dict['sent'].append(word[1].lower())
		for w in nltk.word_tokenize(word[2]):
			if w not in t_dict['ctx']:
				t_dict['ctx'].append(w.lower())

	new_list = []
	for c in t_dict['ctx']:
		new_list.append(c)

	t_dict['ctx'] = new_list
	return t_dict

if __name__ == "main":
	sample = "Jefferson was primarily of English ancestry, born and educated in Virginia. He graduated from the College of William and Mary and briefly practiced law, at times defending slaves seeking their freedom. During the American Revolution, he represented Virginia in the Continental Congress that adopted the Declaration, drafted the law for religious freedom as a Virginia legislator, and served as a wartime governor. He became the United States Minister to France in May time, and subsequently the nation's first Secretary of State a year later under President George Washington. Jefferson and James Madison organized the Democratic Republican Party to oppose the Federalist Party during the formation of the First Party System. With Madison, he anonymously wrote the Kentucky and Virginia Resolutions later, which sought to embolden states rights in opposition to the national government by nullifying the Alien and Sedition Acts. As President, Jefferson pursued the nations shipping and trade interests against Barbary pirates and aggressive British trade policies. He also organized the Louisiana Purchase, almost doubling the countries territory. As a result of peace negotiations with France, his administration reduced military forces. He was reelected at a later time. The second term of Jefferson was beset with difficulties at home, including the trial of former Vice President Aaron Burr. American foreign trade was diminished when Jefferson implemented the Embargo Act of time, responding to British threats to United States shipping. In time, Jefferson began a controversial process of Indian tribe removal to the newly organized Louisiana Territory, and he signed the Act Prohibiting Importation of Slaves in time."
	sentences = tokenizer.tokenize(sample)

	p1 = "An ember sparked will softly glow"
	p2 = "and fed by fuel, will grow and grow."
	p3 = "I once was cinder, sparked by you,"
	p4 = "first timid. . . till the flames then grew"

	#tup = getBeatFromParagraph(sentences)
	#print(tup)
	#print(model_tup)
	#splits = splitBeats(tup, 8)

	#for split in splits:
	#	print(split)

	ny = wikipedia.page('New York')
	sects = ny.sections #it's a list 
	sandy_section = ny.section(ny.sections[7])

	tup = getBeatFromParagraph(sandy_section)

