from twitter_class import Twitter
from generate_tweet import create_random_tweet, delete_image
import tweepy
import twitter_class
import urllib.parse
from datetime import timedelta, datetime
import time
import json
import random
import requests
import threading
from config import TWITTER_USER_ID, queries


def get_timeline():
    tw = Twitter()
    tweets = tw.get_timeline()[1]

    for tweet in tweets:
        print(tweet['created_at'])
        print(tweet['id'])
        print(tweet['id_str'])
        time.sleep(2)


def search_and_like_tweets(query):
    search_query = urllib.parse.quote(query)
    tw = Twitter()
    tweets = tw.filtered_tweets(search_query)[1]
    tweet_id_list = []
    try:
        for tweet in tweets['statuses']:
            print(f"@{tweet['user']['screen_name']}")
            tweet_id = tweet['id']
            print(tweet['created_at'])
            print("------------------------------------------------------------------\n"
                  + tweet['text'].strip() + "\n------------------------------------------------------------------\n\n")
            tweet_id_list.append(tweet_id)
            time.sleep(1)

        for tweet_id in tweet_id_list:
            tw.like_tweet(tweet_id)
        time.sleep(10)
    except json.decoder.JSONDecodeError as e:
        print(str(e))
    time.sleep(30)


def follow_back_followers():
    tw = Twitter()
    data = tw.follower_list(TWITTER_USER_ID)
    followers = data[1]['users']

    print("Following back followers...")
    for follower in followers:
        user_id = follower['id']
        screen_name = follower['screen_name']
        follow_bool = follower['following']
        if not follow_bool:
            tw.follow_user(user_id)
            print("You are now following " + user_id, screen_name)

        else:
            continue
    time.sleep(30)


def destroy_non_followers():
    auth = tweepy.OAuthHandler(twitter_class.API_KEY, twitter_class.API_SECRET)

    # Get access token
    auth.set_access_token(twitter_class.ACCESS_KEY, twitter_class.ACCESS_SECRET)

    # Construct the API instance
    api = tweepy.API(auth)

    # gets cursor list of people @TBL_Broker_List is following
    print("Getting friends (following list)...")

    unfollow_count = 0

    for friend in tweepy.Cursor(api.friends, id=TWITTER_USER_ID, page=10, wait_on_rate_limit=True).items():
        if friend.followers_count < 20000:  # if user has more than 250 followers
            screen_name = friend.screen_name
            target_id = friend.id
            target_user = api.show_friendship(source_id=TWITTER_USER_ID, target_id=target_id)

            if not target_user[1].following:  # if they do not follow back
                api.destroy_friendship(target_id)
                print(f"Unfollowed @{screen_name}.")

                unfollow_count += 1
                if unfollow_count > 50:
                    print(f"Unfollowed {unfollow_count} users.")
                    break
                if unfollow_count % 10 == 0:
                    print(unfollow_count)

            else:
                pass  # skips if they are a follower
        else:
            pass  # skips if they have under 250 followers
        time.sleep(5)


def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError as e:
            print(str(e[0]['message']))
            time.sleep(15 * 60)
        except StopIteration:
            print("Done.")
            break


def process_status(sta):
    print(sta)


def follow_users():
    auth = tweepy.OAuthHandler(twitter_class.API_KEY, twitter_class.API_SECRET)

    # Get access token
    auth.set_access_token(twitter_class.ACCESS_KEY, twitter_class.ACCESS_SECRET)

    # Construct the API instance
    api = tweepy.API(auth)

    my_follower_list = []

    for follower in tweepy.Cursor(api.followers, wait_on_rate_limit=True).items():
        time.sleep(1)
        print("Appended " + follower.id + " - " + follower.screen_name)
        my_follower_list.append(follower.id)

    print(my_follower_list)

    time.sleep(10)

    for i in range(3):
        try:
            for follower in tweepy.Cursor(api.followers, screen_name="TicketFlipping", wait_on_rate_limit=True).items():
                print(follower.id)
                if (follower.friends_count < 300) and (follower.id not in my_follower_list):
                    follower.follow()
                    print("https://twitter.com/" + str(follower.screen_name))
                    time.sleep(2)
            break
        except tweepy.error.TweepError as e:
            print(str(e))
            time.sleep(60)
            pass
    time.sleep(30)


def get_new_follower_list():
    auth = tweepy.OAuthHandler(twitter_class.API_KEY, twitter_class.API_SECRET)

    # Get access token
    auth.set_access_token(twitter_class.ACCESS_KEY, twitter_class.ACCESS_SECRET)

    # Construct the API instance
    api = tweepy.API(auth)

    the_list = []

    for friend in tweepy.Cursor(api.friends, wait_on_rate_limit=True).items(150):
        print("https://twitter.com/" + str(friend.screen_name))
        the_list.append(friend.screen_name)
        time.sleep(1.5)

    print(the_list)

    for follower in tweepy.Cursor(api.followers, screen_name="TicketSummit", wait_on_rate_limit=True).items():
        # print(follower.screen_name)
        if follower.screen_name in the_list:
            time.sleep(1.5)
            pass
        else:
            print("https://twitter.com/" + str(follower.screen_name))
            time.sleep(1.5)
    time.sleep(30)


# check who you are following
def get_friends():
    auth = tweepy.OAuthHandler(twitter_class.API_KEY, twitter_class.API_SECRET)

    # Get access token
    auth.set_access_token(twitter_class.ACCESS_KEY, twitter_class.ACCESS_SECRET)

    # Construct the API instance
    api = tweepy.API(auth)

    user = api.get_user(TWITTER_USER_ID)

    # appends followers to list

    print("Gathering followers...")
    followers = []
    for follower in tweepy.Cursor(api.followers, wait_on_rate_limit=True).items():
        followers.append(follower)
        time.sleep(1)

    time.sleep(3)

    cursor_limit = 200
    print(f"Found {user.followers_count} followers, gathering info on {cursor_limit} of {user.friends_count} friends...")
    friends = []
    for friend in tweepy.Cursor(api.friends, wait_on_rate_limit=True).items(cursor_limit):
        print(friend.screen_name)
        friends.append(friend)
        time.sleep(0.5)

    # creating dictionaries based on id's is handy too

    friend_dict = {}
    for friend in friends:
        friend_dict[friend.id] = friend

    follower_dict = {}
    for follower in followers:
        follower_dict[follower.id] = follower

    # now we find all your "non_friends" - people who don't follow you
    # even though you follow them.

    non_friends = [friend for friend in friends if friend.id not in follower_dict]

    for nf in reversed(non_friends):
        print("Unfollowing " + str(nf.screen_name).rjust(10))
        try:
            nf.unfollow()
        except:
            print(" ... failed, sleeping for 5 seconds and then trying again.")
            time.sleep(5)
            nf.unfollow()
        time.sleep(1)
    time.sleep(3)


def destroy_likes():
    auth = tweepy.OAuthHandler(twitter_class.API_KEY, twitter_class.API_SECRET)

    # Get access token
    auth.set_access_token(twitter_class.ACCESS_KEY, twitter_class.ACCESS_SECRET)

    # Construct the API instance
    api = tweepy.API(auth)
    try:
        page = 85
        for i in range(25):
            print(f"************************Page #{page}************************")
            for favorite in tweepy.Cursor(api.favorites, id=TWITTER_USER_ID, page=page, wait_on_rate_limit=True).items():
                created_date = favorite.created_at
                older_than_2_weeks = datetime.today() - timedelta(days=14)
                if created_date < older_than_2_weeks:
                    favorited = api.destroy_favorite(favorite.id).favorited
                    if not favorited:
                        print(f"[Created on {str(created_date)}] - ID# {str(favorite.id)} - Tweet unliked.")
                    else:
                        print("Error")
                elif created_date > older_than_2_weeks:
                    print(f"[Created on {str(created_date)}] - ID# {str(favorite.id)} - Like is less than 2 weeks old.")
                else:
                    print("N/A")
                    pass
                time.sleep(1.5)
                continue
            page += 1
            time.sleep(5)
            # Encoding in utf-8 is a good practice when using data from twitter that users can submit
            # (it avoids the program crashing because it can not encode characters like emojis)
    except (tweepy.error.TweepError, json.decoder.JSONDecodeError) as e:
        print(str(e))
    time.sleep(3)


def follow_new_followers():
    auth = tweepy.OAuthHandler(twitter_class.API_KEY, twitter_class.API_SECRET)

    # Get access token
    auth.set_access_token(twitter_class.ACCESS_KEY, twitter_class.ACCESS_SECRET)

    # Construct the API instance
    api = tweepy.API(auth)

    r = requests.get('https://phantombuster.s3.amazonaws.com/lt3yvKe4YMs/apOfrPhsoMqHCUigU4Hx4A/result.json')
    new_friends = r.json()

    for new_friend in new_friends:
        # print(new_friend)
        try:
            if int(new_friend['followers_count']) < 500:
                screen_name = new_friend['screenName']
                api.create_friendship(screen_name)
                print("Followed " + screen_name)
            else:
                pass
        except tweepy.error.TweepError as e:
            pass

        time.sleep(1)


def get_mentions_timeline():
    auth = tweepy.OAuthHandler(twitter_class.API_KEY, twitter_class.API_SECRET)

    # Get access token
    auth.set_access_token(twitter_class.ACCESS_KEY, twitter_class.ACCESS_SECRET)

    # Construct the API instance
    api = tweepy.API(auth)
    mentions = api.mentions_timeline()
    for mention in mentions:
        print(str(mention.id) + ' - ' + mention.text)


def post_tweet():
    auth = tweepy.OAuthHandler(twitter_class.API_KEY, twitter_class.API_SECRET)

    # Get access token
    auth.set_access_token(twitter_class.ACCESS_KEY, twitter_class.ACCESS_SECRET)

    # Construct the API instance
    api = tweepy.API(auth)

    # generate random tweet and image
    tweet, file_name = create_random_tweet()

    if file_name:
        t = threading.Timer(7, delete_image, [file_name])
        t.start()
        api.update_with_media(file_name, status=tweet)
    else:
        api.update_status(tweet)

    print(f"Successful tweet: '{tweet}' [Image: {file_name}]")


def main():
    post_tweet()
    destroy_likes()

    random.shuffle(queries)
    for query in queries:
        search_and_like_tweets(query)


if __name__ == "__main__":
    main()




