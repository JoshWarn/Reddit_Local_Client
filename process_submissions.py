from readability import Readability
import definitions as d


def process_submission_json_data(title='submission2'):
    # intakes raw json files; removes data not cared about.
    # Scrape folder for unprocessed json files
    submission_json_files = d.find_json_files_of_type_in_folder('', title, '_', '.json')
    # for each file
    print(submission_json_files)
    reddit_post_id_list, subreddit_list, post_chapter_title_list, author_list, time_post_created_list = [], [], [], [], []
    time_post_modified_list, time_post_grabbed_list, post_flair_list, word_count_list, likes_list = [], [], [], [], []
    upvote_ratio_list, NSFW_list, image_preview_link_list, comment_number_list, readibility_metrics_list = [], [], [], [], []
    post_series_list, post_series_previous_list, post_series_next_list = [], [], []
    links_within_post_list, link_text_within_post_list = [], []

    for i in range(len(submission_json_files)):                         # for each json entry:...
        json_file_data = d.read_json_file(submission_json_files[i])       # open the json file...
        print(i)
        for j in range(len(json_file_data)):      # get however many entries are in each json files:
            text_data = json_file_data[j]["selftext"]
            # [0: local post path,
            # TODO: to do this, it first must be determined if it's part of a series or not... smhmh

            # 1: post_reddit_id/url,                      "url"
            reddit_post_id = json_file_data[j]["url"]
            # 2: subreddit,                               "subreddit"
            subreddit = json_file_data[j]["subreddit"]
            # 3: post_chapter_title,                      "title"
            post_chapter_title = json_file_data[j]["title"]
            # 4: post_author,                             "author"
            author = json_file_data[j]["author"]
            # 5: time post created                        "created_utc"
            time_post_created = json_file_data[j]["created_utc"]
            # 6: time post modified                       "updated_utc"
            time_post_modified = json_file_data[j]["updated_utc"]
            # 7: time post grabbed                        "retrieved_utc"
            time_post_grabbed = json_file_data[j]["retrieved_utc"]
            # 8: [post category/flair (e.g., "meta")]     "link_flair_text"
            post_flair = json_file_data[j]["link_flair_text"]
            # 9: Word count,
            # TODO Big issue here is including story-comments made by author as an extension of the story
            word_count = len(json_file_data[j]["selftext"].split(" "))  # dumb calculation of words in post by splitting by space.
            # 10: likes                                    "score"
            likes = json_file_data[j]["score"]
            # 11: upvote ratio                            "upvote_ratio"
            try:
                upvote_ratio = json_file_data[j]["upvote_ratio"]    # TODO: "upvote ratio" is a newer stat; some posts may not have it.
            except:
                upvote_ratio = 0
            # 12: NSFW status                             "over_18"
            NSFW = json_file_data[j]["over_18"]
            # 13: Preview image                       "preview" -> "images" -> "source" -> "url"; must remove the amp; escapes
            # TODO properly use this.
            try:
                img_preview = json_file_data[j]["preview"]["images"][0]["source"]["url"]
                img_preview = img_preview.replace("amp;", "")    # removes the escape sequence from the link
            except Exception:   # TODO make this nicer later
                img_preview = ""

            # 14: Number of comments,                      "num_comments"
            comment_num = json_file_data[j]["num_comments"]

            # 15: [Reading comprehension level (multiple choices)?] TODO not thoroughly thought through.
            # TODO Big issue here is including story-comments made by author as an extension of the story
            # TODO another issue - text should be cleaned before it's added here! remove links, formatting, new lines etc.


            '''
            if word_count > 100:
                a=1
            Temporarly removing word-count-metric just 'cause it's slow.
                r_metric = Readability(text=json_file_data[j]["selftext"]) # <-- replace raw text here!
                flesch_kincaid_grade = r_metric.flesch_kincaid().score
                flesch_reading_ease = r_metric.flesch().score
                dale_chall = r_metric.dale_chall().score
                readability_metrics = [flesch_kincaid_grade, flesch_reading_ease, dale_chall]
            
            
            else:'''
            readability_metrics = [0, 0, 0]

            # 16: post_series (if part of one),
            series = ""     # somehow find if it matches with any existing series

            # 17: [post_series_previous],
            series_previous = ""    # somehow if any post is previous to it in the series
            # 18: [post_series_next],
            series_next = ""  # somehow if any post is next to it in the series
            # 19: [links_within_post],
            # 20: [link_texts_within_post]]
            links_in_post, link_texts_in_post = d.find_links_in_text(text_data)

            #print(f"Post number {i}, {j}")
            #print(reddit_post_id, subreddit, post_chapter_title, post_flair)
            # print(author, likes, upvote_ratio, NSFW, word_count)
            #print(links_in_post)
            #print(link_texts_in_post)
            #print(time_post_created, time_post_modified, time_post_grabbed)
            #print(readability_metrics)
            #print(img_preview)

            reddit_post_id_list.append(reddit_post_id)
            subreddit_list.append(subreddit)
            post_chapter_title_list.append(post_chapter_title)
            author_list.append(author)
            time_post_created_list.append(time_post_created)
            time_post_modified_list.append(time_post_modified)
            time_post_grabbed_list.append(time_post_grabbed)
            post_flair_list.append(post_flair)
            word_count_list.append(word_count)
            likes_list.append(likes)
            upvote_ratio_list.append(upvote_ratio)
            NSFW_list.append(NSFW)
            image_preview_link_list.append(img_preview)
            comment_number_list.append(comment_num)
            readibility_metrics_list.append(readability_metrics)
            post_series_list.append(series)
            post_series_previous_list.append(series_previous)
            post_series_next_list.append(series_next)
            links_within_post_list.append(links_in_post)
            link_text_within_post_list.append(link_texts_in_post)


    return reddit_post_id_list, subreddit_list, post_chapter_title_list, author_list, time_post_created_list,\
           time_post_modified_list, time_post_grabbed_list, post_flair_list, word_count_list, likes_list,\
           upvote_ratio_list, NSFW_list, image_preview_link_list, comment_number_list, readibility_metrics_list,\
           post_series_list, post_series_previous_list, post_series_next_list, links_within_post_list,\
           link_text_within_post_list

    # Data format:
    '''
    series folder
        post1 json...
            subreddit, url, title, author, likes, upvote_ratio, num_comments, post category, NSFW_status, t_created, t_updated, t_accessed, content,
            series_name, series_previous, series_next, word_count, reading_difficulty
            internal links referenced, preview image location.
            # TODO will have to be able to update links references and preview img location if found to be shared (moved to series_summary_resources)
        post1 folder
            preview image used only by post, internal links referenced only by post, image-downloads
        post2 json...
        post2 folder...
        series_summary_resources
            preview images shared, internal links referenced that are shared...
    '''


    # Get list of all submission jsons in folder
    # For each folder... go through etc.

    # find the series that the post is part of; if none is found, put into a "1-off" folder.
    # Scan the one-off folder to check if any posts match with a series. (e.g. match author, name, look for "previous"/"next"/"first" link posts


def find_series(title, post_links, post_link_text, existing_series, existing_series_titles, existing_series_authors, existing_series_post_links, existing_series_post_link_text):
    # if detected as part of a series, return the series name.

    # calculate similarity with another series, look for "first" / "next" / "previous" links.
    # check for if there are any posts by the same author with similar names

    # else, return none
    return None
