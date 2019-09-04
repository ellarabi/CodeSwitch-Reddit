import csv, sys
import numpy as np
from scipy.stats import spearmanr
from scipy.stats import pearsonr
from scipy.stats import wilcoxon
from nltk.tokenize import word_tokenize
sys.path.append('../')
from utils import Serialization


class Formality():
    """
    testing (in)formality differences in code-swithced vs. monolingual english texts
    by the same set of users; pair-wise wilcoxon rank-sum test is used
    """

    @staticmethod
    def load_formality_markers():
        """
        assumes a list of token+score list extracted from the  formal-informal GYAFC parallel dataset
        ("Dear Sir or Madam, May I Introduce the GYAFC Dataset: Corpus, benchmarks and metrics for formality
        style transfer.", Sudha Rao and Joel Tetreault, 2018)

        extracts a list of (in)formality markers from a pre-computed list of all tokens+scores
        a strict threshold of -5.0 was used for this analysis (configurable)
        :return: a list of (in)formality markers
        """
        markers = []
        filename = 'formality.logodds.out'
        with open(filename, 'r') as fin:
            for line in fin:
                tokens = line.split()
                if len(tokens) < 2: continue
                if tokens[0].isdigit(): continue
                if float(tokens[1]) < LOG_ODDS_THRESHOLD: markers.append(tokens[0])
            # end for
        # end with
        print('loaded', len(markers), 'informality markers')
        return markers
    # end def

    @staticmethod
    def load_data(filename, common_users):
        """
        generates a dictionary of user to all their (cs or monolingual) posts
        :param filename: csv file with user posts
        :param common_users: a list of users who have both cs and monolingual texts
        :return: user to posts map
        """
        texts = {}
        with open(filename, 'r') as fin:
            print('reading', filename)
            csv_reader = csv.reader(fin, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header = csv_reader.__next__()
            for line in csv_reader:
                if len(line) < 8: continue
                if len(line[7].split()) < MIN_SENTENCE_LENGTH: continue
                author = line[0].strip()
                if author not in common_users: continue

                text_by_author = texts.get(author, [])
                text_by_author.append(' '.join(word_tokenize(line[7].strip().lower())))
                texts[author] = text_by_author
            # end for
        # end with

        object_name = '<cs or monolingual texts by author>'
        Serialization.save_obj(texts, object_name)
        return texts

    # end def

    @staticmethod
    def extract_markers(cs_texts, non_cs_texts, markers):
        """
        extracts two lists of per-user frequencies: (in)formality markers in their cs and monolingual texts
        :param cs_texts: user to cs posts dictionary
        :param non_cs_texts: user to monolingual posts dictionary
        :param markers: list of (in)formality markers to consider
        :return: two lists of per-author frequencies
        """
        cs_markers_frequency = []
        non_cs_markers_frequency = []
        ranks = Serialization.load_obj('dict.ranks')
        for author in cs_texts:
            if len(cs_texts[author].split()) > MIN_POSTS_PER_USER and \
                    len(non_cs_texts.get(author, '').split()) > MIN_POSTS_PER_USER:
                cs_markers_frequency.append(Formality.count_markers(cs_texts[author], markers, ranks))
                non_cs_markers_frequency.append(Formality.count_markers(non_cs_texts[author], markers, ranks))
            # end if
        # end for
        print('extracted informality markers', len(cs_markers_frequency))
        return cs_markers_frequency, non_cs_markers_frequency
    # end def

    @staticmethod
    def count_markers(text, markers, ranks):
        """
        computes frequency of (in)formality markers in a given text
        :param text: post text
        :param markers: a list of markers to consider
        :param ranks: english frequency word-rank dictionary
        :return: (in)formality markers frequency
        """
        indicators = []
        for token in text.lower().split():
            if ranks.get(token, sys.maxsize) > MAX_WORD_RANK and token not in markers: continue
            indicators.append(1 if token in markers else 0)
        # end for
        return float(sum(indicators))/len(indicators)
    # end def

    @staticmethod
    def test_formality_difference():
        """
        extracts two lists of per-user (in)formality markers frequency and
        performs Wilcoxon pair-wise significance test for difference
        """
        markers = Formality.load_formality_markers()
        cs_object_name = '<pickle object with map: author to cs texts>'
        non_cs_object_name = '<pickle object with map: author to monolingual english texts>'
        cs_texts = Serialization.load_obj(cs_object_name)
        non_cs_texts = Serialization.load_obj(non_cs_object_name)
        print('loaded', len(cs_texts), 'and', len(non_cs_texts), 'cs and monolingual english by authors')
        for author in cs_texts: cs_texts[author] = ' '.join(cs_texts[author])
        for author in non_cs_texts: non_cs_texts[author] = ' '.join(non_cs_texts[author])

        cs_markers_by_authors, non_cs_markers_by_authors = Formality.extract_markers(cs_texts, non_cs_texts, markers)
        #print(cs_markers_by_authors, non_cs_markers_by_authors)

        print('mean markers frequency in cs:', np.mean(cs_markers_by_authors),
              'in non-cs:', np.mean(non_cs_markers_by_authors))

        Serialization.save_obj(cs_markers_by_authors, 'formality.markers.cs')
        Serialization.save_obj(non_cs_markers_by_authors, 'formality.markers.non-cs')
        stat, pval = wilcoxon(cs_markers_by_authors, non_cs_markers_by_authors)
        print('paired ttest sig test pval:', pval, stat)

        mean1 = np.mean(cs_markers_by_authors); mean2 = np.mean(non_cs_markers_by_authors)
        std1 = np.std(cs_markers_by_authors); std2 = np.std(non_cs_markers_by_authors)
        r1, _ = spearmanr(cs_markers_by_authors, non_cs_markers_by_authors)
        r2, _ = pearsonr(cs_markers_by_authors, non_cs_markers_by_authors)
        print(mean1, mean2, std1, std2, r1, r2)

    # end def

# end class


MAX_WORD_RANK = 10000
MIN_SENTENCE_LENGTH = 10
LOG_ODDS_THRESHOLD = -5.0
MIN_POSTS_PER_USER = 100

if __name__ == '__main__':
    Formality.test_formality_difference()

# end def
