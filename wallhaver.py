#!/usr/bin/env python3

from argparse import ArgumentParser
from json import loads
from os import W_OK, X_OK, access
from os.path import basename, expanduser, isdir, join
from random import randint
from subprocess import run
from urllib.parse import urlparse

from dotenv import dotenv_values
from requests import get as httpget

"""Wallhaven (https://wallhaven.cc) API client to change your desktop background randomly sometimes :)"""

WALLPAPERS_DIRECTORY = "/tmp/wallhaver"  # CHANGE ME


class Wallhaver:
    def __init__(self):
        self.base_url = "https://wallhaven.cc/api/v1/"
        self.dir = WALLPAPERS_DIRECTORY
        self.env = dotenv_values()

        if not isdir(self.dir):
            exit(f"directory {self.dir} doesn't exist")

        if not access(self.dir, X_OK | W_OK):
            exit(f"directory {self.dir} isn't writable")

    def set_background(self, wp_file: str):
        cmd = "gsettings set org.gnome.desktop.background picture-uri file://" + wp_file
        return run(cmd.split())
    
    def download(self, url: str, file: str, chunk_size: int=8192):
        with httpget(url, stream=True) as r:
            r.raise_for_status()

            with open(file, "wb") as f:
                for chunk in r.iter_content(chunk_size):
                    f.write(chunk)

        return True

    def search(self, **kwargs):
        endpoint = self.base_url + "search/"
        
        if req := self._get(endpoint, params=kwargs):
            data = loads(req.text)
        
        return data

    def _get(self, url: str, params: dict):
        headers = {
            "X-API-KEY": self.env["API_KEY"]
        }

        return httpget(url, headers=headers, params=params)

if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)

    parser.add_argument("--just-dl",
                      action="store_true",
                      default=False,
                      help="just download an image but don't set it as desktop wallpaper")

    parser.add_argument("--ratio",
                      choices=["16x9", "16x10"],
                      default="16x9",
                      help="wallpaper's dimensions ratio")
    
    parser.add_argument("--min-size",
                      choices=["1920x1080", "1920x1200"],
                      default="1920x1080",
                      help="wallpaper's minimum dimensions")
    
    parser.add_argument("--purity",
                      choices=["sfw", "sketchy", "nsfw"],
                      default="sfw",
                      help="wallpaper's max purity")
    
    parser.add_argument("--sorting",
                      choices=["random", "date_added", "relevance", "views", "favorites", "toplist"],
                      default="random",
                      help="sorting method")
    
    parser.add_argument("--page",
                      type=int,
                      default=1,
                      help="page number to search")

    parser.add_argument("keywords",
                      nargs="+",
                      help="keywords for searching wallpapers")

    args = vars(parser.parse_args())

    translate_purity = {"sfw":"100","sketchy":"110","nsfw":"111"}

    search_params = {
        "q": " ".join(args["keywords"]),
        "sorting": args["sorting"],
        "ratio": args["ratio"],
        "atleast": args["min_size"],
        "page": args["page"],
        "purity": translate_purity[args["purity"]],
    }

    # Seed to randomize random (must be like [a-zA-Z0-9]{6})
    if search_params["sorting"] == "random":
        search_params["seed"] = "babibu"

    wallhaver = Wallhaver()

    data = wallhaver.search(**search_params)

    # Check if provided page exists
    last_page = int(data["meta"]["last_page"])
    if args["page"] > last_page:
        exit(f"last page is {last_page}")

    # Some search terms return nothing
    if not data["data"]:
        exit("no wallpaper found :(")

    # If wallpapers are found, just choose a random one in the list
    # A full page contains 64 wallpapers
    per_page = int(data["meta"]["per_page"])
    wp = data["data"][randint(1, per_page-1)]

    wp_url = wp["path"]
    wp_file = join(wallhaver.dir, basename(urlparse(wp_url).path).removeprefix("wallhaven-"))

    if wallhaver.download(wp_url, wp_file):
        wallhaver.set_background(wp_file)
