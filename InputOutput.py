import pickle
import os

# === READING AND MERGING ===
# merge_block -> Entry point for all merging operations
# nway_merge -> Merges multiple posting lists into one
# read_posting_list -> Reads a posting list out of a posting list block
# get_dictionary -> Reads the dictionary file and returns an dictionary


def merge_blocks(out_dict, out_postings, block_num):
    """
    First, we unpickle all dictionaries to serve as references for our serialized posting lists.
    Next, we start n-way merging all postings into one (new) dictionary.
    """
    print("Starting merge_block")
    dict_f_list = [str(num) + out_dict for num in range(1, block_num + 1)]
    post_f_list = [str(num) + out_postings for num in range(1, block_num + 1)]

    # union all dictionaries into our new dictionary first
    # at this stage, dictionary: term -> [(block num, position), ...]
    dictionary = dict()
    for i, dict_f in enumerate(dict_f_list):
        print(f"Merging {dict_f} into new dictionary")
        new_dict = pickle.load(open(dict_f, "rb"))
        new_keys = set(new_dict.keys())
        curr_keys = set(dictionary.keys())

        # find existing keys and keys to be added
        existing, to_add = new_keys & curr_keys, new_keys - curr_keys

        # for each existing key, append it to entry
        block_index = i
        for existing_key in existing:
            dictionary[existing_key].append((block_index, new_dict[existing_key]))

        # for each new (to add) key, make new entry
        for to_add_key in to_add:
            dictionary[to_add_key] = [(block_index, new_dict[to_add_key])]

    # in this stage, we convert the dictionary into...
    # dictionary: term -> merged posting list
    print(f"Merging all posting lists")
    post_fp_list = [open(post_f, "r") for post_f in post_f_list]
    for term in dictionary.keys():
        entries = dictionary[term]
        posting_list = nway_merge(post_fp_list, entries)
        dictionary[term] = posting_list
    print(f"Total number of terms is {len(dictionary)}")
    # this function should only be called ONCE... for the merging of all blocks
    # therefore, we can delete all block files
    for doc_name in dict_f_list + post_f_list:
        print(f"Removing {doc_name}")
        os.remove(doc_name)

    return dictionary


def nway_merge(posting_block, entries):
    """
    Takes in file pointers to all posting list blocks along with
    entries (block_num, position) from the merged dictionary.
    Does n-way merge on all posting lists.
    Returns a single posting list.
    """
    if len(entries) == 1:
        block_index, pos = entries[0]
        posting_list = read_posting_list(posting_block[block_index], pos)
        return [len(posting_list), posting_list]

    all_lists = []
    for block_index, pos in entries:
        curr_posting_file = posting_block[block_index]
        new_posting_list = read_posting_list(curr_posting_file, pos)
        all_lists.append(new_posting_list)

    # TODO: Actually do a n-way merge
    posting_list = list(set([item for sublist in all_lists for item in sublist]))
    return [len(posting_list), posting_list]


def read_posting_list(posting_fp, location):
    """
    Returns a posting list from a posting list file pointer,
    given its location (in characters from start) in the file.
    """
    posting_fp.seek(location, 0)
    posting_str = char = ""

    # move past the document frequency stored and reset char
    while char != "$":
        char = posting_fp.read(1)
    char = ""

    # read the entire posting list and stop at terminating char
    while char != "|":
        posting_str += char
        char = posting_fp.read(1)

    # convert to list of ints and return
    # TODO: Adapt this for skip pointers
    posting_list = list(map(int, posting_str.split(",")))
    return posting_list


def read_doc_freq(posting_fp, location):
    """
    Reads only the document frequency from the posting list file.
    For query optimization purposes.
    """
    posting_fp.seek(location, 0)
    doc_freq_str = char = ""
    while char != "$":
        doc_freq_str += char
        char = posting_fp.read(1)
    doc_freq = int(doc_freq_str)
    return doc_freq


def get_dictionary(out_dict):
    """
    FOR SEARCHING ONLY!
    We assume that the full index does not fit in memory, so we only load the dictionary.
    The dictionary lets us read posting lists by their positions in the posting lists file.
    """
    return pickle.load(open(out_dict, "rb"))


# === WRITING ===
# write_block -> Writes in-memory dictionary into a block (dictionary + posting files)
# serialize_posting -> Turns a posting list into a formatted string


def write_block(dictionary, out_dict, out_postings, block_num=""):
    """
    For each (term, posting list) pair in the dictionary...

    We serialize each posting list using serialize_posting into a string.
    The serialized posting list is written into the postings file.
    We count the number of characters written so far as cumulative_ptr.

    As each term is written, we write the (term, cumulative_ptr) pair into index.
    The cumulative_ptr can be used to directly grab a posting list from the postings file.
    The index is written into the dictionary file using pickle.
    """
    index = dict()
    cumulative_ptr = 0

    with open(str(block_num) + out_postings, "w") as postings_fp:
        for term, posting_list in dictionary.items():
            posting_list = posting_list[1]  # discard frequency for now
            posting_list_serialized = serialize_posting(posting_list)
            index[term] = cumulative_ptr
            cumulative_ptr += len(posting_list_serialized)
            postings_fp.write(posting_list_serialized)

    pickle.dump(index, open(str(block_num) + out_dict, "wb"))
    if block_num:
        print(f"Wrote {len(dictionary)} terms into block number {block_num}")
    else:
        print(f"Wrote {len(dictionary)} terms into final files")


def serialize_posting(posting_list):
    """
    Turns a posting list into a string, and returns the string.
    The string format is: "(freq)$(id1),(id2^skip),(...),(idn)|".
    The "|" is the terminator character for the serialization.
    """
    posting_list = sorted(list(posting_list))
    doc_freq = str(len(posting_list))
    doc_ids = ",".join(map(str, posting_list))  # TODO: Add skip pointers here
    output = f"{doc_freq}${doc_ids}|"
    return output
