# Discord-Bot
A discord bot including lol stats, chatting, music and more

## How to use?
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
