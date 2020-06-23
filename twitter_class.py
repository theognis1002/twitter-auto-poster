import oauth2
import json
import time
import sys
from config import API_KEY, API_SECRET, ACCESS_KEY, ACCESS_SECRET, queries


class Twitter:
    def __init__(self):
        self.consumer = oauth2.Consumer(key=API_KEY, secret=API_SECRET)
        self.access_token = oauth2.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
        self.client = oauth2.Client(self.consumer, self.access_token)

    def get_timeline(self):
        timeline_endpoint = "https://api.twitter.com/1.1/statuses/home_timeline.json"
        response = self.client.request(timeline_endpoint, method="GET")
        data = json.loads(response[1])
        return response[0], data

    def filtered_tweets(self, keyword):
        timeline_endpoint = f"https://api.twitter.com/1.1/search/tweets.json?" \
                            f"q={keyword}&result_type=mixed&count=100"
        response = self.client.request(timeline_endpoint, method="GET")
        data = json.loads(response[1])
        if len(data['statuses']) == 0:
            print(f"No tweets found for keyword: '{keyword.upper()}'")
            sys.exit(0)
        return response[0], data

    def like_tweet(self, t_id):
        time.sleep(5)
        timeline_endpoint = f"https://api.twitter.com/1.1/favorites/create.json?id={t_id}"
        response = self.client.request(timeline_endpoint, method="POST")
        data = json.loads(response[1])

        try:
            if data['favorited']:
                print(f"Tweet #{t_id} favorited.")
            else:
                print(f"Tweet#{t_id} error.")
        except KeyError:
            error_message = data['errors'][0]['message']
            print(error_message)
            if "To protect our users from spam and other malicious activity" in error_message:
                exit()
        return response[0], data

    def get_user_id(self, user_name):
        timeline_endpoint = f"https://api.twitter.com/1.1/users/search.json?q={user_name}&count=3"
        response = self.client.request(timeline_endpoint, method="GET")
        data = json.loads(response[1])
        user_id = data[0]['id']
        return user_id

    def follower_list(self, user_id):
        timeline_endpoint = f"https://api.twitter.com/1.1/followers/list.json?user_id={user_id}&count=200"
        response = self.client.request(timeline_endpoint, method="GET")
        data = json.loads(response[1])
        return response[0], data

    def friend_list(self, user_id):
        timeline_endpoint = f"https://api.twitter.com/1.1/friends/list.json?user_id={user_id}"
        response = self.client.request(timeline_endpoint, method="GET")
        data = json.loads(response[1])
        return data

    def show_friendship_details(self, user_id, target_user):
        time.sleep(1)
        timeline_endpoint = f"https://api.twitter.com/1.1/friends/list.json?source_id={user_id}&target_id={target_user}"
        response = self.client.request(timeline_endpoint, method="GET")
        data = json.loads(response[1])
        return data

    def follow_user(self, user_id):
        try:
            timeline_endpoint = f"https://api.twitter.com/1.1/friendships/create.json?user_id={user_id}"
            response = self.client.request(timeline_endpoint, method="POST")
            data = json.loads(response[1])
            name = data['name']
            screen_name = data['screen_name']
            print(f"Followed back {name} (@{screen_name})")
        except Exception as e:
            print(str(e))

