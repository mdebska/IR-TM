from a1 import index

def permuterm_index(dict : dict) -> dict:
    """
    Creates a permuterm index from the given dictionary and postings.   
    The dictionary should be in the format {term: (count, pointer)}.
    """
    permuterm_dict = {}
    for term in dict:
        # create the permuterm for the term
        term_length = len(term)
        permuterm = term + "$"  # add a special end character
        _, pointer = dictionary[term]
        posting_list = postings[pointer]
        for _ in range(term_length + 1):  # +1 to include the original term
            permuterm_dict[permuterm] = posting_list
            permuterm = permuterm[1:] + permuterm[0]
    return permuterm_dict

def query_permuterm(term: str, permuterm_dict: dict) -> list:
    """
    Returns the posting list(s) for a term or wildcard query using the permuterm index.
    Supports queries with a single '*' wildcard.
    """
    # No wildcard
    if '*' not in term:
        term_length = len(term)
        term = term + "$"
        for _ in range(term_length):
            # print(f"Checking term: {term}")
            if term in permuterm_dict:
                # print(f"Found postings for term: {permuterm_dict[term]}")
                return list(permuterm_dict[term])
            term = term[1:] + term[0]
        return []

    # Wildcard handling
    split = term.split('*')
    prefix, suffix = split[0], split[1]
    rotated = suffix + "$" + prefix  # rotate so * is at the end
    # print(f"Rotated term for wildcard query: {rotated}")

    results = set()
    for key in permuterm_dict:
        if key.startswith(rotated):
            results.update(permuterm_dict[key])
            # print(f"Found postings for key: {key} -> {permuterm_dict[key]}")
    return list(results)

def intersect_queries(query1: str, query2: str, permuterm_dict: dict) -> list:
    """
    Returns the intersection of two queries using the permuterm index.
    """
    res = []
    postings1 = query_permuterm(query1, permuterm_dict)
    postings2 = query_permuterm(query2, permuterm_dict)

    # initialize iterators
    iter1 = iter(postings1)
    iter2 = iter(postings2)
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

if __name__ == "__main__":
    dictionary, postings = index(r"data_1_2\tweets.csv")
    
    # Create the permuterm index
    permuterm_dict = permuterm_index(dictionary)

    # Example queries
    # print(intersect_queries("side", "effect", permuterm_dict)) 
    # print(intersect_queries("malar*", "vaccine", permuterm_dict))  
    # print(intersect_queries("*aria", "vaccin*", permuterm_dict)) 
    # print(intersect_queries("*ree", "on*ne", permuterm_dict))