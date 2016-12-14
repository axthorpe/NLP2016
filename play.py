cd $HOME

# Update / Install NLTK
pip install -U nltk

# Download the Stanford NLP tools
wget http://nlp.stanford.edu/software/stanford-ner-2015-12-09.zip
wget http://nlp.stanford.edu/software/stanford-postagger-full-2015-12-09.zip
wget http://nlp.stanford.edu/software/stanford-parser-full-2015-12-09.zip
# Extract the zip file.
unzip stanford-ner-2015-12-09.zip 
unzip stanford-parser-full-2015-12-09.zip 
unzip stanford-postagger-full-2015-12-09.zip


export STANFORDTOOLSDIR=$HOME/stanford/tools

export CLASSPATH=$STANFORDTOOLSDIR/stanford-postagger-full-2015-12-09/stanford-postagger.jar:$STANFORDTOOLSDIR/stanford-ner-2015-12-09/stanford-ner.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-12-09/stanford-parser.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-12-09/stanford-parser-3.6.0-models.jar

export STANFORD_MODELS=$STANFORDTOOLSDIR/stanford-postagger-full-2015-12-09/models:$STANFORDTOOLSDIR/stanford-ner-2015-12-09/classifiers