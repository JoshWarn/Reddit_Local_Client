import definitions as d
import process_submissions as p
import os
import urllib
from urllib.error import HTTPError
import requests
import re
import time
import hashlib


def process_imgur_links(imgur_image_links, text_links, url_id_list, subreddit_list, post_title_list,
                        author_list, t_created_list, t_accessed_list, nsfw_list,
                        img_folder_name="Images3"):
    # TODO instead of numbers, use the imgur-link-hash and an md5 of the file as the image-name
    # TODO find which file-hashes are the "this content doesn't exist anymore" and don't save them.
    # This would allow new images to be added as more links are scraped over time.

    # tries to make an image folder to put all the images into
    make_folder(img_folder_name)

    # goes through links in reverse order:
    print(f"Total Links found: {len(imgur_image_links)}")

    # Deletes duplicates in a list; only leaving the oldest (furthest down in the list)
    # e.g. [1, 2, 2, 3, 1, 2] -> [3, 1, 2].
    # TODO make a dedicated function for this later.
    # TODO this has the HUGE issue of removing older versions of a link - could shuffle list.
    # A bad solution to that is to go through the list in-order but shift the deleted index by the number of deletions
    deleted_count = 0
    for i in range(len(imgur_image_links)):
        if imgur_image_links.count(imgur_image_links[i - deleted_count]) > 1:
            imgur_image_links.pop(i - deleted_count)
            text_links.pop(i - deleted_count)
            url_id_list.pop(i - deleted_count)
            subreddit_list.pop(i - deleted_count)
            post_title_list.pop(i - deleted_count)
            author_list.pop(i - deleted_count)
            t_created_list.pop(i - deleted_count)
            nsfw_list.pop(i - deleted_count)
            deleted_count += 1
    print(f"Total Links found after deleting duplicates: {len(imgur_image_links)}")


    # return imgur_image_links # TODO this is temporary to compare which links each function finds


    # TODO This doesn't actually do what I want; I want for numbers to go 1 -> + with index going from 999 -> - -> 1.
    for i in range(len(imgur_image_links)):
        # print(imgur_image_links)
        imgur_link_ext = "." + imgur_image_links[i].split(".")[-1]
        print(f"{i}/{len(imgur_image_links)}", imgur_image_links[i], imgur_link_ext)
        # if it's a single image or direct link, download
        if imgur_link_ext in [".jpg", ".jpeg", ".png", ".gif", ".mp4"]:
            imgur_hash = imgur_image_links[i].split(".")[-2].split("/")[-1]
            save_img_and_create_metadata(img_folder_name, imgur_hash, imgur_image_links[i], text_links[i], imgur_image_links[i], url_id_list[i],
                                        subreddit_list[i], post_title_list[i], author_list[i], t_created_list[i],
                                        t_accessed_list[i], nsfw_list[i])

        # the link is in the form of a gallery:
        else:
            # get image links from blog-gallery, embed-gallery, and general-gallery:
            blog_gallery_image_links = grab_imgur_blog_links(imgur_image_links[i])
            embed_gallery_image_links = grab_imgur_embed_links(imgur_image_links[i])
            general_gallery_image_links = grab_imgur_general_links(imgur_image_links[i])
            #print("v1", blog_gallery_image_links)
            #print("v2", embed_gallery_image_links)
            #print("v3", general_gallery_image_links)
            # Combines all the link-lists into a single list and removes duplicates (and some h-variants)
            combined_img_links = combine_lists_and_remove_dupes([blog_gallery_image_links, embed_gallery_image_links,
                                                                 general_gallery_image_links])
            print(blog_gallery_image_links, embed_gallery_image_links, general_gallery_image_links)
            print(combined_img_links)
            # print("A", combined_img_links)
            # if there is more than one file, make a folder - else just place at the lowest level
            gallery_hash = imgur_image_links[i].split("/")[-1]
            if len(combined_img_links) > 1:     # more than one file in folder

                # make a folder for the images
                gallery_folder_path = f"{img_folder_name}/{gallery_hash}"
                make_folder(gallery_folder_path)

                for j in range(len(combined_img_links)):

                    # grab and save image
                    img_data, img_data_ext = direct_imgur_image_link_download(combined_img_links[j])
                    imgur_hash = combined_img_links[j].split(".")[-2].split("/")[-1]
                    file_hash = data_file_hash(img_data)
                    with open(f'{gallery_folder_path}/{imgur_hash}-{file_hash}{img_data_ext}', 'wb') as handler:
                        handler.write(img_data)
                    time.sleep(3)

                # create a single metadata file for all the images

                create_img_metadata_file(img_folder_name, gallery_hash, "0", combined_img_links[j], text_links[i], imgur_image_links[i], url_id_list[i], subreddit_list[i],
                                         post_title_list[i], author_list[i], t_created_list[i],
                                         t_accessed_list[i], nsfw_list[i])

            elif len(combined_img_links) == 1:
                save_img_and_create_metadata(img_folder_name, gallery_hash, combined_img_links[0], text_links[i], imgur_image_links[i], url_id_list[i],
                                            subreddit_list[i], post_title_list[i], author_list[i], t_created_list[i],
                                            t_accessed_list[i], nsfw_list[i])
        time.sleep(10)


def save_img_and_create_metadata(path, imgur_hash, imgur_image_link, text_link, reddit_link, url_id_list, subreddit_list, post_title_list,
                                 author_list, t_created_list, t_accessed_list, nsfw_list):
    img_data, img_data_ext = direct_imgur_image_link_download(imgur_image_link)
    file_hash = data_file_hash(img_data)
    # create the image-file and save image:
    with open(f'{path}/{imgur_hash}-{file_hash}{img_data_ext}', 'wb') as handler:
        handler.write(img_data)
    # create the meta-data file and save metadata:
    create_img_metadata_file(path, imgur_hash, file_hash, imgur_image_link, text_link, reddit_link, url_id_list, subreddit_list,
                             post_title_list, author_list, t_created_list,
                             t_accessed_list, nsfw_list)


def preprocess_data_for_imgur_links(preview, links, text, url_ids, subreddits, titles, authors, created, accessed, nsfw):
    # goal here is to go through all links and check if it's an imgur link
    processed_links, processed_text_links = [], []
    processed_url_id_list, processed_subreddit_list, processed_post_title_list, processed_author_list = [], [], [], []
    processed_t_created_list, processed_t_accessed_list, processed_nsfw_list = [], [], []
    for i in range(len(links)):
        #if len(preview[i]) > 0:
            # print(f"Preview Image:{preview[i]}")
            # TODO not implemented scraping these yet; they're embedded into reddit.


        for j in range(len(links[i])):
            # make sure link is imgur link
            imgur_link_matchs = re.findall('(https?://(www\.)?(i\.|m\.)?(stack\.)?imgur\.com//?(a/|gallery/)?(r/[a-zA-Z0-9]+/)?[a-zA-Z0-9]+(\.(jpg|jpeg|png|gif|mp4))?)',
                                    links[i][j])
            if len(imgur_link_matchs) > 0:
                #print("A", imgur_link_matchs)
                #print("B", imgur_link_matchs[0][0])
                processed_links.append(imgur_link_matchs[0][0])
                processed_text_links.append(text[i][j])
                processed_url_id_list.append(url_ids[i])
                processed_subreddit_list.append(subreddits[i])
                processed_post_title_list.append(titles[i])
                processed_author_list.append(authors[i])
                processed_t_created_list.append(created[i])
                processed_t_accessed_list.append(accessed[i])
                processed_nsfw_list.append(nsfw[i])

    return processed_links, processed_text_links, processed_url_id_list, processed_subreddit_list, \
           processed_post_title_list, processed_author_list, processed_t_created_list, processed_t_accessed_list, \
           processed_nsfw_list


def combine_lists_and_remove_dupes(list_array):
    combined_list = []
    for i in range(len(list_array)):
        for j in range(len(list_array[i])):
            if list_array[i][j] not in combined_list:
                combined_list.append(list_array[i][j])
    # NOTE this also removes h-variants *IF* (and only if) there is a non-h-variant in the list
    # This will NOT remove h-variants that don't have a non-h-variant in the list.
    # that has to be done in the main function - or at least somewhere where files are being read.

    # Getting the hashes of all the imgur images
    imgur_img_hash_list = []
    for i in range(len(combined_list)):
        if combined_list[i].count('.') >= 2:
            imgur_img_hash_list.append(combined_list[i].split(".")[-2])
        else:
            imgur_img_hash_list.append(combined_list[i].split("/")[-1])

    #print("Hash List", imgur_img_hash_list)
    # if a trailing-h-hash with the h removed is already in the list, remove
    for j in range(len(combined_list) - 1, -1, -1):
        if imgur_img_hash_list[j][-1] == 'h':
            # print(hash_list[j], combined_link_list[j], hash_list[j][0:-1])
            if imgur_img_hash_list[j][0:-1] in imgur_img_hash_list:
                # print(f"removing {hash_list[j]}")
                imgur_img_hash_list.pop(j)
                combined_list.pop(j)
    #print("Reduced Combined List", combined_list)
    return combined_list


def grab_imgur_blog_links(url):
    url = url + "/layout/blog"
    html_data = str(html_grab_withfiveohfour_error_wrap(url))
    search_string = 'content="(https://i\.imgur\.com/[a-zA-Z0-9]+\.jpg|jpeg|png|gif|mp4|jpg\?1|png\?1)"'
    raw_image_links = re.findall(search_string, html_data)
    return raw_image_links


def grab_imgur_embed_links(url):
    url = url + "/embed?pub=tru"
    html_data = str(html_grab_withfiveohfour_error_wrap(url))

    hash_search_string = '"hash":"([a-zA-Z0-9]+)"'
    exts_search_string = '"ext":"\.(jpg|jpeg|png|gif|mp4|jpg\?1|png\?1)"'

    hash_list = re.findall(hash_search_string, html_data)
    exts_list = re.findall(exts_search_string, html_data)

    raw_image_links = []
    for i in range(len(hash_list)):
        # print("test string", f"https://i.imgur.com/{hash_list[i]}.{exts_list[i]}")
        raw_image_links.append(f"https://i.imgur.com/{hash_list[i]}.{exts_list[i]}")
    return raw_image_links


def grab_imgur_general_links(url):
    html_data = str(html_grab_withfiveohfour_error_wrap(url))

    search_string = 'content="(https://i\.imgur\.com/[a-zA-Z0-9]+\.jpg|jpeg|png|gif|mp4|jpg\?1|png\?1)"'
    raw_image_links = re.findall(search_string, html_data)
    return raw_image_links


def html_grab_withfiveohfour_error_wrap(url):
    # Named after the most frequent HTML error (504), but also works with 503.
    error = 504
    while error == 504 or error == 503:
        try:
            response = urllib.request.urlopen(url)
            html_data = response.read()
            response.close()
            return html_data
        except HTTPError as err:
            if err.code == 404:
                return ""
                print(f"404 Error! {err}")
            elif err.code == 504 or err.code == 503:
                error = error.code
            else:
                raise


def create_img_metadata_file(path, imgur_hash, file_hash, imgur_image_link, text_link, reddit_link, url_ids, subreddit, title, author,
                             t_created, t_access, nsfw_state, encoding="utf-8"):
    with open(f"{path}/{imgur_hash}-{file_hash}.txt", 'w', encoding=encoding) as f:
        f.write(f"{url_ids}\n")
        f.write(f"{text_link}\n")
        f.write(f"{reddit_link}\n")
        f.write(f"{imgur_image_link}\n")
        f.write(f"{imgur_hash}\n")
        f.write(f"{file_hash}\n")
        f.write(f"{subreddit}\n")
        f.write(f"{title}\n")
        f.write(f"{author}\n")
        f.write(f"{t_created}\n")
        f.write(f"{t_access}\n")
        f.write(f"{nsfw_state}\n")


def direct_imgur_image_link_download(link):
    """
    TODO try check for h-files and try non-h;
    # Don't know what processing was done before and want to make this robust.
    # confirm that the link has a known extension
    #
    :param link: Imgur link to the image-download
    :param ext: Extension of the image download.
    :return:
    """
    # Gets the image-type extension e.g., .png, .jpg, .jpeg, .gif, .gifv, .mp4
    link_ext = "." + link.split(".")[-1]

    # Don't know why I'm getting a ".jpg?1" ext.
    # This may be obsolete if I've found the root cause elsewhere.
    # if extension is .jpg?1, replace with .jpg.
    if link_ext == ".jpg?1":
        link_ext = ".jpg"
        link = link.replace(".jpg?1", ".jpg")
    if link_ext == ".png?1":
        link_ext = ".png"
        link = link.replace(".png?1", ".png")


    # confirming that the extension is a valid type
    if link_ext not in (".jpg", ".jpeg", ".png", ".gif", ".mp4"):
        raise Exception(f"Direct Imgur link has wrong extension!\n Link found: {link}")

    # Time to open the file

    # Error 504 is gateway timeout error; Basically the server didn't recieve data it requested.
    # Basically if this error is hit, wait a bit and retry; It's not an error in the code.

    error = 504

    if link.split(".")[-2][-1] == 'h':  # if trailing
        # make non-h-link
        h_pos = link.rfind('h')
        nonhlink = link[0:h_pos] + link[h_pos + 1:]
        # print("TESTING", link, nonhlink)
        while error == 504:
            try:
                response = requests.get(nonhlink, timeout=20)
                img_data = response.content
                response.close()
                error = 0
            except HTTPError as err:
                if err.code == 504:
                    error = err.code
                    print(f"HTTPError 504 on non-h: Retrying... ")
                # TODO Handle 404 errors here???? Just going to raise 404 errors for now. Will likely change later.
                elif error == 404:
                    print("non-h 404 error!")
                    print(f"NOT BREAKING; Trying h-img")
                    pass
                # TODO Make an exception here for if my internet dies... Error 421?
                else:
                    print(f"Error raised on non-h: {err}")
                    print(f"NOT BREAKING; Trying h-img")
                    error = err.code
                    pass
    else:
        while error == 504:
            try:
                # end bad code time.
                response = requests.get(link, timeout=20)
                img_data = response.content
                response.close()
                error = 0

            except HTTPError.code as error:
                if error == 504:
                    print(f"HTTPError 504: Retrying... ")

                # TODO Handle 404 errors here???? Just going to raise 404 errors for now. Will likely change later.
                elif error == 404:
                    print("404 error!")
                    raise
                # TODO Make an exception here for if my internet dies... Error 421?
                else:
                    raise

    return img_data, link_ext


def make_folder(folder_name):
    """
    # Tries to create a folder if it doesn't already exist.
    # If it exists, it does nothing.
    :param folder_name: The name of the folder being created
    :return: NONE
    """

    try:
        os.makedirs(folder_name)
    except WindowsError as ex:
        if ex.winerror == 183:  # If the folder already exists
            print(f"Tried creating folder; folder {folder_name} Already exists; continuing.")
        else:
            raise


def main_save_imgur_images(f_name="Images4", json_title='submission2'):
    post_ids, subreddits, titles, author, t_created, _, t_accessed, _, _, likes, _, nsfw, previews, \
    _, _, _, _, _, links, link_texts = p.process_submission_json_data(json_title)

    imgur_image_links, text_links, url_id_list, subreddit_list, title_list, author_list, t_created_list, t_accessed_list, \
    nsfw_list = preprocess_data_for_imgur_links(previews, links, link_texts, post_ids, subreddits, titles, author,
                                                t_created, t_accessed, nsfw)

    process_imgur_links(imgur_image_links, text_links, url_id_list, subreddit_list, title_list,
                            author_list, t_created_list, t_accessed_list, nsfw_list,
                            img_folder_name=f_name)


def data_file_hash(data):
    if type(data) is bytes:
        hash_obj = hashlib.md5(data)
        hash_str = hash_obj.hexdigest()
    else:
        data = str.encode(str(data))
        hash_obj = hashlib.md5(data)
        hash_str = hash_obj.hexdigest()
    return str(hash_str)


# main_save_imgur_images(f_name="HFY_images", json_title='submission2')
