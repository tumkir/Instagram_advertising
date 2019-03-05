import argparse
import re
from os import getenv

from dotenv import load_dotenv
from instabot import Bot


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('media_url')
    parser.add_argument('media_owner')
    args = parser.parse_args()
    return args


def get_mentioned_friends(comment):
    # Regex for Instagram Username:
    # https://blog.jstassen.com/2016/03/code-regex-for-instagram-username-and-hashtags/
    pattern = '(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'
    mentioned_friends = re.findall(pattern, comment)
    return mentioned_friends


def get_username_of_participants(ids_mentioned_friends, ids_likers, ids_followers):
    ids_all_participants = set(ids_mentioned_friends.keys()).intersection(ids_likers, ids_followers)
    username_all_participants = [ids_mentioned_friends[id] for id in ids_all_participants]
    return username_all_participants


if __name__ == '__main__':
    load_dotenv()
    args = get_arguments()
    bot = Bot()
    bot.login(username=getenv("login"), password=getenv("password"), use_cookie=False)
    id_image = bot.get_media_id_from_link(args.media_url)
    ids_likers = bot.get_media_likers(id_image)
    ids_followers = bot.get_user_followers(args.media_owner)
    ids_mentioned_friends = {}
    all_comments = bot.get_media_comments_all(id_image)
    for comment in all_comments:
        mentioned_friends = get_mentioned_friends(comment['text'])
        if not mentioned_friends:
            continue
        for friend in mentioned_friends:
            id_from_username = bot.get_user_id_from_username(friend)
            if id_from_username is None:
                continue
            ids_mentioned_friends[str(comment['user_id'])] = comment['user']['username']
    all_participants = get_username_of_participants(ids_mentioned_friends, ids_likers, ids_followers)
    print(all_participants)
