# Parsing:
from nltk.parse.stanford import StanfordParser

stanford_parser_dir = '/home/stanford/'
eng_model_path = "/home/divya/stanford/englishRNN.ser.gz"
my_path_to_models_jar = "/home/divya/stanford/tools/stanford-parser-full-2015-12-09/stanford-parser-3.6.0-models.jar"
my_path_to_jar = "/home/divya/stanford/tools/stanford-parser-full-2015-12-09/stanford-parser.jar"

parser=StanfordParser(model_path=eng_model_path, path_to_models_jar=my_path_to_models_jar, path_to_jar=my_path_to_jar)

tre = parser.raw_parse("the quick brown fox jumps over the lazy dog")
tre.next().pretty_print()
