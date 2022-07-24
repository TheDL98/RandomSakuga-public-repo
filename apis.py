# Copyright (C) 2022 Ahmed Alkadhim
#
# This file is part of Random Sakuga.
#
# Random Sakuga is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Random Sakuga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Random Sakuga.  If not, see <http://www.gnu.org/licenses/>.

import requests
import logging
from urllib.parse import urljoin

import logger_config


logger = logging.getLogger("logger_config")


def get_sb_post(limit: int, tags: str) -> dict:
    # Get random posts from Sakugabooru
    payload = {"limit": limit, "tags": tags}
    url = "https://www.sakugabooru.com/post.json"
    posts_response = requests.get(url, payload)

    # Select the highest scored post
    high_score = 0
    high_post: dict
    for post in posts_response.json():
        if post["score"] >= high_score:
            high_post, high_score = post, int(post["score"])
    logger.info(f"Sakuga Booru post ID: {high_post['id']}")
    return high_post


def tag_summary(prev_tag_summary: dict) -> dict:
    # Request a summary json of all the tags on the site and convert it to a list
    url = "https://www.sakugabooru.com/tag/summary.json"
    tag_summary: dict = requests.get(url)
    if prev_tag_summary["version"] != tag_summary.json()["version"]:
        prev_tag_summary["version"] = tag_summary.json()["version"]
        prev_tag_summary["tags"] = tag_summary.json()["data"].split(" ")
        for i in range(len(prev_tag_summary["tags"])):
            prev_tag_summary["tags"][i] = prev_tag_summary["tags"][i].split("`")
            prev_tag_summary["tags"][i].remove("")
    return prev_tag_summary


# Query IMDb using imdb-api.com
def imdb_search(media: str, api_key: str) -> dict | None:
    url = f"https://imdb-api.com/en/API/AdvancedSearch/{api_key}"
    payload = {"title": media, "genres": "animation", "count": "1"}
    try:
        imdb_result = requests.get(url, payload)
        return imdb_result.json()["results"][0]
    except IndexError:
        return None


# Use the Jikan unofficial MyAnimeList API to search for anime shows
def jikan_mal_search(media: str, jikan_local_address: str | bool) -> dict | None:
    default_url = "https://api.jikan.moe/v3/search/anime"
    try:
        if jikan_local_address:
            requests.get(jikan_local_address)
            url = urljoin(jikan_local_address, "v3/search/anime")
        else:
            url = default_url
    except requests.exceptions.ConnectionError:
        logger.error(
            "No connection to your local Jikan API. "
            "Make sure your server is up and the address is correct."
        )
        url = default_url

    payload = {"q": media, "limit": 1}
    try:
        jikan_response = requests.get(url, payload)
        if not jikan_response.ok:
            raise requests.HTTPError(
                "{0[type]}: {0[status]}\n\t{0[message]}".format(jikan_response.json())
            )
        mal_result = jikan_response.json()["results"][0]
        return mal_result
    except requests.HTTPError as e:
        logger.error(e)
        return None


# Create a Facebook video post
def fb_video_post(page_id: str, file: bytes, payload: str) -> int | None:
    url = f"https://graph.facebook.com/{page_id}/videos"
    try:
        fb_post_response = requests.post(url, payload, files={"source": file})
        if not fb_post_response.ok:
            raise requests.HTTPError(
                "{0[type]}: {0[code]}\n\t{0[message]}".format(
                    fb_post_response.json()["error"]
                )
            )
        return int(fb_post_response.json()["id"])
    except requests.HTTPError as e:
        logger.error(e)
        return None


# Create an FB comment
def fb_comment(access_token: str, post_id: int, comment: str) -> str:
    fb_comment_url = f"https://graph.facebook.com/{post_id}/comments"
    fb_comment_payload = {"access_token": access_token, "message": comment}
    fb_comment_response = requests.post(fb_comment_url, fb_comment_payload)
    return fb_comment_response.json()["id"]
