# Discord-Bot
A discord bot including lol stats, chatting, music and more

## How to use?
### Create missing files and directories

Create a file named `Tokens.json` in `./res/settings`. This file allows to run different bots (Tokens) without having to change the code.
Content should be of the type 
<pre><code>{
  "Bot" : {
    "name of bot 1" : ["Token 1", "Welcome channel id"],
    "name of bot 2" : ["Token 2", "Welcome channel id"],
    ...more bots...
  },
  "LoL" : "Riot API Key"
}
</code></pre>
To change the default bot, you must edit line 136 of `Discord_Bot.py`.


### Install required modules

Use `sudo pip3 install` or `sudo python3 -m pip install` to install the following modules if you are running a raspberry pi with oled 128x64 display. Otherwise, omit `sudo`:
* [py-cord](https://docs.pycord.dev/en/stable/)
* [yt-dlp](https://github.com/yt-dlp/yt-dlp))
* [psutil](https://github.com/giampaolo/psutil)
* [PyNaCl](https://github.com/pyca/pynacl/)
* [adafruit-circuitpython-ssd1306](https://github.com/adafruit/Adafruit_CircuitPython_SSD1306)
* [pillow](https://python-pillow.org/)
* [requests](https://requests.readthedocs.io/en/latest/)
* [opencv-python](https://opencv.org/)
* [scikit-image](https://scikit-image.org/)

In addition, you must install [ffmpeg](https://ffmpeg.org/) to be able to play music.

### Running the bot
In a terminal, run `python3 <Path-to-project>/Discord_Bot.py` to run the default bot. To select another one, simply add its name at the end. For example `python3 <Path-to-project>/Discord_Bot.py Test`.
If you want to use the 128x64 display, you must add `sudo` before.


This discord bot was created under Riot Games' "Legal Jibber Jabber" policy using assets owned by Riot Games.  Riot Games does not endorse or sponsor this project.

## Support, feature request and contact
You can join my [discord server](https://discord.gg/F6bjEfKybV) for any question or post an issue on github.
