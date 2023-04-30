import definitions as d
import pickle as pkl


def create_corpus(skip_compilation=False):

    # go through every json file's text; find frequency of words...
    submission_json_files = d.find_json_files_of_type_in_folder('', 'submission2', '_', '.json')

    if skip_compilation is False:
        # for each file
        print(submission_json_files)
        for i in range(len(submission_json_files)):  # for each json entry:...

            # makes a new dictionary for each file; I'm worried about the dictionary getting too large to do in a single go.
            words = []
            word_frequency = []
            json_file_data = d.read_json_file(submission_json_files[i])  # open the json file...
            for j in range(len(json_file_data)):  # get however many entries are in each json files:
                    print(f"{i}, {j}")
                    text_data = json_file_data[j]["selftext"]

                    # clean json text:
                    word_list = clean_text_for_comprehension(text_data)
                    for k in range(len(word_list)):
                        if word_list[k] not in words:
                            words.append(word_list[k])
                            word_frequency.append(1)
                        else:
                            index_loc = words.index(word_list[k])
                            word_frequency[index_loc] += 1
            # sort the list by frequency...
            word_dict = dict(zip(words, word_frequency))
            word_dict_sorted = dict(sorted(word_dict.items(), key=lambda x: x[1], reverse=True))

            #for key, value in word_dict_sorted.items():
            #    print(key, value)

            # Save the word-frequency dictionary to a pickle file
            with open(f"wordfrequencycorpus_{i}.pkl", 'ab+') as f:
                pkl.dump(word_dict_sorted, f)
            with open(f"wordfrequencycorpus_{i}.txt", 'a+', encoding="utf-8") as f:
                for key, value in word_dict_sorted.items():
                    f.write(f"{key}, {value}\n")

    combined_word_list, combined_frequency_list = [], []
    # after all dictionaries have been made... figure out how to combine into a single dictionary.
    for i in range(len(submission_json_files)):
        print(f"Working on corpus {i}")
        with open(f"wordfrequencycorpus_{i}.pkl", 'rb+', ) as f:
            single_dict = pkl.load(f)
        keys = list(single_dict.keys())
        values = list(single_dict.values())

        print(len(keys), len(values), len(combined_word_list), len(combined_frequency_list))
        for j in range(len(keys)):
            if keys[j] not in combined_word_list:
                combined_word_list.append(keys[j])
                combined_frequency_list.append(values[j])
            else:
                index_loc = combined_word_list.index(keys[j])
                combined_frequency_list[index_loc] += values[j]

    combined_word_dict = dict(zip(combined_word_list, combined_frequency_list))
    combined_word_dict_sorted = dict(sorted(combined_word_dict.items(), key=lambda x: x[1], reverse=True))
    for key, value in combined_word_dict_sorted.items():
        print(key, value)
    print(len(combined_word_dict_sorted))

    with open(f"wordfrequencycorpus.pkl", 'ab+') as f:
        pkl.dump(combined_word_dict_sorted, f)
    with open(f"wordfrequencycorpus.txt", 'a+', encoding="utf-8") as f:
        for key, value in combined_word_dict_sorted.items():
            f.write(f"{key}, {value}\n")


def custom_reading_comprehension(corpus, sample):
    a = 1
    # TODO later; replace the other readability metrics
    # find the frequency of words used;
    # compare to their frequency in modern language-use in a dataset.
    # increase the "difficulty" if the word is infrequently used in the text too - as that'd reduce the context that one can use to define the word.
    # also account for sentence lengths?


def clean_text_for_comprehension(text):
    text = text.replace("[", ' ')
    text = text.replace("]", ' ')   # splits linked text from links

    text_list = text.split(" ")

    terms = ['http', 'https', 'r/hfy', 'r/HFY', '/u/']
    for i in range(len(text_list)):
        for j in range(len(terms)):
            if terms[j] in text_list[i]:
                removed_string = text_list[i]
                # print('removed', terms[j], removed_string)
                text = text.replace(removed_string, '')




    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')  # double check this
    text = text.replace('\"', ' ')
    text = text.replace("\'", ' ')   # note: this causes issues with contractions e.g. can't;[name]'s; you'd; you'll; you're
    text = text.replace("\\", ' ')
    text = text.replace("&amp;#x200B;", ' ')
    text = text.replace("&amp;", ' ')
    text = text.replace("---", ' ')
    text = text.replace("&gt;", ' ')
    text = text.replace("&gt;", ' ')
    replace_char_list = list("~?!.,*=|-—+{}:;/“”’‘_…()^©‾◡◝%")
    for i in range(len(replace_char_list)):
        text = text.replace(replace_char_list[i], ' ')

    # makes all text lowercase
    text = text.lower()

    # removes things that are only numbers *OR* if it has non-alnum characters *OR* if longer than 25 characters:
    text = text.split(" ")
    for i in range(len(text)-1, -1, -1):
        if text[i].isalpha() is False:
            text.pop(i)
        #elif len(text[i]) >= 25:
        #    print(f"String too long! {text[i]}")
        #    text.pop(i)

    return text


# create_corpus(skip_compilation=True)


# First full corpus has 271k after corpus 15; but doesn't remove non-alphanum strings; est new 250k after corpus 15.
