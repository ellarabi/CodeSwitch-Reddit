import re
import sys, csv
from scipy.stats import ranksums
from scipy.stats import sem
from nltk.tokenize import word_tokenize
from random import shuffle
import numpy as np

import benepar
from polyglot.detect import Detector
from en_function_words import FUNCTION_WORDS
import countries

sys.path.append('../')
from utils import Serialization


class DataProcessing:
    @staticmethod
    def read_data(filename):
        """
        collect user data from all but country-specific subreddits
        :param filename: a csv file with posts by all users subject for texting
        :return: user to posts dictionary, subreddits list
        """
        data = {}
        subreddits = []
        with open(filename, 'r') as fin:
            csv_reader = csv.reader(fin, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for line in csv_reader:
                if len(line) < 4: continue
                # filter out all country-specific subreddits
                if line[1].strip().lower() in countries.COUNTRIES: continue
                subreddits.append(line[1].strip())

                author = line[0].strip()

                authors_texts = data.get(author, [])
                authors_texts.append(line[3].strip())
                data[author] = authors_texts
            # end for
        # end with
        return data, subreddits
    # end def

    @staticmethod
    def read_non_native_authors():
        """
        return a list of non-native Reddit users as extracted from the dataset in
        "Native Language Cognate Effects on Second Language Lexical Choice", Rabinovich et al., 2018
        https://www.mitpressjournals.org/doi/abs/10.1162/tacl_a_00024
        :return:
        """
        filename = '<a filename with a list of non-native english authors>'
        with open(filename, 'r') as fin:
            authors = [line.strip() for line in fin]
        # end with
        return authors
    # end def

    @staticmethod
    def load_concreteness_scores(filename):
        """
        :param filename: a file with english words concreteness score
        :return: word to score dictionary
        """
        data = {}
        with open(filename, 'r') as fin:
            csv_reader = csv.reader(fin, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header = csv_reader.__next__()
            for line in csv_reader:
                if len(line) < 2: continue
                data[line[0].strip()] = float(line[1])
            # end for
        # end with
        return data
    # end def

    @staticmethod
    def load_aoa_scores(filename):
        """
        :param filename: a file with english words AoA score
        :return: word to score dictionary
        """
        data = {}
        with open(filename, 'r') as fin:
            csv_reader = csv.reader(fin, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header = csv_reader.__next__()
            for line in csv_reader:
                if len(line) < 3: continue
                data[line[0].strip()] = float(line[2])
            # end for
        # end with
        return data
    # end def

    @staticmethod
    def filter_out_non_english_posts(dataobject):
        """
        given a list of posts, filter in clean monolingual english posts
        :param dataobject: user to posts object
        :return: user to posts clean dictionary
        """
        clean_data = {}
        data = Serialization.load_obj(dataobject)
        for author in data:
            print('processing:', author)
            author_eng_posts = []
            for post in data[author]:
                sentences = []
                for sentence in re.split('\.|\! |\? |\n', post):
                    if len(sentence.split()) < 10: continue
                    try: detector = Detector(sentence)
                    except: continue

                    if detector.languages[0].name == 'English' and \
                            detector.languages[0].confidence > DETECTOR_CONFIDENCE:
                        sentences.append(sentence)
                    # end if
                # end for
                if len(sentences) == 0: continue
                author_eng_posts.append('. '.join(sentences))
            # end for
            if len(author_eng_posts) == 0: continue
            clean_data[author] = author_eng_posts
        # end for

        Serialization.save_obj(clean_data, dataobject+'.clean')
        for author in clean_data:
            print(author, len(clean_data[author]))
        # end for

    # end def

# end class


class Proficiency:
    @staticmethod
    def load_data(file_cs, file_monolingual):
        """
        loads posts by code-switchers and noncode-switchers
        :param file_cs: a csv file with posts by frequent code-switching users
        :param file_monolingual: a csv file with posts by user who don't (or very rarely) code-switch
        :return:
        """
        data_cs, subreddits_cs = DataProcessing.read_data(file_cs)
        data_monolingual, subreddits_monolingual = DataProcessing.read_data(file_monolingual)

        subreddits = subreddits_cs
        subreddits.extend(subreddits_monolingual)
        subreddits = set(subreddits)

        Serialization.save_obj(data_cs, DATA_CS)
        Serialization.save_obj(data_monolingual, DATA_MONOLINGUAL)
        print('code-switchers:', len(data_cs), 'non-code-switchers:', len(data_monolingual))
        print('total subreddits:', len(subreddits))
    # end def

    @staticmethod
    def norm_type_to_token_ratio(tokens):
        """
        extracts normalized (moving average) type-to-token ratio for a list of tokens
        see e.g., http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.248.5206&rep=rep1&type=pdf
        :param tokens: a list fo tokens
        :return: normalized type-to-token ratio
        """
        nttrs = []
        STTY_STEP = 1000
        if len(tokens) < STTY_STEP: return None
        for i in range(0, len(tokens)-STTY_STEP, STTY_STEP):
            current_batch = tokens[i:i+STTY_STEP]
            nttrs.append(float(len(set(current_batch)))/len(current_batch))
        # end for
        return np.mean(nttrs)
    # end def

    @staticmethod
    def mean_word_length(tokens):
        """
        computes mean word length ina given text
        :param tokens: a list of tokens
        :return: mean word length
        """
        lengths = [len(token) for token in tokens]
        return float(sum(lengths))/len(lengths)
    # end def

    @staticmethod
    def lexical_density(tokens):
        """
        computes the # of content (not functional) to total # of words
        :param tokens: a list of tokens
        :return: lexical density
        """
        content = [1 if token not in FUNCTION_WORDS else 0 for token in tokens]
        return float(sum(content))/len(tokens)
    # end def

    @staticmethod
    def average_age_of_acquisition(tokens):
        """
        computes AoA for a given list of tokens
        :param tokens: a list of tokens
        :return: AoA
        """
        rates = []
        for token in tokens:
            if token not in aoa.keys(): continue
            rates.append(aoa[token])
        # end for
        return np.mean(rates)

    # end def

    @staticmethod
    def mean_word_concreteness(tokens):
        """
        computes mean concreteness score for a given token list
        :param tokens: a list of tokens
        :return: mean concreteness
        """
        rates = []
        for token in tokens:
            if token not in concreteness.keys(): continue
            rates.append(concreteness[token])
        # end for
        return np.mean(rates)
    # end def

    @staticmethod
    def compute_lexical_metrics(texts):
        """
        given user posts, concatenates them and computes all lexical metrics
        :param texts: user posts
        :return: an array of lexical metrics
        """
        clean_tokens = []
        clean_content_tokens = []
        tokenized = word_tokenize(' '.join(texts).lower())

        for token in tokenized:
            if ranks.get(token, sys.maxsize) > MAX_WORD_RANK: continue
            if not token.isalpha(): continue # consider only words
            clean_tokens.append(token)
            if token in FUNCTION_WORDS: continue
            clean_content_tokens.append(token)
        # end for

        nttr = Proficiency.norm_type_to_token_ratio(clean_content_tokens)
        mean_aoa = Proficiency.average_age_of_acquisition(clean_content_tokens)
        mean_concreteness = Proficiency.mean_word_concreteness(clean_content_tokens)
        mean_length = Proficiency.mean_word_length(clean_content_tokens)
        # consider all tokens (content and functional)
        lexical_density = Proficiency.lexical_density(clean_tokens)

        return [nttr, lexical_density, mean_aoa, mean_concreteness, mean_length]

    # end def

    @staticmethod
    def mean_sentence_length(sentences):
        """
        computes mean sentence length for a list of sentences
        :param sentences: a list of sentences
        :return: mean length
        """
        lengths = [len(sentence.split()) for sentence in sentences]
        return np.mean(lengths)
    # end def

    @staticmethod
    def get_tree_depth(tree):
        """
        computes max parsing tree depth given a tree
        :param tree: parsing tree
        :return: max depth
        """
        positions = []
        leaves = len(tree.leaves())
        leavepos = set(tree.leaf_treeposition(n) for n in range(leaves))
        for pos in tree.treepositions():
            if pos not in leavepos:
                positions.append(len(pos))
            # end if
        # end for
        return max(positions)
    # end def

    @staticmethod
    def parsing_metrics(parser, sentences):
        """
        computes mean max parsing tree depth and the total # of clauses in a sentence
        :param parser: parser
        :param sentences: a list of sentences
        :return: metrics
        """
        shuffle(sentences)
        clauses = []; depths = []
        for sentence in sentences[:500]:
            sentence_clauses = 0
            try:
                tree = parser.parse(sentence)
            except ValueError as exception:
                print(exception)
                continue
            # end try

            for subtree in tree.subtrees():
                if subtree.label() in ['S', 'SBAR', 'SBARQ']:
                    sentence_clauses += 1
                # end if
            # end for
            clauses.append(sentence_clauses if sentence_clauses > 0 else 1)
            depths.append(Proficiency.get_tree_depth(tree))
        # end for

        return np.mean(clauses), np.mean(depths)
    # end def

    @staticmethod
    def compute_grammatical_metrics(texts):
        """
        given user posts, concatenates them and computes all grammatical metrics
        :param texts: user posts
        :return: an array of grammatical metrics
        """
        sentences = []
        parser = benepar.Parser("benepar_en2")
        for sentence in re.split('\.|\! |\? |\n', '\n'.join(texts)):
            sentence = re.sub(r'\s+', ' ', sentence).strip()
            if len(sentence.split()) < 3 or len(sentence.split()) > 70: continue
            sentences.append(' '.join(word_tokenize(sentence)))
        # end for

        mean_num_of_clauses, mean_tree_depth = Proficiency.parsing_metrics(parser, sentences)
        mean_length = Proficiency.mean_sentence_length(sentences)

        return [mean_num_of_clauses, mean_tree_depth, mean_length]

    # end def

    @staticmethod
    def extract_proficiency_metrics(objname):
        """
        extract lexical and grammatical proficiency metrics given user to posts data
        :param objname: pickle object with user to posts data
        :return:
        """
        metrics = {}
        data = Serialization.load_obj(objname)

        for author in data:
            if len(data[author]) < MIN_POSTS_FOR_TEST: continue
            metrics[author] = Proficiency.compute_lexical_metrics(data[author])
            metrics[author].extend(Proficiency.compute_grammatical_metrics(data[author]))
            print(author, metrics[author]); sys.stdout.flush()
        # end for
        Serialization.save_obj(metrics, objname.replace('data', 'metrics.lex.gramm.clean'))
        print(len(metrics))
    # end def

    @staticmethod
    def estimate_average_and_significance(metrics_obj):
        """
        extracts mean and standard error of users' proficiency metrics
        :param metrics_obj: a pickle object name with extracted proficiency metrics per user
        :return: an N*M matrix where N is the # of metrics and M is the # of users
        """
        values = []
        metrics = Serialization.load_obj(metrics_obj)
        for author in metrics: values.append(metrics[author])
        values = np.matrix(values)

        print('ntty, lexical density, mean AoA,', 'mean concreteness,', 'mean word length,',
              'mean clauses,', 'mean tree depth,', 'mean sent length')

        flats = []
        for i in range(1, values.shape[1]):
            flat = []
            for val in values[:, i]: flat.append(float((val)[0]))
            print('{0:.3f}'.format(np.mean(values[:, i])), '\t', '{0:.3f}'.format(sem(flat)))
            flats.append(flat)
        # end for
        return flats

    # end def

# end class


MAX_WORD_RANK = 10000
MIN_POSTS_FOR_TEST = 50
DATA_CS = 'data.cs.by.author'
DATA_MONOLINGUAL = 'data.monolingual.by.author'
DATA_CS_CLEAN = 'data.cs.by.author.clean'
DATA_MONOLINGUAL_CLEAN = 'data.monolingual.by.author.clean'
METRICS_CS = 'metrics.lex.gramm.clean.cs.by.author'
METRICS_MONOLINGUAL = 'metrics.lex.gramm.clean.mono.by.author'

DETECTOR_CONFIDENCE = 90

non_natives = DataProcessing.read_non_native_authors()
ranks = Serialization.load_obj('dict.ranks')
filename = '<a file with english words concreteness ratings>'
concreteness = DataProcessing.load_concreteness_scores(filename)
filename = '<a file with english words AoA ratings>'
aoa = DataProcessing.load_aoa_scores(filename)

if __name__ == '__main__':
    """
    assumes polyglot language detector and benepar parser installed
    https://polyglot.readthedocs.io/en/latest/Detection.html
    https://pypi.org/project/benepar/
    """

    file_cs = '<a csv file with cs posts>'
    file_monolingual = '<a csv file with monolingual english posts>'
    Proficiency.load_data(file_cs, file_monolingual)

    Proficiency.extract_proficiency_metrics(DATA_CS_CLEAN)
    Proficiency.extract_proficiency_metrics(DATA_MONOLINGUAL_CLEAN)

    DataProcessing.filter_out_non_english_posts(DATA_MONOLINGUAL)

    cs_flats = Proficiency.estimate_average_and_significance(METRICS_CS)
    monolingual_flats = Proficiency.estimate_average_and_significance(METRICS_MONOLINGUAL)

    for i in range(len(cs_flats)):
        _, pval = ranksums(cs_flats[i], monolingual_flats[i])
        print(i, pval)
    # end for

# end if
