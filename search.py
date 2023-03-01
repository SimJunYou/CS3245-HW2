#!/usr/bin/python3
import re
import nltk
import sys
import getopt
from Parser import read_and_parse_queries
from InputOutput import get_dict_and_doc_list
from Searcher import process_query


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
    )


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print("running search on the queries...")

    dictionary, all_doc_ids = get_dict_and_doc_list(dict_file)
    queries = read_and_parse_queries(queries_file, postings_file, dictionary)
    with open(results_file, "w") as of:
        for query in queries:
            # process query, remove skip pointers, convert to string
            result = process_query(query, dictionary, all_doc_ids, postings_file)
            result = list(map(lambda x: x[0] if isinstance(x, tuple) else x, result))
            result = ",".join(map(str, result))
            print(result, file=of)


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:p:q:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-d":
        dictionary_file = a
    elif o == "-p":
        postings_file = a
    elif o == "-q":
        file_of_queries = a
    elif o == "-o":
        file_of_output = a
    else:
        assert False, "unhandled option"

if (
    dictionary_file == None
    or postings_file == None
    or file_of_queries == None
    or file_of_output == None
):
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
