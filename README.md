## CodeSwitch-Reddit

CodeSwitch-Reddit corpus collection, pre-processing and analysis is described in the paper:\
[CodeSwitch-Reddit: Exploration of Written Multilingual Discourse in Online Discussion Forums](https://www.aclweb.org/anthology/D19-1484/), Rabinovich et al., 2019. Supplemental materials are in [CodeSwitch-Reddit: Supplemental Materials](https://github.com/ellarabi/CodeSwitch-Reddit/blob/master/code_switching_supplemental.pdf).

The full dataset is available at http://www.cs.toronto.edu/~ella/code-switch.reddit.tar.gz. A cleaner monolingual part of the dataset was generated in Jan 2020, you may want to re-download if interested in that part of the corpus.

**cs_main_reddit_corpus.csv**: the main dataset comprising English-{Tagalog, Greek, Romanian, Indonesian, Russian} code-switched posts, detected with high accuracy (refer to the paper for details).

**cs_additional_reddit_corpus.csv**: additional dataset comprising English-{Spanish, Turkish, Arabic, Croatian, Albanian} code-switched posts. Despite its lower (true code-switching) accuracy, we recognize the potential usefulness of this additional data, and release it as an addendum to our main corpus, for possible further cleanup and preprocessing.

**eng_monolingual_reddit_corpus.csv**: monolingual English posts from the set of country-specific subreddits.


Please contact ellarabi@gmail.com for any questions.
