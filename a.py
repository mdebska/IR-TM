import pandas as pd
import re

def load_csv(path):
    return pd.read_csv(path, 
                        sep="\t", 
                        header=None,
                        encoding="utf-8",
                        names=["ts", "id", "uname", "name", "comment"],
                        on_bad_lines="skip", # skips wrong formatted lines
                        )

def doc_to_terms(string):
    EMOJI_PATTERN = re.compile( # (source: stackoverflow)
    "(["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "])"
  )

    # lowercase & no punctuation 
    string_processed = re.sub("[\[\]\.\(\),\?!\"\']", "",string).lower()

    # no emojis
    string_processed = re.sub(EMOJI_PATTERN, "", string_processed)

    # removes "newline" & "tab"
    string_processed = re.sub("newline", " ", string_processed)
    string_processed = re.sub("tab", " ", string_processed)

    # splites where a space is
    terms = re.split(" ", string_processed)

    # removes duplicates
    terms = list(set(terms))

    # ignores tweets with links 
    for term in terms:
        if re.findall("\Ahttp", term):
          return []

    return terms

def index(filename):
    tweets = load_csv(filename)

    dictionary = {}
    postings = {}

    for index, row in tweets.iterrows():
        terms = doc_to_terms(row["comment"])

        for term in terms:
            if term in dictionary:
                count, pointer = dictionary[term]
                count += 1
                postings[pointer].append(row["id"])

            else:
                count, pointer = 1, "p"+ str(len(postings) + 1)
                dictionary[term] = (count, pointer)
                postings[pointer] = [row["id"]]

    index = (dictionary, postings)
    return index

dictionary, postings = index("data/tweets.csv")