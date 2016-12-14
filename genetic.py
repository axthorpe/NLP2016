import editdistance
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
from nltk.corpus import cmudict
import stress as st
import random
import music
import wikipedia
import copy
import rhymer
from nltk.corpus import brown
from nltk.probability import LidstoneProbDist, WittenBellProbDist
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
import numpy as np
from nltk.corpus import brown

# train our likelihood model on front and back context of brown corpus
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

def population(indiv):
	#generate our initial seed population
	pop = []
	for i in range(0, 80):
		new_one = copy.deepcopy(indiv)
		if len(indiv['sent']) > 2:
			pop.append(mutate(new_one, random.randint(0, len(indiv['sent']) -2)))
		else:
			pop.append(new_one)
	return pop

def hypernym_substitution(indiv, idx):
	# disambiguate the sentence[idx] in the sentence using lesk algorithm
	# get hypernyms using
	# wn.synsets(sentence[idx]) --> sample one from the correct sense

	# return sentence with modified sentence[idx]
	word = indiv['sent'][idx]
	nym = word
	net = lesk(indiv['ctx'], word)
	if net:
		sub = net.hypernyms()
		nyms = []
		for su in sub:
			for ny in su.lemma_names():
				nyms.append(ny)

		if len(nyms) > 0:
			return nym_substitution(indiv, idx, nyms)
		else:
			return indiv
	else:
		return indiv

def hyponym_substitution(indiv, idx):
	word = indiv['sent'][idx]
	nym = word
	net = lesk(indiv['ctx'], word)
	if net:
		sub = net.hyponyms()
		nyms = []
		for su in sub:
			for ny in su.lemma_names():
				nyms.append(ny)

		if len(nyms) > 0:
			return nym_substitution(indiv, idx, nyms)
		else:
			return indiv
	else:
		return indiv

def synonym_substitution(indiv, idx):
	# same as hypernym, but find synonyms instead
	word = indiv['sent'][idx]
	nym = word
	net = lesk(indiv['ctx'], word)
	if net:
		nyms = net.lemma_names()
		if len(nyms) > 0:
			return nym_substitution(indiv, idx, nyms)
		else:
			return indiv
	else:
		return indiv

def findCtxIdx(indiv, word):
	for i in range(0, len(indiv['ctx'])):
		if indiv['ctx'][i].lower() == word.lower():
			return i

	return 0

def nym_substitution(indiv, idx, nyms):
	nym = random.choice(nyms)
	if nym in d:
		# reset indiv to the correct stuff, return
		indiv['stress'][idx] = st.getStress(nym)
		indiv['ctx'][findCtxIdx(indiv, indiv['sent'][idx])] = nym #order matters
		indiv['sent'][idx] = nym
	else:
		if '-' in nym:
			multi_words = nym.split('-')
		elif '_' in nym:
			multi_words = nym.split('_')
		else:
			return indiv

		can_parse = True
		stress = ''
		for mw in multi_words:
			if mw not in d:
				can_parse = False
			else:
				stress += st.getStress(mw)  #GET THE STRESS from our other package

		if can_parse:
			# reset indiv to the correct stuff, same as line 36
			indiv['stress'][idx] = stress
			indiv['ctx'][findCtxIdx(indiv, indiv['sent'][idx])] = nym #order matters
			indiv['sent'][idx] = nym
		else:
			return indiv
 
	return indiv

def one_syllable_flipper(indiv, idx):
	#with low probability, if the sentence[idx] is a 1 syllable word, we can destress it or stress it
	#because if it were a song, we could over emphasize or emphasize it less
	if len(indiv['stress'][idx]) == 1:
		if indiv['stress'][idx] == '0':
			indiv['stress'][idx] = '1'
		else:
			indiv['stress'][idx] = '0'

	return indiv

def contracter(indiv, idx):
	#with low probability, we could just take a word that has more than one syllable and chop off the first syllable, replacing it with an '
	#would not want to do this multiple times, so only do it if the sentence[idx] doesn't contain a '
	if len(indiv['stress'][idx]) > 1 and "'" not in indiv['sent'][idx]:
		vowels = ['a', 'e', 'i', 'o', 'u', 'y']
		contraction_idx = 0
		for char in indiv['sent'][idx]:
			if char in vowels:
				break
			contraction_idx += 1
		indiv['ctx'][findCtxIdx(indiv, indiv['sent'][idx])] = "'" + indiv['sent'][idx][contraction_idx+1:] #order matters
		indiv['sent'][idx] = "'" + indiv['sent'][idx][contraction_idx+1:] #make sure this doesn't overflow
		indiv['stress'][idx] = indiv['stress'][idx][1:]
	return indiv

def mutate(indiv, idx):
	#call one mutation
	mutated_sentence = random.choice(mutations)(indiv, idx)
	return mutated_sentence

def get_likelihood_score(indiv):
	prob = 0.0
	#ngram_rev['jefferson']['thomas'] = -1.7
	#ngram['thomas']['jefferson']
	#for word in indiv['ctx']:
	for i in range(0, len(indiv['ctx']) - 1):
		word = indiv['ctx'][i].lower()
		next = indiv['ctx'][i+1].lower()
		try:
			prob += ngram[word][next]
			#print(prob)
		except:
			#print("dis not in here")
			prob += (-5)
	for i in range(1, len(indiv['ctx'])):
		word = indiv['ctx'][i].lower()
		prev = indiv['ctx'][i-1].lower()
		try:
			prob += ngram_rev[prev][word]
			#print(prob)
		except:
			#print("dis not in here")
			prob += (-5)
	prob = prob / len(indiv['ctx'])

	return 10000*(np.exp(prob))

def getLevyScore(stress, target):
	indiv_stress = ''.join((s) for s in stress)
	target_stress = ''.join((t) for t in target)

	lev_score = 10.0 - 1*(float(editdistance.eval(indiv_stress, target_stress)))
	return lev_score/10

def fitness(indiv, target):
	# metrical model score
	# first convert the sentence or target to binary 1s and 0s

	indiv_stress = ''.join((s) for s in indiv['stress'])
	target_stress = ''.join((t) for t in target)
	meter_score = (1/(float(editdistance.eval(indiv_stress, target_stress) + 1))) * 20
	
	num_beats_score = (1 / (float(abs(len(indiv_stress) - len(target_stress))) + 1)) * 30

	#likelihood score
	likelihood_score = get_likelihood_score(indiv)

	return (num_beats_score + meter_score + likelihood_score)

def diff(male, female):
	for i in range(0, len(male['sent'])):
		if male['sent'][i] != female['sent'][i]: return False
		if male['stress'][i] != female['stress'][i]: return False
	return True

def evolve(pop, target, retain=0.2, select_chance=0.05, mutate_chance=0.005):
	graded = [(fitness(x, target), x) for x in pop]

	graded = [x[1] for x in sorted(graded, reverse=True)]
	retain_length = int(len(graded)*retain)
	parents = graded[:retain_length]

	for indiv in graded[retain_length:]:
		if select_chance > random.random():
			parents.append(indiv)

	modified_parents = []
	for indiv in parents:
		if mutate_chance > random.random():
			pos_to_mutate = random.randint(0, len(indiv['sent']) - 2) # don't modify the last position
			to_mutate = copy.deepcopy(indiv)
			mutated = mutate(to_mutate, pos_to_mutate)
			modified_parents.append(mutated)
		else:
			modified_parents.append(indiv)

	parents_length = len(modified_parents)
	desired_length = len(pop) - parents_length
	children = []
	while len(children) < desired_length:
		male = random.choice(modified_parents)
		female = random.choice(modified_parents)
		if (diff(male, female)):
			child_sent = []
			child_ctx = []
			child_stress = []

			start_idx = 0
			try:
				while (male['sent'][0].lower() != male['ctx'][start_idx].lower()): start_idx += 1
			except:
				#print(male['sent'], male['ctx'])
				print("Exception: Male with Female match error")

			for i in range(0, len(male['sent'])): # assuming that our parents are all lists, which is how we should store it
				if random.random() < 0.5: # this might need to change if we add things like 'not' or we decide to delete words
					child_sent.append(male['sent'][i])
					child_stress.append(male['stress'][i])
				else:
					child_sent.append(female['sent'][i])
					child_stress.append(female['stress'][i])

			new_word_idx = 0
			child_ctx.extend(male['ctx'][:start_idx])
			child_ctx.extend(child_sent)
			child_ctx.extend(male['ctx'][start_idx+len(child_sent):])

			child = {'stress':child_stress, 'ctx':child_ctx, 'sent':child_sent}

			children.append(child)
			#print(len(children))
	modified_parents.extend(children)
	return modified_parents

mutations = [hyponym_substitution, synonym_substitution, one_syllable_flipper]
d = cmudict.dict()

if __name__ == "__main__":
	print("Hello world!")

	#t_dict = {'stress':['0', '1', '110', '0'], 'sent':['the', 'a', 'manhattan', 'dog'], 'ctx':['There', 'was', 'the', 'a', 'manhattan', 'dog', 'in', 'the', 'park']}
	#target_stress = ['1', '1', '101', '0']

	#fitness(t_dict, target_stress)

	#ny = wikipedia.page('New York')
	# sects = ny.sections #it's a list 
	# sandy_section = ny.section(ny.sections[8])

	#best_song, num_beats = music.getBestSong()
	#sample = "Jefferson was primarily of English ancestry, born and educated in Virginia. He graduated from the College of William and Mary and briefly practiced law, at times defending slaves seeking their freedom. During the American Revolution, he represented Virginia in the Continental Congress that adopted the Declaration, drafted the law for religious freedom as a Virginia legislator, and served as a wartime governor. He became the United States Minister to France in May time, and subsequently the nation's first Secretary of State a year later under President George Washington. Jefferson and James Madison organized the Democratic Republican Party to oppose the Federalist Party during the formation of the First Party System. With Madison, he anonymously wrote the Kentucky and Virginia Resolutions later, which sought to embolden states rights in opposition to the national government by nullifying the Alien and Sedition Acts. As President, Jefferson pursued the nations shipping and trade interests against Barbary pirates and aggressive British trade policies. He also organized the Louisiana Purchase, almost doubling the countries territory. As a result of peace negotiations with France, his administration reduced military forces. He was reelected at a later time. The second term of Jefferson was beset with difficulties at home, including the trial of former Vice President Aaron Burr. American foreign trade was diminished when Jefferson implemented the Embargo Act of time, responding to British threats to United States shipping. In time, Jefferson began a controversial process of Indian tribe removal to the newly organized Louisiana Territory, and he signed the Act Prohibiting Importation of Slaves in time."
	#sample = "that good old song of element we sing it oar and oar. It cheers are hearts and warms are blood to hear them shout and roar. we come from old Virginia where all is bright and gay. gets all join hands and give a yell for the dear old bread and gay"
	#sample = "The number of cells in a plant is always increasing. Plants gain energy through the sun. Their leaves have a way of absorbing sun light and converting it into sugar"
	#sample = "There are four main ways that a dog "
	#sample = "The dog walked all around the world looking for a place to eat food. It finally found a little house on the prairie. The dog walked into the house and ate some roasted chicken!"
	#sample = "The sun is a weight of heavy air that is a million miles away from the earth. Space is a vacuum that contains no molecules! When astronauts go to space, they have to wear special suits in order to not be destroyed by the powerful void. These suits have lots of features like fans and a radio"
	#sample = "Termites eat through wood two times faster when listening to rock music!\n"
	#sample = "Not all trees have all the organs or parts as mentioned above. For example, most palm trees are not branched, the cactus of North America has no functional leaves, tree ferns do not produce bark. Based on their general shape and size, all of these are nonetheless generally regarded as trees. Trees can vary very much. A plant form that is similar to a tree, but generally having smaller, multiple trunks and branches that arise near the ground, is called a shrub or a bush. Even though that is true, no precise differentiation between shrubs and trees is possible. Given their small size, bonsai plants would not technically be trees, but one should not confuse reference to the form of a species with the size or shape of individual specimens. A spruce seedling does not fit the definition of a tree, but all spruces are trees."
	sample = "Food is what people and animals eat. Food usually comes from animals or plants. It is eaten by living things to provide energy and nutrition. Food contains the nutrition that people and animals need to be healthy. Food shortage is still a big problem in the world today. Many people do not have enough money to buy the food that they need. Bad weather or other problems sometimes destroy the growing food in one part of the world. When people do not have enough food, we say that they are hungry. If they do not eat enough food for a long time, they will become sick and die from starvation."

	tup = st.getBeatFromParagraph(sample)
	#print(tup)

	#good_old_song = "that good old song of element we sing it oar and oar\nIt cheers are hearts and warms are blood to hear them shout and roar\nwe come from old Virginia where all is bright and gay\nlets all join hands and give a yell for the dear old element"
	good_old_song = "and roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\nand roar and roar and roar and roar and roar\n"
	
	#good_old_song = "Well the years start coming and they don't stop coming\nFed to the rules and I hit the ground running\nDidn't make sense not to live for fun\nYour brain gets smart but your head gets dumb\nSo much to do, so much to see\nSo what's wrong with taking the back streets\nYou never know if you do go\nYou never shine if you do glow"

	stresses = []
	num_beats = []
	for line in good_old_song.split('\n'):
		words, curr_stress = st.getBeatFromSentence(line)
		print(words, curr_stress)
		if len(curr_stress) > 0:
			stresses.append(curr_stress.split(' '))
			num_num = 0
			for striss in curr_stress.split(' '):
				num_num += len(striss)
			num_beats.append(num_num)

	print("--------------------")
	print(num_beats)
	print("------------------------")
	best_song = stresses
	pattern = st.splitBeats(tup, num_beats)
	#print(pattern)

	#for patt in pattern:
	#	print(patt[0])
	#t_dict = st.tupToDict(pattern, 1)

	dicts = []
	for i in range(0, len(pattern)):
		mini_dict = st.tupToDict(pattern, i)
		dicts.append(mini_dict)

	pre_score = 0.0
	for i in range(0, len(dicts)):
		#print("--------------------------")
		#print(dicts[i]['sent'])
		#print("--------------------------")
		pre_score += getLevyScore(dicts[i]['stress'], stresses[0])

	pre_score /= len(dicts)
	print("The pre score is: " + str(pre_score))
	#print(dicts)

	# call divyas function, pass in dicts[i], and dicts[i+1]
	rhyme_dicts = []
	print("About to create our rhymes!")
	total = 0
	rhymed = 0
	for i in range(0, len(dicts) - 1, 2):
		if i < len(dicts) - 1:
			#print('we in here')
			rhyme_dict1, rhyme_dict2,b = rhymer.driverDriver(dicts[i], dicts[i+1])
			if b = True:
				rhymed += 1
			total += 1
			#print(dicts[i]['sent'][0], dicts[i+1]['sent'][0])
			for wrd in rhyme_dict1['sent']:
				if wrd not in rhyme_dict1['ctx']: rhyme_dict1['ctx'].append(wrd)
			for wrd in rhyme_dict2['sent']:
				if wrd not in rhyme_dict2['ctx']: rhyme_dict2['ctx'].append(wrd)
			rhyme_dicts.append(rhyme_dict1)
			rhyme_dicts.append(rhyme_dict2)
		else:
			rhyme_dicts.append(dicts[i])
	print("Just created our rhymes!")

	for rhym in rhyme_dicts:
		print(rhym['sent'])
	count = 0
	evolved_sents = []
	z = 0

	sents_over_time = {}
	for t_dict in rhyme_dicts: #not rhyme dicts for now
		pop = population(t_dict)
		#print(best_song)
		if count == len(num_beats):
			count = 0
		target = best_song[count]

		k = evolve(pop, target)
		#print(k[0]['sent'])
		#print(fitness(t_dict, best_song[0]))
		sub_score = 0.0
		for i in range(0, 300):
			pop = evolve(pop, target)
			if i % 5 == 0:
				graded = [(fitness(x, target), x) for x in pop]
				graded = [x[1] for x in sorted(graded)]
				if i in sents_over_time:
					sents_over_time[i].append(graded[40])
				else:
					sents_over_time[i] = [graded[40]]

		target_str = ''.join((target[j]) for j in range(0, len(target)))
		#print("TARGET STR: " + target_str)
		for i in range(len(pop)):
			#print(pop[i]['sent'])
			curr_str = ''.join((pop[i]['stress'][j]) for j in range(0, len(pop[i]['stress'])))
			#print("CURRENT BEAT: " + curr_str)

		graded = [(fitness(x, target), x) for x in pop]
		graded = [x[1] for x in sorted(graded)]

		
		#print(graded[0]['sent'])
		#print(fitness(graded[0], target))
		best_beat = ' '.join((graded[-1]['stress'][j]) for j in range(0, len(graded[-1]['stress'])))

		best_str = ' '.join((graded[-1]['sent'][j]) for j in range(0, len(graded[-1]['sent'])))
		evolved_sents.append((best_str, graded[-1]['stress']))

		#print("BEST STR: " + best_str)
		count += 1
		#print(fitness(graded[99], target))
	idx_2 = 0
	post_score = 0.0

	for evo in evolved_sents:
		print(evo[0])
	"""
	for evo in evolved_sents:
		print(stresses[idx_2])
		post_score += getLevyScore(evo[1], stresses[0])
		print(evo)
		idx_2 += 1
		if (idx_2 == len(stresses)):
			idx_2 = 0
	post_score /= len(evolved_sents)

	print(post_score)

	for sent in range(0, 1000, 10):
		sub_sum = 0
		for rul in sents_over_time[sent]:
			sub_sum += getLevyScore(rul['stress'], stresses[0])
		#print("--------------------------------------")
		print(sub_sum / len(sents_over_time[sent]))
		#print("--------------------------------------")
	"""
