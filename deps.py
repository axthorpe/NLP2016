import nltk
from nltk.corpus import wordnet
from nltk.wsd import lesk
import shlex
from subprocess import Popen, PIPE
from spacy.en import English
from nltk.corpus import cmudict
import pickle
import spacy
import copy
from nltk import Tree
from nltk.parse.stanford import StanfordParser
stanford_parser_dir = '/home/stanford/'
eng_model_path = "/home/divya/stanford/englishRNN.ser.gz"
my_path_to_models_jar = "/home/divya/stanford/tools/stanford-parser-full-2015-12-09/stanford-parser-3.6.0-models.jar"
my_path_to_jar = "/home/divya/stanford/tools/stanford-parser-full-2015-12-09/stanford-parser.jar"
parser=StanfordParser(model_path=eng_model_path, path_to_models_jar=my_path_to_models_jar, path_to_jar=my_path_to_jar)


nlp = English()
file1 = open('word_to_rhyme_group.pickle', 'rb')
w2r_data = pickle.load(file1)
file1.close()
file2 = open('rhyme_groups.pickle', 'rb')
rg_data = pickle.load(file2)
file2.close()
print_script = ''