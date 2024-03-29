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
import sys

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

	information = str(sys.argv[1])
	# will take wikipedia as first thing
	wiki_info = wikipedia.page(information)
	section = wiki_info.section(wiki_info.sections[8])

	# will select the number one trending song as of now
	best_song, num_beats = music.getBestSong()
	
	best_song = stresses
	pattern = st.splitBeats(tup, num_beats)

	dicts = []
	for i in range(0, len(pattern)):
		mini_dict = st.tupToDict(pattern, i)
		dicts.append(mini_dict)

	pre_score = 0.0
	for i in range(0, len(dicts)):
		pre_score += getLevyScore(dicts[i]['stress'], stresses[0])

	pre_score /= len(dicts)
	print("The pre score is: " + str(pre_score))

	rhyme_dicts = []
	total = 0.0
	rhymed = 0
	for i in range(0, len(dicts) - 1, 2):
		if i < len(dicts) - 1:
			#print('we in here')
			rhyme_dict1, rhyme_dict2,b = rhymer.driverDriver(dicts[i], dicts[i+1])
			if b == True:
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
	percent_rhyme = rhymed/total
	print("PERCENT RHYME: " + str(percent_rhyme))
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
