import sys
import math
import codecs
import argparse
from collections import Counter
from collections import defaultdict

from nltk.tokenize import word_tokenize


parser = argparse.ArgumentParser(
	description='computes the weighted log-odds-ratio, informative dirichlet prior algorithm')
parser.add_argument('-f', '--first', help='description for first counts file ')
parser.add_argument('-s', '--second', help='description for second counts file')
parser.add_argument('-p', '--prior', help='description for prior counts file')
parser.add_argument('--out_file', type=argparse.FileType('w'), default=sys.stdout)
parser.add_argument('--min_count', default=0)
parser.add_argument('--stopwords')
args = parser.parse_args()


def load_counts(filename, min_count=0, stopwords=set()):
	result = defaultdict(int)
	with codecs.open(filename, 'r', 'utf-8') as fin:
		word_counts = Counter(fin.read().split())

	for word, count in word_counts.items():
		if count >= min_count and word not in stopwords:
			result[word] = count
		# end if
	# end for
	print('# of keys in', filename, len(result.keys()))
	return result
# end def


def load_stopwords(filename):
	stopwords = set()
	for line in open(filename):
		for word in line.split():
			if word: stopwords.add(word)
		# end for
	# end for
	return stopwords
# end def


def compute_log_odds(counts1, counts2, prior):
	sigmasquared = defaultdict(float)
	sigma = defaultdict(float)
	delta = defaultdict(float)

	for word in prior.keys(): prior[word] = int(prior[word] + 0.5)

	for word in counts2.keys():
		counts1[word] = int(counts1[word] + 0.5)
		if prior[word] == 0: prior[word] = 1
	# end for

	for word in counts1.keys():
		counts2[word] = int(counts2[word] + 0.5)
		if prior[word] == 0: prior[word] = 1
	# end for

	n1 = sum(counts1.values())
	n2 = sum(counts2.values())
	nprior = sum(prior.values())

	for word in prior.keys():
		if prior[word] > 0:
			l1 = float(counts1[word] + prior[word]) / ((n1 + nprior) - (counts1[word] + prior[word]))
			l2 = float(counts2[word] + prior[word]) / ((n2 + nprior) - (counts2[word] + prior[word]))
			sigmasquared[word] = 1 / (float(counts1[word]) + float(prior[word])) + 1 / (
			float(counts2[word]) + float(prior[word]))
			sigma[word] = math.sqrt(sigmasquared[word])
			delta[word] = (math.log(l1) - math.log(l2)) / sigma[word]
		# end if
	# end for
	return delta
# end def


def main():
	stopwords = set()
	if args.stopwords:
		stopwords = load_stopwords(args.stopwords)
	else:
		print("not using stopwords")

	counts1 = load_counts(args.first, 0, stopwords)
	counts2 = load_counts(args.second, 0, stopwords)
	prior = load_counts(args.prior, args.min_count, stopwords)

	delta = compute_log_odds(counts1, counts2, prior)

	for word, log_odds in sorted(delta.items(), key=lambda x: x[1]):
		args.out_file.write("{}\t{:.3f}\n".format(word, log_odds))
	# end for

# end def


def preprocess_data(filename):
	with open(filename, 'r') as fin, open(filename+'.tok', 'w') as fout:
		for line in fin:
			fout.write(' '.join(word_tokenize(line.strip().lower())) + '\n')
		# end for
	# end with
# end def


if __name__ == '__main__':
	main()

# end if
