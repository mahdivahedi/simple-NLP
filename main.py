from typing import List
from collections import defaultdict

LANDAS = [0.8, 0.1, 0.1]
EPSILON = 0.00001

start = '<s> '
end = ' <\s>'


def create_dict(sentences: List[str]):
	l = []
	curpus = ' - '.join(sentences)
	words = curpus.split()
	for word in words:
		if word not in ['-', '<s>', '<\s>'] :
			if (curpus.count(word) > 1) and (curpus.count(word) < 9000):
			    if word not in l:
			    	l.append(word)
	return l

def read_input(path):
	with open(path, 'r', encoding="utf-8") as f:
		sentences = f.readlines()
		edit_sentences(sentences)
		dictionary = create_dict(sentences)
		# sentences = unkonwn_finder(sentences)
		return {
			"dict": dictionary,
			"sentences": sentences
		}

def edit_sentences(sentences: List[str]):
	for i in range(len(sentences)):
		sentences[i] = sentences[i].replace("?", " ")
		sentences[i] = sentences[i].replace(":", " ")
		sentences[i] = sentences[i].replace("؟", " ")
		sentences[i] = sentences[i].replace("،", " ")
		sentences[i] = sentences[i].replace("*", " ")
		sentences[i] = sentences[i].replace("\"", " ")
		sentences[i] = sentences[i].replace("--", " ")
		sentences[i] = sentences[i].replace("-", " ")
		sentences[i] = sentences[i].replace("!", " ")
		sentences[i] = sentences[i].strip()
		while '  ' in sentences[i]:
			sentences[i] = sentences[i].replace('  ', ' ')
		sentences[i] = start + sentences[i] + end


def generate_unigram(sentences: List[str]):
	grams = []
	for sentence in sentences:
		words = sentence.split()
		for i in range(1, len(words) - 1):
			gram = words[i:i + 1]
			if gram not in grams:
				grams.append(gram)
	return grams

def generate_bigram(sentences: List[str]):
	grams = []
	for sentence in sentences:
		words = sentence.split()
		for i in range(0, len(words) - 2):
			gram = words[i:i + 2]
			if gram not in grams:
				grams.append(gram)
	return grams

def generate_bigram_for_query(sentence: str):
	grams = []
	words = sentence.split()
	for i in range(0, len(words) - 2):
		gram = words[i:i + 2]
		grams.append(gram)
	return grams

def learn(sentences: List[str]):
	unigrams = defaultdict(lambda: 0)
	bigrams = defaultdict(lambda: defaultdict(lambda: 0))
	p_unigrams = defaultdict(lambda: 0)
	p_bigrams = defaultdict(lambda: defaultdict(lambda: 0 ))
	text = ' '.join(sentences)
	size = len(text.split()) - len(sentences) * 2
	for k in generate_unigram(sentences):
		 unigrams[k[0]] += text.count(k[0])
		 p_unigrams[k[0]] = unigrams[k[0]] / size
	unigrams['<s>'] = len(sentences)
 
	for k in generate_bigram(sentences):
		 tmp = ' '.join(k)
		 bigrams[k[0]][k[1]] = text.count(tmp)
		 p_bigrams[k[0]][k[1]] = bigrams[k[0]][k[1]] / unigrams[k[0]]

	return{
		"unigram" : p_unigrams,
		"bigram": p_bigrams
	}
def backoff_model(unigram, bigram, words):
	return bigram[words[0]][words[1]] * LANDAS[0] + unigram[words[1]] * LANDAS[1] + EPSILON * LANDAS[2]

def read_test_set():
	neg_test_sentences = []
	pos_test_sentences = []
	with open("corpus/test_filen.txt", "r", encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			neg_test_sentences.append(line)
		edit_sentences(neg_test_sentences)
	with open("corpus/test_filep.txt", "r", encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			pos_test_sentences.append(line)
		edit_sentences(pos_test_sentences)
	return {
		"pos_test_sentences": pos_test_sentences,
		"neg_test_sentences": neg_test_sentences
	}
	
if __name__=="__main__":
	pos = read_input("/home/meyti/Documents/AI/Projects/AI_P4/rt-polarity.pos")
	pos_model = learn(pos["sentences"])
	pos_unigram = pos_model["unigram"]
	pos_bigram = pos_model["bigram"]


	neg = read_input("/home/meyti/Documents/AI/Projects/AI_P4/rt-polarity.neg")
	neg_model = learn(neg["sentences"])
	neg_unigram = neg_model["unigram"]
	neg_bigram = neg_model["bigram"]
	print("Train completed...")
	inp = input()
	n_value = 0.5
	p_value = 0.5
	while(inp!="!q"):
	    for k in generate_bigram_for_query(inp):
        	 p_value *= backoff_model(pos_unigram, pos_bigram, k)
	      n_value *= backoff_model(neg_unigram, neg_bigram, k)

	    print(p_value,n_value)
	    if p_value >= n_value:
	        print("not filter this")
	    else:
	        print("filter this")
	    print(">",end=" ")
	    inp = input()

