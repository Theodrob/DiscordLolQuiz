import os
import discord
from discord.ext import commands
import random
import logging
from PIL import Image

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

intents = discord.Intents.all()  # or .all() if you ticked all, that is easier


bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = ""

prefix = "?g"

GUESS_SKIN_ATTEMPT = 0
GUESS_SKIN_IS_PLAYING = False
GUESS_SKIN_IMAGE = None
GUESS_SKIN_CHAMPION = None
GUESS_SKIN_CURRENT_IMAGE = None
GUESS_SKIN_X = 0
GUESS_SKIN_Y = 0


GUESS_SPELL_ATTEMPT = 0
GUESS_SPELL_IS_PLAYING = False
GUESS_SPELL_IMAGE = None
GUESS_SPELL_CHAMPION = None
GUESS_SPELL_CURRENT_IMAGE = None
GUESS_SPELL_X = 0
GUESS_SPELL_Y = 0

scoreboard = {}


async def zoom_in():
    global GUESS_SKIN_ATTEMPT, GUESS_SKIN_Y, GUESS_SKIN_X, GUESS_SKIN_IMAGE
    lvl = GUESS_SKIN_ATTEMPT // 10
    image_file = f"./splash/{GUESS_SKIN_IMAGE}"
    image = Image.open(image_file)

    # Get the size of the image
    width, height = image.size

    # Define the size of the zoom area

    zoom_factor = 0.2 + lvl/10
    max_zoom_factor = 0.8
    zoom_width = int(width * zoom_factor)
    zoom_height = int(height * zoom_factor)

    max_zoom_width = int(width * max_zoom_factor)
    max_zoom_height = int(height * max_zoom_factor)

    if GUESS_SKIN_X == 0 and GUESS_SKIN_Y == 0:

        # Generate random coordinates for the top left corner of the zoom area
        x = random.randint(0, width - max_zoom_width)
        y = random.randint(0, height - max_zoom_height)
        GUESS_SKIN_X = x
        GUESS_SKIN_Y = y
    else:
        x = GUESS_SKIN_X
        y = GUESS_SKIN_Y


    # Extract the zoomed area from the image
    zoomed_image = image.crop((x, y, x + zoom_width, y + zoom_height))

    # Define the name of the zoomed image file
    zoomed_image_file = "./guess_image.jpg"

    # Save the image
    zoomed_image.save(zoomed_image_file)

    # Return the image file name
    return zoomed_image_file


@bot.command()
async def skin(ctx, *args):
    global GUESS_SKIN_IS_PLAYING, GUESS_SKIN_ATTEMPT, GUESS_SKIN_IMAGE, GUESS_SKIN_CHAMPION, GUESS_SKIN_CURRENT_IMAGE

    # Check is a game is already in progress before starting a new one
    if GUESS_SKIN_IS_PLAYING or GUESS_SPELL_IS_PLAYING:
        await ctx.reply("Game already in progress")
        return

    # Select a random splash art
    splash_folder = "./splash"
    img = random.choice(os.listdir(splash_folder))
    #logger.info(img)

    # Initialization of the game
    GUESS_SKIN_ATTEMPT = 0
    GUESS_SKIN_IS_PLAYING = True
    GUESS_SKIN_IMAGE = img
    GUESS_SKIN_CHAMPION = img.split("_")[0].lower()
    GUESS_SKIN_CURRENT_IMAGE = await zoom_in()

    # Send the image to the discord channel
    file = discord.File(GUESS_SKIN_CURRENT_IMAGE)
    await ctx.send(file=file)


async def is_skin_guess_correct(guess):
    # Ignores "'" characters and blank spaces in case a player wants to try "Kai'Sa"  or "Kai Sa" while the answer
    # will be kaisa
    if guess.lower().replace("'", "").replace(" ", "") == GUESS_SKIN_CHAMPION:
        return True
    else:
        return False


# Remove the zoomed image and set all the values to default
async def resetSkin():
    global GUESS_SKIN_IMAGE, GUESS_SKIN_IS_PLAYING, GUESS_SKIN_CHAMPION, GUESS_SKIN_ATTEMPT, GUESS_SKIN_CURRENT_IMAGE, \
        GUESS_SKIN_X, GUESS_SKIN_Y, scoreboard

    os.remove(str(GUESS_SKIN_CURRENT_IMAGE))

    GUESS_SKIN_ATTEMPT = 0
    GUESS_SKIN_IS_PLAYING = False
    GUESS_SKIN_IMAGE = None
    GUESS_SKIN_CHAMPION = None
    GUESS_SKIN_CURRENT_IMAGE = None
    GUESS_SKIN_X = 0
    GUESS_SKIN_Y = 0
    scoreboard = {}


async def guess_the_skin(message):
    global GUESS_SKIN_IMAGE, GUESS_SKIN_IS_PLAYING, GUESS_SKIN_CHAMPION, GUESS_SKIN_ATTEMPT, GUESS_SKIN_CURRENT_IMAGE, \
        GUESS_SKIN_X, GUESS_SKIN_Y, scoreboard

    # Remove the "?g" at the beginning of the message
    guess = message.content[len(prefix):]
    channel = message.channel
    found = await is_skin_guess_correct(guess)

    # Manages the scoreboard
    if message.author.name not in scoreboard:
        scoreboard[message.author.name] = 1
    else:
        scoreboard[message.author.name] += 1

    # Ends the game if someone found the right answer
    if found:
        score = ""
        for player in scoreboard:
            score += f"{player} : {scoreboard[player]} attempts\n"
        await message.reply(f"Correct ! Found in {GUESS_SKIN_ATTEMPT + 1} attempts\n{score}")
        file = discord.File(f"./splash/{GUESS_SKIN_IMAGE}")
        await message.reply(file=file)
        await resetSkin()

    # Ends the game if 60 attempts were made
    elif GUESS_SKIN_ATTEMPT == 60:
        await channel.send(f"You lost! ... It was {GUESS_SKIN_CHAMPION}...")
        file = discord.File(f"./splash/{GUESS_SKIN_IMAGE}")
        await channel.send(file=file)
        await resetSkin()

    # If the answer is wrong, deletes the message and zoom out every 10 attempts
    else:
        await message.delete()
        GUESS_SKIN_ATTEMPT += 1
        if GUESS_SKIN_ATTEMPT % 10 == 0:
            GUESS_SKIN_CURRENT_IMAGE = await zoom_in()
            file = discord.File(str(GUESS_SKIN_CURRENT_IMAGE))
            await channel.send(file=file)


async def pixelize():
    global GUESS_SPELL_ATTEMPT, GUESS_SPELL_Y, GUESS_SPELL_X, GUESS_SPELL_IMAGE

    image_path = f"./spell/{GUESS_SPELL_IMAGE}"
    if GUESS_SPELL_ATTEMPT > 0:
        pixel_size = 50 // GUESS_SPELL_ATTEMPT
    else:
        pixel_size = 20

    image = Image.open(image_path)

    # Get image size
    width, height = image.size

    # Calculate the amount of pixels
    num_pixels_x = width // pixel_size
    num_pixels_y = height // pixel_size

    # Resize the image by using the method "NEAREST" to get a pixelized effect
    resized_image = image.resize((num_pixels_x, num_pixels_y), Image.NEAREST)

    # Resize the image to its original size
    final_image = resized_image.resize((width, height), Image.NEAREST)

    pixelized_img = f"./spell/guess_image.png"
    final_image.save(pixelized_img)

    return pixelized_img


@bot.command()
async def spell(ctx, *args):
    global GUESS_SPELL_IS_PLAYING, GUESS_SPELL_ATTEMPT, GUESS_SPELL_IMAGE, GUESS_SPELL_CHAMPION, \
        GUESS_SPELL_CURRENT_IMAGE

    if GUESS_SKIN_IS_PLAYING or GUESS_SPELL_IS_PLAYING:
        await ctx.reply("Game already in progress")
        return

    # Selects random image
    splash_folder = "./spell"
    img = random.choice(os.listdir(splash_folder))
    # logger.info(img)

    # Initializes the game
    GUESS_SPELL_ATTEMPT = 0
    GUESS_SPELL_IS_PLAYING = True
    GUESS_SPELL_IMAGE = img
    champion = img.split(".")[0][:-1].lower()
    spell = img.split(".")[0][-1].lower()
    GUESS_SPELL_CHAMPION = f"{champion} {spell}"
    GUESS_SPELL_CURRENT_IMAGE = await pixelize()

    logger.info(GUESS_SPELL_CHAMPION)

    file = discord.File(GUESS_SPELL_CURRENT_IMAGE)
    await ctx.send(file=file)


async def is_spell_guess_correct(guess):
    if guess.lower().replace("'", "").strip() == GUESS_SPELL_CHAMPION:
        return True
    else:
        return False


# Removes the image file and reset values to default
async def resetSpell():
    global GUESS_SPELL_IMAGE, GUESS_SPELL_IS_PLAYING, GUESS_SPELL_CHAMPION, GUESS_SPELL_ATTEMPT, GUESS_SPELL_CURRENT_IMAGE, \
        GUESS_SPELL_X, GUESS_SPELL_Y, scoreboard

    os.remove(str(GUESS_SPELL_CURRENT_IMAGE))

    GUESS_SPELL_ATTEMPT = 0
    GUESS_SPELL_IS_PLAYING = False
    GUESS_SPELL_IMAGE = None
    GUESS_SPELL_CHAMPION = None
    GUESS_SPELL_CURRENT_IMAGE = None
    GUESS_SPELL_X = 0
    GUESS_SPELL_Y = 0
    scoreboard = {}


async def guess_the_spell(message):
    global GUESS_SPELL_IMAGE, GUESS_SPELL_IS_PLAYING, GUESS_SPELL_CHAMPION, GUESS_SPELL_ATTEMPT, \
        GUESS_SPELL_CURRENT_IMAGE, GUESS_SPELL_X, GUESS_SPELL_Y, scoreboard

    # Removes the "?g" at the beginning of the message
    guess = message.content[len(prefix):]

    # Manages scoreboard
    if message.author.name not in scoreboard:
        scoreboard[message.author.name] = 1
    else:
        scoreboard[message.author.name] += 1

    channel = message.channel
    found = await is_spell_guess_correct(guess)

    # Ends the game if someone found the right answer
    if found:
        score = ""
        for joueur in scoreboard:
            score += f"{joueur} : {scoreboard[joueur]} attempts\n"
        await message.reply(f"Correct ! found in {GUESS_SPELL_ATTEMPT + 1} attempts\n{score}")
        file = discord.File(f"./spell/{GUESS_SPELL_IMAGE}")
        await message.reply(file=file)
        await resetSpell()

    # Ends the game after 60 attempts
    elif GUESS_SPELL_ATTEMPT == 60:
        await channel.send(f"You lost! ...  The right answer was : {GUESS_SPELL_CHAMPION}...")
        file = discord.File(f"./spell/{GUESS_SPELL_IMAGE}")
        await channel.send(file=file)
        await resetSpell()

    # If the answer is wrongs, deletes the message and add more pixels after 5 attempts
    else:
        await message.delete()
        GUESS_SPELL_ATTEMPT += 1
        if GUESS_SPELL_ATTEMPT % 5 == 0:
            GUESS_SPELL_CURRENT_IMAGE = await pixelize()
            file = discord.File(str(GUESS_SPELL_CURRENT_IMAGE))
            await channel.send(file=file)


@bot.event
async def on_message(message):

    if GUESS_SKIN_IS_PLAYING and message.content[:len(prefix)] == prefix:
        await guess_the_skin(message)

    elif GUESS_SPELL_IS_PLAYING and message.content[:len(prefix)] == prefix:
        await guess_the_spell(message)

    await bot.process_commands(message)


bot.run(TOKEN)
