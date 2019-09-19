import sys
import requests
import datetime
import json
import pandas as pd
import spacy
import multiprocessing as mp
from pathlib import Path


def has_text(element):
    """
    return true if the element is not empty
    :param element:
    :return:
    """
    body = element.get('body', '')
    selftext = element.get('selftext', '')
    return len(body) > 0 and body != '[removed]' or len(selftext) > 0 and selftext != '[removed]'


# end def


def crawl_subreddit_data(subreddit_name, retrieval_type='comment'):
    """
    crawl all posts (submissions or comments) for a given subreddit
    :param subreddit_name:
    :param retrieval_type:
    :return:
    """

    today = datetime.datetime.utcnow()
    today_timestamp = int((today - datetime.datetime(1970, 1, 1)).total_seconds())
    before_date = today_timestamp
    previous_time = before_date
    out_folder = Path(f"/ais/hal9000/masih/codeswitch/allposts/")
    out_file = out_folder / f"{subreddit_name}.{retrieval_type}.json.out"
    with open(out_file, 'w') as fout:
        count = 0
        done = False
        while not done:
            print(before_date)
            count += 1
            query = PUSHSHIFT_ENDPOINT + retrieval_type + '/?subreddit=' + subreddit_name + \
                    '&sort=desc&size=' + str(MAX_RETRIEVED_ELEMENTS) + '&before=' + str(before_date)
            print(query, 'request #', count)

            r = requests.get(query)
            if r.status_code is not 200:
                print('bad response code:', r.status_code)
                break

            # end if

            # record the response
            for element in r.json()['data']:
                if has_text(element):
                    json.dump(element, fout)
                    fout.write('\n')
                    fout.flush()
                # end if

                before_date = element['created_utc']
            # end for

            # if len(r.json()['data']) < MAX_RETRIEVED_ELEMENTS:
            if before_date == previous_time:
                done = True
                print("done")
            else:
                previous_time = before_date
        # end if
    # end while


# end with
# end def


MAX_RETRIEVED_ELEMENTS = 1000
PUSHSHIFT_ENDPOINT = 'https://api.pushshift.io/reddit/search/'


def main():
    subreddits = sys.argv[1] # file location containing list of subreddits to retrieve from
    retrieval_type = sys.argv[2]
    assert (retrieval_type in ['submission', 'comment'])
    sub_lst = []
    with open(subreddits, 'r') as fin:
        for line in fin:
            subreddit_name = line.strip()
            sub_lst.append(subreddit_name)
    for x in sub_lst:
        crawl_subreddit_data(x)


if __name__ == '__main__':
    main()
    # end for
# end with

# end if
