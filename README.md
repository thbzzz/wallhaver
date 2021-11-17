# Wallhaver

[Wallhaven](https://wallhaven.cc) API client to change your desktop background randomly sometimes :)

Currently, it only works on GNOME (tested on 3.38) but you can easily adapt it to i3, KDE, Windows or whatever by tweaking the `cmd` string in the `set_background` function.

## Installation

Clone this repo and install required modules using `pip`.

```sh
git clone https://github.com/thbzzz/wallhaver.git
cd wallhaver
pip install -r requirements.txt
```

Set the `WALLPAPERS_DIRECTORY` according to your environment: it should be the absolute path of the directory where you want to store downloaded wallpapers, like `/home/user/pictures/wallpapers`.

## Usage

Running the script will pull an image from <https://wallhaven.cc> according to provided keywords and options, save it in a folder, and put it as desktop wallpaper.

```
usage: wallhaver.py [-h] [--just-dl] [--ratio {16x9,16x10}] [--min-size {1920x1080,1920x1200}] [--purity {sfw,sketchy,nsfw}] [--sorting {random,date_added,relevance,views,favorites,toplist}] [--page PAGE] keywords [keywords ...]

positional arguments:
  keywords              keywords for searching wallpapers

optional arguments:
  -h, --help            show this help message and exit
  --just-dl             just download an image but don't set it as desktop wallpaper
  --ratio {16x9,16x10}  wallpaper's dimensions ratio
  --min-size {1920x1080,1920x1200}
                        wallpaper's minimum dimensions
  --purity {sfw,sketchy,nsfw}
                        wallpaper's max purity
  --sorting {random,date_added,relevance,views,favorites,toplist}
                        sorting method
  --page PAGE           page number to search
```

For example, running:

```
wallhaver.py dog
```

will set your wallpaper to a (probably) cute dog image.

If you have a wide screen and you prefer ducks, instead you can do:

```
wallhaver.py --ratio 16x10 --min-size 1920x1200 --sorting favorites duck
```

Because an image is downloaded each time the script is called, be careful of the size of your `WALLPAPERS_DIRECTORY`.

## Automation

You can use everything you want to automate the execution of this script.

Personally, I wrapped it in a `systemd` service to run it at boot time.

`touch ~/.config/systemd/user/wallhaver.service`

```
[Unit]
Description=Change your wallpaper at boot

[Service]
Type=simple
StandardOutput=journal
Execstart=/path/to/wallhaver.py duck

[Install]
WantedBy=default.target
```

Enable it with `systemctl`:

```
systemctl --user enable wallhaver.service  # run the script each next boots
systemctl --user start wallhaver.service  # run the script now
```

Now your wallpaper will be updated each time the system is fully booted.

## API key

No API key is needed to query the Wallhaven API. Having an API key only gives access to NSFW content.

To get one, register at https://wallhaven.cc/join and find it in your account settings.

Then, create a `.env` file next to the `wallhaver.py` script and put `API_KEY=<key>` inside.
