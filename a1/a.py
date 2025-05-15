import pandas as pd
import re

def load_csv(path):
    """
    Loads a csv file and returns a pandas dataframe.
    """
    return pd.read_csv(path, 
                        sep="\t", 
                        header=None,
                        encoding="utf-8",
                        names=["ts", "id", "uname", "name", "comment"],
                        on_bad_lines="skip", # skips wrong formatted lines
                        )

def doc_to_terms(string):
    """
    Normalization of the terms in a tweet.
    """
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
    """
    Creates a non-positional inverted index from a csv file.
    """
    # load the csv file
    tweets = load_csv(filename)

    dictionary = {}
    postings = {}

    
    for index, row in tweets.iterrows():
        # normalize terms
        terms = doc_to_terms(row["comment"])

        #  create the posting list and the dictionary
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

# example usage
dictionary, postings = index("data/tweets.csv")

def query(term : str):
    """
    Returns the posting list of a term.
    """
    if term in dictionary: 
        _, pointer = dictionary[term]
        t_posting = postings[pointer]
    else:
        t_posting = {}

    return t_posting

def query_two(term1, term2 : str):
    """
    Returns the intersection of two posting lists.
    """
    if term1 in dictionary and term2 in dictionary:
        # get the posting lists of the terms
        _, pointer1 = dictionary[term1]
        _, pointer2 = dictionary[term2]
        t_posting1 = postings[pointer1]
        t_posting2 = postings[pointer2]

        # initialize iterators
        iter1 = iter(t_posting1)
        iter2 = iter(t_posting2)

        res = []
        try:
            doc1 = next(iter1)
            doc2 = next(iter2)
            # iterate through the posting lists 
            # until the end of one of them is reached
            while True:
                if doc1 == doc2:
                    res.append(doc1)
                    doc1 = next(res)
                    doc2 = next(res)
                elif doc1 < doc2:
                    doc1 = next(iter1)
                else:
                    doc2 = next(iter2)
        except StopIteration:
            pass
    return res


