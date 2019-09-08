import pandas as pd
from collections import Counter
import re
from en_function_words import FUNCTION_WORDS
import operator
from nltk.corpus import words
from string import punctuation
regex = re.compile('[%s]' % re.escape(punctuation))

common_words = set(words.words())
FUNCTION_WORDS = set(FUNCTION_WORDS)

"""
A script to identify words that would indicate that a post is a translation post
"""


def clean_string(string):
    """
    Helper function to clean a string and tokenize it
        :param string: str
            The str to clean by removing punctuation
        :return: list
            Cleaned list of tokens to be returned
    """

    global regex
    string = string.lower()
    string = re.sub('&.*;', ' ', string)
    string = regex.sub("", string)
    string_list = string.split()

    return string_list


def count_words(lst):
    """
    Get word count from list of posts
    :param lst: list or array
    :return: Counter
    """
    word_counter = Counter()
    for post in lst:
        string_list = clean_string(post)
        final_words = filter_words(string_list)
        word_counter.update(final_words)
    return word_counter


def compute_probability(word, joined_count, counter2):
    """
    Compute conditional probability given
    :param joined_count:
    :param word:
    :param counter2:
    :return:
    """
    if word in counter2:
        pwt = joined_count[word] / len(joined_count)
        pw = counter2[word] / len(counter2)
        return pwt / pw
    else:
        pwt = joined_count[word] / len(joined_count)
        return pwt


def filter_words(word_list):
    """
    Filter out certain words
    :param word_list: list
    :return: list
    """
    final_words = []
    for word in word_list:
        if word in FUNCTION_WORDS:
            continue
        elif len(word) < 3:
            continue
        elif word not in common_words:
            continue
        else:
            final_words.append(word)
    return final_words


def main_program(translation_file, cs_post_file):
    p_wt = {}
    translation_posts = pd.read_csv(translation_file, encoding='utf-8')
    cs_posts = pd.read_csv(cs_post_file, encoding="utf-8")
    translation_lst = translation_posts["Text"].values
    cs_lst = cs_posts["Text"].values
    cs_count = count_words(cs_lst)
    translation_count = count_words(translation_lst)
    for word in translation_count:
        p_wt[word] = compute_probability(word, translation_count, cs_count)
    sorted_probs = sorted(p_T.items(), reverse=True, key=operator.itemgetter(1))
    final_translation_words = sorted_probs[:50]
    with open('translation_prob.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in final_translation_words:
            writer.writerow([key, value])
        writer.close()


if __name__ == "__main__":
    translation_loc = sys.argv[1]
    cs_post_loc = sys.argv[2]
    main_program(translation_loc, cs_post_loc)
