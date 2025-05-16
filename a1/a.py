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
    EMOJI_PATTERN = re.compile(
        r"(["
        r"\U0001F1E0-\U0001F1FF"
        r"\U0001F300-\U0001F5FF"
        r"\U0001F600-\U0001F64F"
        r"\U0001F680-\U0001F6FF"
        r"\U0001F700-\U0001F77F"
        r"\U0001F780-\U0001F7FF"
        r"\U0001F800-\U0001F8FF"
        r"\U0001F900-\U0001F9FF"
        r"\U0001FA00-\U0001FA6F"
        r"\U0001FA70-\U0001FAFF"
        r"\u2702-\u27B0"
        r"])"
    )

    string_processed = re.sub(r"[\[\]\.\(\),\?!\"'@:#]", "", string).lower()
    string_processed = re.sub(EMOJI_PATTERN, "", string_processed)
    string_processed = re.sub(r"newline", " ", string_processed)
    string_processed = re.sub(r"tab", " ", string_processed)

    terms = re.split(r"\s+", string_processed.strip())
    terms = list(set(terms))

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

        # create the posting list and the dictionary
        for term in terms:
            if term in dictionary:
                count, pointer = dictionary[term]
                count += 1
                postings[pointer].add(row["id"])
                dictionary[term] = (count, pointer)

            else:
                pointer = "p"+ str(len(postings) + 1)
                dictionary[term] = (1, pointer)
                postings[pointer] = {row["id"]}

    # sort the posting lists
    for pointer in postings:
        postings[pointer] = sorted(postings[pointer])

    return dictionary, postings

# example usage
dictionary, postings = index(r"a1\data\tweets.csv")

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
    res = []
    if term1 in dictionary and term2 in dictionary:
        # get the posting lists of the terms
        _, pointer1 = dictionary[term1]
        _, pointer2 = dictionary[term2]
        t_posting1 = postings[pointer1]
        t_posting2 = postings[pointer2]

        # initialize iterators
        iter1 = iter(t_posting1)
        iter2 = iter(t_posting2)
        try:
            doc1 = next(iter1)
            doc2 = next(iter2)
            # iterate through the posting lists 
            # until the end of one of them is reached
            while True:
                if doc1 == doc2:
                    res.append(doc1)
                    doc1 = next(iter1)
                    doc2 = next(iter2)
                elif doc1 < doc2:
                    doc1 = next(iter1)
                else:
                    doc2 = next(iter2)
        except StopIteration:
            pass
    return res
            
# test case
res1 = query_two("side", "effect")
res2 = query_two("malaria", "vaccine")
result = list(set(res1) & set(res2))
print("Result: ", result)