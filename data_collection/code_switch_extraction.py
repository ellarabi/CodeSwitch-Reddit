import json
import re
import pandas as pd
import numpy as np
from post import Post
from datetime import datetime
from polyglot.detect import Detector
from polyglot.text import Text
import spacy
import xx_ent_wiki_sm
import multiprocessing as mp

spacy.require_gpu()
nlp = xx_ent_wiki_sm.load()
false_langs = ["kn", "un", "or", "chr", "xx"]
translation_words = np.loadtxt("translationprobs.txt", usecols=0, dtype="str")


def code_switch_polyglot(country, translation=True):
    """
    Function to find code switch posts given a country
    :param translation: bool
        if we should remove translation posts
    :param country: str country to find code switching posts in
    :return: array
        array of Post objects
    """
    global valid_countries
    comments = []
    final_file = f"<outpuht file path>/{country}.comment.json.out"

    with open(final_file, "r") as posts:

        for line in posts:

            data = json.loads(line)

            if "subreddit" in data.keys():
                sub_reddit = data["subreddit"]

            else:
                continue

            author = data["author"]
            if ("bot" in author.lower()) or ("AutoModerator" in author):
                continue
            date = data["created_utc"]
            post_id = data["id"]
            link_id = data["link_id"]
            parent_id = data["parent_id"]

            if "body" in data.keys():
                langs = find_langs(data["body"], translation)

            elif "selftext" in data.keys():
                langs = find_langs(data["selftext"], translation)
            else:
                langs = None
            if langs is None:
                continue
            else:
                lang1 = langs[0]
                lang2 = langs[1]
                confidence = langs[2]
                code_switch = Post(author, sub_reddit, date, country, confidence, raw_text,
                                   lang1,
                                   lang2, post_id, link_id, parent_id)
            comments.append(code_switch)
        posts.close()

    print(country, "done")
    return comments


def find_langs(raw_text, translation=True):
    """

    :param translation: bool
        if we should remove translation posts
    :param raw_text: the raw text from the subreddit
    :return: tuple
        if post is not codeswitch post then return None,
        else return lang1, lang2 and confidence of lang1 in post
    """
    global false_langs
    if "http" in raw_text:
        return None
        # skip posts that have links (these posts are too noisy and hard to built regex to remove the links)
    clean_string = clean_text(raw_text)
    if translation:
        if is_translation(clean_string):
            return None

    detector = Detector(clean_string, quiet=True)
    if ("en" != detector.languages[0].code) and ("en" != detector.languages[1].code):
        # skip posts that don't contain any english
        return None

    if (detector.languages[1].code not in false_langs) and (detector.languages[0].code not in false_langs):
        if detector.reliable:
            lang1 = detector.languages[0].name
            lang2 = detector.languages[1].name
            confidence = detector.languages[1].confidence

            return lang1, lang2, confidence
        else:
            return None
    else:
        return None


def clean_text(text):
    """

    :param text: str the raw text to be cleaned
    :return: str
        return cleaned string
    """
    new_string = re.sub('&gt;.*', ' ', text)  # remove replies to
    new_string = re.sub('&.*;', ' ', new_string)  # remove replied to
    new_string = re.sub("r\/.*\s", ' ', new_string)  # remove any subreddit links
    new_string = re.sub("u\/.*\s", " ", new_string)  # remove user names
    new_string = ''.join(z for z in new_string if z.isprintable())

    string_list = re.findall('\".*\"', new_string)

    # remove quotes that are longer than 5 words in length
    for string in string_list:
        token_count = len(string.split())
        if token_count > 5:
            new_string = new_string.replace(string, " ")

    # remove named entities
    doc = nlp(new_string)
    for ent in doc.ents:
        new_string = new_string.replace(ent.text, " ")

    return new_string


def is_translation(text):
    """
    Check if post is a translation post
    :param text: str
        the post to check if there is translation

    :return: bool
    """
    post = Text(text)
    all_words = [word.lower() for word in post.words if word.isalpha()]
    for word in all_words:
        if word in translation_words:
            return True
    else:
        return False


if __name__ == "__main__":
    out_file = "<output file location>"
    eng_countries = ["Canada", "US", "Australia", "UK", "NewZealand"]
    pool = mp.Pool(8)  # specify how many cores to use
    countries = np.loadtxt("countries.txt", usecols=0, dtype="str")
    valid_countries = [x for x in countries if x not in eng_countries]
    results = pool.map(code_switch_polyglot, valid_countries)
    comments_array = [item for sublist in results for item in sublist]

    header = Post.header()
    comments_df = pd.DataFrame([x.to_tuple() for x in comments_array], columns=header)
    pd.DataFrame.to_csv(comments_df, out_file, index=False, encoding='utf-8')
