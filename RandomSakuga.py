# Copyright (C) 2021 Ahmed Alkadhim
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

from sys import stdout
from time import strftime, localtime, sleep
from tempfile import NamedTemporaryFile
import requests
import logging
import os
import funcs
import options


version = "V1.16"
print(f"RandomSakuga {version}", end="\n\n")


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler_format = logging.Formatter(
    "%(levelname)s<%(asctime)s>%(module)s:%(message)s", "%Y-%m-%d %H:%M:%S"
)
strream_handler_format = logging.Formatter("%(levelname)s:%(module)s:%(message)s")

file_handler = logging.FileHandler("RandomSakuga.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_handler_format)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
stream_handler.setFormatter(strream_handler_format)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


if options.root_logger:
    logging.basicConfig(
        filename="debug.log",
        level=logging.DEBUG,
        format="%(levelname)s<%(asctime)s>%(name)s:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# Global variables
tag_summary_dict = {"version": None, "tags": []}


def post():
    global tag_summary_dict
    sb_post = funcs.get_sb_post(options.sb_limit, options.sb_tags)
    tag_summary_dict = funcs.tag_summary(tag_summary_dict)
    artist, media = funcs.artist_and_media(sb_post["tags"], tag_summary_dict["tags"])
    mal_info = funcs.jikan_mal_search(media, sb_post["tags"])
    fb_payload = funcs.create_fb_post_payload(
        sb_post["id"], artist, media, options.fb_access_token
    )
    temp_file_data = requests.get(sb_post["file_url"])
    # Create a temporary file
    with NamedTemporaryFile() as tf:
        tf.name = "dl_file." + sb_post["file_ext"]
        tf.write(temp_file_data.content)
        tf.seek(0)
        fb_post_id = funcs.fb_video_post(options.fb_page_id, tf, fb_payload)
    if fb_post_id:
        if mal_info:
            funcs.fb_MAL_comment(
                options.fb_access_token, fb_post_id, mal_info["mal_id"]
            )

        logger.info(f"Facebook post ID: {fb_post_id}")
        post_feedback = (
            f"post({fb_post_id}) on {strftime('%d/%m/%Y, %H:%M:%S', localtime())}"
        )
        print(post_feedback)
        print(len(post_feedback) * "-", end="\n\n")


try:
    # One post when the script starts if set to True
    if options.single_mode:
        post()

    # Scheduler setup
    if options.schedule_mode:
        while True:
            if os.name == "posix":
                stdout.write("\033[2K\033[1G")  # Erase and go to beginning of line
            print(strftime("%H:%M", localtime()), end="\r")

            # Scheduler
            # Post every six hours at (00:00, 06:00, ...)
            hour_ = localtime().tm_hour % 6
            minute = localtime().tm_min
            if hour_ == 0 and minute == 0:
                post()
            sleep(60)  # wait one minute
except KeyboardInterrupt:  # ! PyInstaller doesn't handle this well (PyInstaller #3646)
    print("\nInterrupt signal received!")
