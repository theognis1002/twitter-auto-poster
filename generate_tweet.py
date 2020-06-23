import dropbox
import random
import os
import json
from config import DBX_ACCESS_TOKEN


TWEET_CHOICE = ['SERVICES IMAGES', 'TESTIMONIALS', 'PROFITS', 'GENERAL TWEETS']


def delete_image(file_name):
    os.remove(file_name)
    print(f"Deleted image file: '{file_name}'")


def create_random_tweet():
    # loads tweet category, selects random tweet, hashtag(s), url snippet
    tweet_category = random.choice(TWEET_CHOICE)
    tweet_list = json.loads(open('tweet_list.json').read())
    hashtags = ' '.join(random.sample(tweet_list['HASHTAGS'], random.randint(1, 3)))
    random_tweet_image_filename = None
    random_url = random.choice(tweet_list['URL_SNIPPETS'])
    url_snippet = " " + random_url + " " if len(random_url) else " "

    # get tweet image if not general tweet
    if tweet_category != 'GENERAL TWEETS':
        dbx = dropbox.Dropbox(DBX_ACCESS_TOKEN)
        nested_folder = tweet_category

        dbx_root_folder = "/apps/TBL Twitter Images/" + nested_folder + "/"

        random_tweet_image_filename = (random.choice(dbx.files_list_folder(dbx_root_folder).entries)).name
        random_tweet_image_location = dbx_root_folder + random_tweet_image_filename

        # download image from dropbox
        with open(random_tweet_image_filename, 'wb') as f:
            metadata, r = dbx.files_download(random_tweet_image_location)
            f.write(r.content)

        if nested_folder == 'SERVICES IMAGES':
            if 'dropchecker' in random_tweet_image_filename.lower():
                services_nested_key = 'DROPCHECKER'
            elif 'presale' in random_tweet_image_filename.lower() or 'list' in random_tweet_image_filename.lower():
                services_nested_key = 'PRESALE_LIST'
            elif 'event_tracker' in random_tweet_image_filename.lower() or 'list' in random_tweet_image_filename.lower():
                services_nested_key = 'EVENT_TRACKER'
            else:
                # exit function if image not labelled correctly due to inability to parse json file correctly
                return False

            random_tweet = random.choice(tweet_list[nested_folder]['TWEETS'][services_nested_key]) + \
                                url_snippet + hashtags
        else:
            random_tweet = random.choice(tweet_list[tweet_category]['TWEETS']) + " " + hashtags

    else:
        random_tweet = random.choice(tweet_list[tweet_category]['TWEETS']) + " " + hashtags

    return random_tweet, random_tweet_image_filename


if __name__ == '__main__':
    pass
