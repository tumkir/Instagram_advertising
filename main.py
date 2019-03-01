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


def get_username_of_participants(who_mentioned_friends_list, who_liked_list, who_following_list):
    ids_all_participants = set(who_mentioned_friends_list).intersection(who_liked_list, who_following_list)
    username_all_participants = [bot.get_username_from_user_id(id) for id in ids_all_participants]
    return username_all_participants


if __name__ == '__main__':
    load_dotenv()
    args = get_arguments()
    bot = Bot()
    bot.login(username=getenv("login"), password=getenv("password"), use_cookie=False)
    id_image = bot.get_media_id_from_link(args.media_url)
    ids_who_liked = bot.get_media_likers(id_image)
    ids_who_following = bot.get_user_followers(args.media_owner)
    ids_who_mentioned_friends = []
    all_comments = bot.get_media_comments_all(id_image)
    for comment in all_comments:
        mentioned_friends = get_mentioned_friends(comment['text'])
        if not mentioned_friends:
            continue
        for friend in mentioned_friends:
            id_from_username = bot.get_user_id_from_username(friend)
            if id_from_username is None:
                continue
            ids_who_mentioned_friends.append(str(comment['user_id']))
    all_participants = get_username_of_participants(ids_who_mentioned_friends, ids_who_liked, ids_who_following)
    print(all_participants)
