import time
import urllib.request
import os
import json
import pickle as pkl
import glob
# ONLY PUT FINISHED DEFINITIONS HERE


def grab_data_json(sub, req_type="submission", before_time=int(time.time()), after_time=0, f_name="output",
                   sleep_time=5, query_count=100, max_byte_size=50000000):
    assert req_type in ["submission", "comment"], f"Request type should be 'submission' or 'comment'. Found: {req_type}"
    start_time, count_sum, part = int(time.time()), 0, 1
    part_string = f"{str(part).zfill(4)}_{count_sum}"

    while True:
        url = f"https://api.pushshift.io/reddit/search/" \
              f"{req_type}/?subreddit={sub}&size={query_count}&before={before_time}&after={after_time}"

        # Grabbing site data; retries 10 times if fails.
        for i in range(10):
            try:
                r = json.load(urllib.request.urlopen(url))['data']
                break
            except Exception as exc:
                print(exc, f"Retry{i}")
                time.sleep(sleep_time)
                continue

        # If the query doesn't return anything, presume it is at the oldest date and exit.
        if len(r) == 0:
            print(f"\nF_Grab_Data: No queries return!\nReq: {req_type}, Sub: {sub}\nTime:{before_time} to {after_time}")
            break

        before_time = r[-1]["created_utc"]
        count_sum += len(r)
        # make new json file-name if file is over max-size (50mb)
        if os.path.exists(f"{f_name}_{start_time}_{part_string}.json"):
            if os.path.getsize(f"{f_name}_{start_time}_{part_string}.json") > max_byte_size:
                part += 1
                part_string = f"{str(part).zfill(4)}_{count_sum}"
                print(f"\nCreating New File: Part {part}.")

        # Save file
        if os.path.exists(f"{f_name}_{start_time}_{part_string}.json"):
            with open(f"{f_name}_{start_time}_{part_string}.json", "r+", encoding="utf-8") as f:
                data = json.load(f)
                for i in range(len(r)):
                    data.append(r[i])
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            with open(f"{f_name}_{start_time}_{part_string}.json", "a+", encoding="utf-8") as f:
                json.dump(r, f, ensure_ascii=False, indent=4)

        # Print the story-numbers to console
        if count_sum <= query_count or count_sum % (30*query_count) < (count_sum-len(r)) % (30*query_count):
            print(f"\nCount: {count_sum}.", end="")
        else:
            print(f"{count_sum}.", end="")

        time.sleep(sleep_time)


def read_json_file(path):
    with open(path, 'r', encoding="utf-8") as f:
        return json.load(f)


def write_post_meta_data_file(f_name, data_list):
    """
    :param f_name: local path of meta-data file.
    :param data_list: a 1x(16to30) list of meta-data about the post.
    :return: NONE
    """
    # Uses a pkl file to store post-metadata
    if len(data_list) < 16:
        print(f"Yo something fucked\n{data_list}")
        quit
    while len(data_list) < 30:
        data_list.append([])

    with open(f_name, 'ab+') as f:
        pkl.dump(data_list, f)


def read_meta_data_file(f_name):
    """
    Data in the following form (in a list):
        [0: local post path,
        1: post_reddit_id/url,                      "url"
        2: subreddit,                               "subreddit"
        3: post_chapter_title,                      "title"
        4: post_author,                             "author"
        5: time post created                        "created_utc"
        6: time post modified                       "updated_utc"
        7: time post grabbed                        "retrieved_utc"
        8: [post category/flair (e.g., "meta")]     "link_flair_text"
        9: Word count,
        10: likes                                    "score"
        11: upvote ratio                            "upvote_ratio"
        12: NSFW status                             "over_18"
        13: Preview image                       "preview" -> "images" -> "source" -> "url"; must remove the amp; escapes
        14: Number of comments,                      "num_comments"
        15: [Reading comprehension level (multiple choices)?] TODO not thoroughly thought through.
        16: post_series (if part of one),
        17: [post_series_previous],
        18: [post_series_next],
        19: [links_within_post],
        20: [link_texts_within_post]]
    :param f_name: local path of meta-data file.
    :return: returns a #-of-posts x 30 array of meta-data.
    """
    if os.path.exists(f_name):
        data = []
        with open(f_name, 'rb') as f:
            try:
                while True:
                    data.append(pkl.load(f))
            except EOFError:
                pass
        return data
    else:
        print(f"meta-data-file doesn't exist with path: {f_name}")
        quit


def find_json_files_of_type_in_folder(path='', prefix='submission', split_char='_', extension=".json"):
    """
    :param path:            Path of directory to scan for files in; defaults to local directory
    :param prefix:          Keyword to use for searching for json files e.g., "comment" or "submission".
    :param split_char:      What to split the json-filename-string by
    :param extension:       ... should always be ".json".
    :return: json_files     Returns json files that you want to grab data from - likely "comment" or "submission".
    """
    json_files = glob.glob(f"{path}*{extension}")
    for i in range(len(json_files)-1, -1, -1):    # must iterate through list backwards
        if prefix not in json_files[i].split(split_char):
            json_files.pop(i)
    return json_files


def find_links_in_text(text):
    link_text_list, link_list = [], []

    text_list = text.split(' ')
    for i in range(len(text_list)):

        if "http" in text_list[i]:

            link = str(text_list[i][text_list[i].rfind("http"):]).strip()  # has to use rfind instead of find to find the LAST instance of substring in string

            if link[-1] == ")":
                link = link[0:-1]

            if "\n" in link:
                link = link.split("\n")[0]
            # link = link.replace("\n", "")
            # print("text str temp:", text_list[i])

            # TODO This is testing; remove later.
            if link.split(".")[-1] == ("pn" or "jp" or ".jpe" or "gi"):
                print(i, link)
            # TODO End testing

            if ")" in link:
                link = link[0:link.rfind(")")]

            while link[-1] == ")" or link[-1] == "]" or link[-1] == "\\":
                link = link[0:-1]
            #print("AE", text_list[i].rfind("http"), text_list[i][text_list[i].rfind("http")-1])
            # print("link", link)

            # if link is raw without an embed:
            try:
                if text_list[i][text_list[i].rfind("http")-1] != "(" or text_list[i].rfind("http") == 0 \
                        or ")" not in text_list[i] or text_list[i][text_list[i].rfind("http")-2] != "]":
                    text_link = "NONE"

                else:   # link is embedded
                    # There could be a space in the [test text] string; append previous until "[" is found.
                    text_link = text_list[i][0:text_list[i].rfind("http") - 1]
                    relative_index = 1
                    #print("a0", text_list[i][0:text_list[i].rfind("http") - 2], text_list[i][0:text_list[i].rfind("http")])
                    #print("A", text_link)
                    while "[" not in text_link:
                        #print("b", text_link)
                        text_link = str(text_list[i - relative_index]) + " " + str(text_link)
                        relative_index += 1

                    # remove all characters that may be budding up to the left of the "[" eg. "garbage[..."
                    # the OR "[" in text_link[1:] makes sure there's only 1 "[" in the string.
                    while text_link[0] != "[" or "[" in text_link[1:]:
                        text_link = text_link[1:]
                    #print("c", text_link)
                    # gets rid of the brackets ex. [text] -> text...
                    # doesn't work with trailing if "]" is hyperlinked e.g. [[hey, here's some text]] -> hey, here's some text]
                    text_link = text_link[1:-1]

                    # to fix that...
                    # print("AEA", text_link)
                    #print("d", text_link)
                    while text_link[-1] == "]" or text_link[-1] == "\\":
                        text_link = text_link[0:-1]

                    # remove leading spaces
                    while "&lt;" in text_link:
                        text_link = text_link.replace("&lt;", "")

                    # remove leading spaces
                    while text_link[0] == " ":
                        text_link = text_link[1:]
            except:
                text_link = "BROKEN"

            link_list.append(link)
            link_text_list.append(text_link)
    return link_list, link_text_list
