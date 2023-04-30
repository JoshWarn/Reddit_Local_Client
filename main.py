import definitions as d
import grab_imgur_links_2 as gil2
import reading_comprehension_data as rcd
# Step 0: Create a list of all links on the subreddit:

# Step 1.1: Compare against existing list to see if associated data has already been scraped
#       Do this by comparing pages that have already been downloaded.


# Step 1.2: Iterate through each non-archived page - grabbing the whole page's information.
#d.grab_data_json("HFY", "submission", after_time=0, f_name="output_submission2", sleep_time=2, query_count=100)  # Downloads subreddit into 50mb JSON files.
# d.grab_data_json("HFY", "comment", after_time=0, f_name="output_comment3", sleep_time=1, query_count=100)

# Grabbing sister-communities:


"""
humansarespaceorcs
humansarespacebards
humansarespaceferrets
RedditSerials
TurningtoWords

Hunter_or_Huntress
NatureofPredators
NatureOfPredatorsNSFW (?)
Sexyspacebabes
GATEhouse
bubblewriters
"""
# d.grab_data_json("humansarespaceorcs", "submission", after_time=0, f_name="HASO_Submissions01", sleep_time=2, query_count=100)
# d.grab_data_json("humansarespacebards", "submission", after_time=0, f_name="HASB_Submissions01", sleep_time=2, query_count=100)
#d.grab_data_json("humansarespaceferrets", "submission", after_time=0, f_name="HASF_Submissions01", sleep_time=2, query_count=100)
#d.grab_data_json("Hunter_or_Huntress", "submission", after_time=0, f_name="HoH_Submissions01", sleep_time=2, query_count=100)
#d.grab_data_json("NatureofPredators", "submission", after_time=0, f_name="NoP_Submissions01", sleep_time=2, query_count=100)
#d.grab_data_json("NatureOfPredatorsNSFW", "submission", after_time=0, f_name="NoPNSFW_Submissions01", sleep_time=2, query_count=100)
#d.grab_data_json("Sexyspacebabes", "submission", after_time=0, f_name="SSB_Submissions01", sleep_time=2, query_count=100)
#d.grab_data_json("GATEhouse", "submission", after_time=0, f_name="GATEhouse_Submissions01", sleep_time=2, query_count=100)
# ... after initial dataset is created, get the msot recent time and then only grab stuff that is newer... unless wanting to increment versions of older posts.


# To grab new post data:
# 1a. Scan through all .json files in directory that are submission/comment files
# 1b. Find the newest .json file
# 1c. Find the most recently grabbed post/comment
# 1d. Scan from the most recent time to current.
# 1e. As posts can be made at the same second - with one being grabbed but not the other, you have to start at that exact same time
#       meaning you may get duplicated (or you *wlll* 100% get at least 1 duplicate).
# 1f. For every new post, check to see if you already have it in the database.
# 1g. If you do, check to see if the content (or likes/metadata) has been updated.
# 1h. if it has been, make a new revision-history for that doc...(?)
# 1i. Else, just create a new document like normal...

gil2.main_save_imgur_images(f_name="HFY_images", json_title='submission2')


# rcd.create_corpus(skip_compilation=True)
