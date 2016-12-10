import lyricwikia
import pylast
import nltk
from nltk.corpus import cmudict
from sets import Set
import string
import stress as st

puncts = Set(string.punctuation)

API_KEY = "ce0d2b3398a8f472db3b8d3eecdc598f" # this is a sample key
API_SECRET = "291f72293c887d6cb2747fc4cb28657c"

#username = "naveenkiyer"
#password_hash = pylast.md5("myPassword")

network = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SECRET)

artists = network.get_top_artists(limit=1) #[2].item

d = cmudict.dict()

def getBestSong():
	a_dict = {}
	for artist in artists:
		#print(artist.item)
		a_dict[str(artist.item)] = []
		tracks = artist.item.get_top_tracks()
		for track in tracks:
			a_dict[str(artist.item)].append(str(track.item).split('-')[1].strip())

	fout = open('artist-song.txt', 'w')

	lyrics = []

	for a in a_dict:
		for t in a_dict[a]:
			#fout.write(a + "~" + t + '\n')
			try:
				lyric = lyricwikia.get_lyrics(a, t)
				lyrics.append(lyric)
				#print("Success!")
			except:
				print("This song was not found: " + t + "by " + a)

	for l in lyrics:
		in_dict = 0.0
		total = 0.0
		for w in nltk.word_tokenize(l):
			word = w.lower()
			if word in d:
				in_dict += 1
			if word not in puncts:
				total += 1
		perc = (in_dict / total) * 100

	best_song = lyrics[0].split('\n')

	stresses = []
	num_beats = []
	for line in best_song:
		words, curr_stress = st.getBeatFromSentence(line)
		if len(curr_stress) > 0:
			stresses.append(curr_stress.split(' '))
			num_beats.append(len(curr_stress.split(' ')))

	return stresses, num_beats

#print(stresses)
#for l in stresses:
#	print(l)

#print(a_dict)
#track = artist.get_top_tracks()[70].item
#print(str(track).split('-')[1].strip())


