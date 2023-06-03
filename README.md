# DiscordLolQuiz
A Discord Bot to play some League of Legends Quiz

# Install

```bash
git clone https://github.com/Theodrob/DiscordLolQuiz
```

## Requirements:

```bash
pip install discord
```

```bash
pip install Pillow
```

## Start the bot

Before starting the bot, you will need to add your Discord Token in the variable `TOKEN` on line 18.

Start the bot:

```bash
cd DiscordLolQuiz
```

```bash
python3 ./LoLQuizBot.py
```

# Games

## Skin guesser

Discord Command: `!skin`

The bot selects one random splash art from the `splash` folder, and zoom on it.  

Players have to guess whose champion is this splash art by typing `?g [champion]`.  

The champion name is not sensitive to case, and it's not necessary to type "'" or to put blank space for champions like
Kai'Sa, Rek'Sai, Tahm Kench, etc.

Every 10 failed guesses, the image will zoom out.

## Spell guesser

Discord Command: `!spell`
The bot selects one random spell from the `spell` folder, and pixelize it.

Players have to guess whose champion is this spell by typing `?g [champion] [Q|W|E|R]`.  

The champion name is not sensitive to case, and it's not necessary to type "'" or to put blank space for champions like
Kai'Sa, Rek'Sai, etc. And you must NOT put blank space in the middle of the name. (e.g. Tahm Kench -> TahmKench)

Every 5 failed guesses, the image will be resent with more pixels.

# Sources

The images come from [Data Dragon](https://riot-api-libraries.readthedocs.io/en/latest/ddragon.html), and are from the patch 13.10.
You may want to update it by downloading the sources with latest patch, and replace the current ones.

/!\ Important:
Whereas splash art names are already all with good format (`champion_1.jpg`), spell icons are not.
There are different formats and most of them use `championQ.png`. If you plan to update sources, you'll have to rename
every spell icons with this format.

You can use this script to check which images don't have the right format:
```python
import os

splash_folder = "./spell"
names = os.listdir(splash_folder)
i = 0
for icon in names:
    name = icon.split(".")[0]
    if name[-1] not in ["Q", "W", "E", "R"]:
        print(name)
        i += 1
print("Remaining :", i)
```

# Custom the game
You may want to change some parts of the code, for example the prefixes.  

The prefix to start the game (!) is defined on line 16 
```python
bot = commands.Bot(command_prefix="!", intents=intents)
```
You can change it if you want to avoid a conflict with another bot for example.

The prefix used to give an answer (?g) is defined on line 20:
```python 
prefix = "?g"
```