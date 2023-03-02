This is the README file for A0200198L-A0199724M's submission
Email(s): e0407179@u.nus.edu e0406705@u.nus.edu

== Python Version ==

We're using Python Version 3.8.10 for this assignment.

== General Notes about this assignment ==

Implementation uses SPIMI with a fixed threshold for the number of pairs.
With the reuters corpora, we should see 5 blocks in total get formed and ultimately removed
after the merge is complete.

Tokenization is simple, using NLTK's word_tokenize, case folding, and Porter stemming.
Punctuation is left in place.

The dictionary contains a mapping of terms to their position in the posting lists file
in number of characters, which serves as a pointer for retrieval.

The final dictionary file contains:
- Dictionary object, as mentioned above
- Set of all document IDs (for NOT operations)

The final posting list will have skip pointers written in it. Each posting list has this format:
(num items)$(item1)^(skip len),(item2),...,(itemX)^(skip len),...,(itemZ)|

Special characters:
- '$' separates the number of items from the actual list
- '^' denotes that the following number represents a skip pointer
- '|' terminates the posting list serialization

The search methods only reads the necessary postings lists from the postings lists file.
AND and OR operators are implemented using the algorithms described in the lecture.

Parsing of queries is done using the shunting yard algorithm, and the query is transformed
into a single Operator object, with all sub-queries nested within itself.

e.g. a OR (b AND c AND d) -> OR(a, AND(b, c, d))

Resolving an operator will recursively resolve all operators stored as operands within itself.
We can take advantage of this to pass in the dictionary and set of all documents from the
outermost operator, letting it get passed down to all operators at resolve time.

Malformed queries will result in an error being printed at the corresponding line in the
output file.

== Files included with this submission ==

- README.txt
- CS3245-hw2-check.sh
- index.py  > Main loop for indexing, calls helper functions from InputOutput and Tokenizer
- search.py > Main loop for search, calls helper functions from InputOutput, Parser, and Searcher

- InputOutput.py > Helper functions for input/output operations
- Tokenizer.py   > Helper functions for tokenization operations
- Parser.py      > Helper functions for parsing queries
- Searcher.py    > Helper functions for searching, and class definitions for operators

- dictionary.txt > Final dictionary file from indexing Reuters corpora 
- postings.txt   > Final postings lists file from indexing Reuters corpora 

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0200198L-A0199724M, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

None
