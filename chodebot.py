import os
# import random
import asyncio
import logging
import discord
import datetime
import refs.keywords
import refs.reactions
import refs.guildsinfo
import refs.randomstuff
from pathlib import Path
from dotenv import load_dotenv
from discord.ext import commands
from typing import Literal, Optional
from cogs.mondocs import MsgToKeepTrackOf  #, CountChannel, GuessChannel, TriviaQuestions
from mongoengine import connect, disconnect, DEFAULT_CONNECTION_NAME

#  ToDo: Add Command For Checking Individual Game Data From Within My Priv-Channel
#   Systems; Question of Thee Day, polling feature, (Music Player?)
#   Games; Hangman, Daily Number Guess Game, Would you Rather, Connect 4
#   ______________________________________________MORE URGENTLY______________________________________________
#   fix the new logging system to properly account for custom font for better logging
#   Add new checks to message edit/delete to ignore 'ignore_keys'.
#   ______________________________________________MORE URGENTLY______________________________________________

# logger = logging.getLogger(__name__)
# file_handler = logging.FileHandler(filename='log.log', mode='w', encoding='utf-8')
# nul_handler = logging.NullHandler()
# console_handler = logging.StreamHandler()
# logger.addHandler(file_handler)
# logger.addHandler(nul_handler)
# logger.addHandler(console_handler)
# logger.setLevel(logging.INFO)


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    return logger


logger = setup_logger("logger", "log.log")
logger_count = setup_logger("logger_count", "log_count.log")
logger_guess = setup_logger("logger_guess", "logger_guess.log")
logger_hangman = setup_logger("logger_hangman", "logger_hangman.log")

# logger = logging.getLogger(__name__)
# file_handler = logging.FileHandler('log.log')
# console_handler = logging.StreamHandler()
# logger.addHandler(file_handler)
# logger.addHandler(console_handler)
# logger.setLevel(logging.INFO)

load_dotenv()
DISTOKEN = os.getenv("TOKEN")
OWNERID = int(os.getenv("OWNERID"))
OWNERTAG = f"<@{OWNERID}>"
PermError = os.getenv("PermError")
NoFileError = os.getenv("NoFileError")
OwnPermError = os.getenv("OwnPermError")
ErrorMsgOwner = os.getenv("ErrorMsgOwner")
mongo_login_string = os.getenv("monlog_string")
mongo_default_collection = os.getenv("mondef_string")
main_path = Path(__file__).parent.absolute()

keyds = refs.keywords
reans = refs.reactions
guifo = refs.guildsinfo
ranff = refs.randomstuff
ignore_keys = ranff.ignore_keys


bot = discord.ext.commands.Bot(command_prefix='$', intents=discord.Intents.all())
# bot.remove_command('help')
startup_extensions = [
    "mondocs",
    "commands",
    "warnsys",
    "directory_thread",
    "economy",
    "events",
    "count",
    "sentence",
    "guessing",
    "trivia",
    "hangman"
]


def __init__(self):
    self.bot = bot


async def load_extensions():
    for extension in startup_extensions:
        try:
            await bot.load_extension(f"cogs.{extension}")
            logger.info(f"Loaded {extension}")
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Failed to load {extension}: {exc}")


async def connect_mongo():
    try:
        client = connect(mongo_default_collection, host=mongo_login_string, alias=DEFAULT_CONNECTION_NAME)
        formatted_time = await fortime()
        logger.info(f"{ranff.long_dashes}\n{formatted_time}: MongoDB Connected")
        return client
    except Exception as e:
        formatted_time = await fortime()
        logger.error(f"{formatted_time}: {e}")
        return None


async def get_database(client):
    try:
        db = client.get_default_database(mongo_default_collection)
        formatted_time = await fortime()
        logger.info(f"{formatted_time}: Database loaded")
        return db
    except Exception as e:
        formatted_time = await fortime()
        logger.error(f"{formatted_time}: {e}")


async def number_emojis(guess):
    if guess == 69:
        return "😉"
    elif guess == 100:
        return "💯"
    elif guess == 210:
        return "🖖"
    elif guess == 420:
        return "🍁"
    elif guess == 666:
        return "🔥"
    elif guess == 777:
        return "🎲"
    elif guess == 1000:
        return "💸"
    elif guess == 2000:
        return "🍰"
    elif guess == 3000:
        return "☣️"
    elif guess == 4000:
        return "🌈"
    elif guess == 5000:
        return "💠"
    elif guess == 6000:
        return "➰"
    elif guess == 7000:
        return "👅"
    elif guess == 8000:
        return "🧟"
    elif guess == 9000:
        return "🦴"
    elif guess == 10000:
        return "🆘"
    else:
        return None


async def guildid_check(ctx, guildid: int, channel_type: str):
    try:
        if guildid == guifo.pettysqad_id:
            if channel_type == "general":
                return guifo.pettysqad_general_chat
            else:
                await ctx.channel.send(f"CHANNEL_TYPE DOESN't MATCH")
                return None
        elif guildid == guifo.chodeling_id:
            if channel_type == "general":
                return guifo.spc_priv_test
            else:
                await ctx.channel.send(f"CHANNEL_TYPE DOESN't MATCH")
                return None
        else:
            await ctx.channel.send(f"GUILDID DOESN't MATCH")
            return None
    except Exception as e:
        await ctx.channel.send(f"Error -- {e}")
        print(e)
        return None


async def owner_check(ctx, guildid):
    if guildid == guifo.pettysqad_id:
        return guifo.pettysqad_owner_id
    elif guildid == guifo.chodeling_id:
        return guifo.chodeling_owner_id
    elif guildid == guifo.chroniclers_id:
        return guifo.chroniclers_owner_id
    elif guildid == guifo.cemetery_id:
        return guifo.cemetery_owner_id
    elif guildid == guifo.mellowzone_id:
        return guifo.mellowzone_owner_id
    elif guildid == guifo.queenpalace_id:
        return guifo.queenpalace_owner_id
    elif guildid == guifo.catino_id:
        return guifo.catino_owner_id
    elif guildid == guifo.dark_lair_id:
        return guifo.dark_lair_owner_id
    elif guildid == guifo.fire_floozie_id:
        return guifo.fire_floozie_owner_id
    else:
        await ctx.reply(ErrorMsgOwner.format(OWNERTAG, "Guild Records could not be found in owner_check"))
        return None


async def rannumb_comparasion(document):
    try:
        field = None
        if document['lastguessed'] < document['answer']:
            field = "Thee answer is higher than thee guess"
        elif document['lastguessed'] > document['answer']:
            field = "Thee answer is lower than thee guess"
        return field
    except Exception as e:
        formatted_time = await fortime()
        logger.error(f"{formatted_time}: Something went wrong in rannum_comp -- {e}")
        return None


# ToDo: Split up based on if guess is longer than answer, and have two separate checks based on
#  Might be thee only way I get this fucking fixed properly..............................
#  Or.. Give in and redo it, so we tell people which letters are in the correct spot...
async def ranword_comparasion(guess, document):
    correct_position, correct_letter, wrong_letter = 0, 0, 0
    new_wrong_more = False
    already_checked_right, already_checked_wrong_spot, already_checked_not = "", "", ""
    if len(guess) >= len(document['answer']):
        for_target = document['answer']
        if_target = guess
        new_wrong_more = True
    else:
        for_target = guess
        if_target = document['answer']
    try:
        for i, letter in enumerate(for_target):
            right_letter_spot = False
            if i >= len(if_target):
                break
            if letter == if_target[i]:
                if letter in already_checked_right or letter in already_checked_wrong_spot:
                    answer_count = document['answer'].count(letter)
                    guess_count = guess.count(letter)
                    if new_wrong_more:
                        if guess_count < answer_count:
                            wrong_letter += 1
                            already_checked_not += letter
                        else:
                            right_letter_spot = True
                    else:
                        if 1 < answer_count and answer_count > already_checked_right.count(letter) or answer_count > already_checked_wrong_spot.count(letter):
                            right_letter_spot = True
                        else:
                            wrong_letter += 1
                            already_checked_not += letter
                else:
                    right_letter_spot = True
                if right_letter_spot:
                    correct_position += 1
                    already_checked_right += letter
            elif letter in if_target:
                answer_count = document['answer'].count(letter)
                guess_count = guess.count(letter)
                already_checked_right_count = already_checked_right.count(letter)
                already_checked_wrong_spot_count = already_checked_wrong_spot.count(letter)
                if answer_count <= already_checked_right_count or answer_count <= already_checked_wrong_spot_count:
                    wrong_letter += 1
                    already_checked_not += letter
                elif letter in already_checked_right or letter in already_checked_wrong_spot:
                    if new_wrong_more:
                        if guess_count < answer_count:
                            wrong_letter += 1
                            already_checked_not += letter
                        else:
                            correct_letter += 1
                            already_checked_wrong_spot += letter
                    elif not new_wrong_more:
                        if guess_count < answer_count:
                            wrong_letter += 1
                            already_checked_not += letter
                        else:
                            correct_letter += 1
                            already_checked_wrong_spot += letter
                elif new_wrong_more:
                    if letter in already_checked_wrong_spot:
                        wrong_letter += 1
                        already_checked_not += letter
                    else:
                        correct_letter += 1
                        already_checked_wrong_spot += letter
                elif not new_wrong_more:
                    if for_target[i] in already_checked_wrong_spot:
                        wrong_letter += 1
                        already_checked_not += letter
                    else:
                        correct_letter += 1
                        already_checked_wrong_spot += letter
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Something Went wrong forloop ranword_comp")
                    return None, None, "This is in relation to letter in if_target"
            elif letter not in if_target:
                wrong_letter += 1
                already_checked_not += letter
        if new_wrong_more:
            new_wrong_letter = abs(len(if_target) - len(for_target))
            wrong_letter += new_wrong_letter
        else:
            new_wrong_letter = abs(wrong_letter - len(for_target)) + wrong_letter
            if new_wrong_letter < wrong_letter:
                wrong_letter = new_wrong_letter
        return correct_position, correct_letter, wrong_letter
    except Exception as e:
        formatted_time = await fortime()
        logger.error(f"{formatted_time}: Something went wrong in ranword_comp -- {e}")
        return None, None, e


async def perm_check(ctx, guildid):
    try:
        if ctx.author.id == OWNERID:
            usersperms = "owner"
            return usersperms
        elif ctx.author.guild_permissions.administrator:
            usersperms = "admin"
            return usersperms

        if guildid == guifo.chodeling_id:
            modrole = ctx.guild.get_role(guifo.chodeling_mod)
            normalrole = ctx.guild.get_role(guifo.chodeling_norm)
        elif guildid == guifo.pettysqad_id:
            modrole = ctx.guild.get_role(guifo.pettysqad_mod)
            normalrole = ctx.guild.get_role(guifo.pettysqad_norm)
        elif guildid == guifo.cemetery_id:
            modrole = ctx.guild.get_role(guifo.cemetery_mod)
            normalrole = ctx.guild.get_role(guifo.cemetery_norm)
        elif guildid == guifo.chroniclers_id:
            modrole = ctx.guild.get_role(guifo.chroniclers_mod)
            normalrole = ctx.guild.get_role(guifo.chroniclers_norm)
        elif guildid == guifo.mellowzone_id:
            modrole = ctx.guild.get_role(guifo.mellowzone_mod)
            normalrole = ctx.guild.get_role(guifo.mellowzone_norm)
        elif guildid == guifo.queenpalace_id:
            modrole = ctx.guild.get_role(guifo.queenpalace_mod)
            normalrole = ctx.guild.get_role(guifo.queenpalace_norm)
        elif guildid == guifo.catino_id:
            modrole = ctx.guild.get_role(1203492587470848050)
            normalrole = ctx.guild.get_role(guifo.catino_norm)
        elif guildid == guifo.dark_lair_id:
            modrole = ctx.guild.get_role(guifo.dark_lair_mod)
            normalrole = ctx.guild.get_role(guifo.dark_lair_norm)
        elif guildid == guifo.fire_floozie_id:
            modrole = ctx.guild.get_role(guifo.fire_floozie_mod)
            normalrole = ctx.guild.get_role(guifo.fire_floozie_norm)
        else:
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, "Guild ID Doesn't match any of my records"))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: {ctx.author.name}/{ctx.author} is trying to perm_check from a guildid ({guildid}) that doesn't match records!!")
            return None

        if modrole in ctx.author.roles:
            usersperms = "mod"
        elif normalrole in ctx.author.roles:
            usersperms = "normal"
        else:
            usersperms = None
        return usersperms
    except AttributeError as e:
        await ctx.reply(f"I couldn't access your perms, are we in a server? -- {e}")
        formatted_time = await fortime()
        logger.error(f"{formatted_time}: {ctx.author.name} from {ctx.guild.name} threw an attribute error in {ctx.channel.name} : {ctx.channel.id} -- {e}")
        return None


async def fortime():
    try:
        nowtime = datetime.datetime.now()
        formatted_time = nowtime.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time
    except Exception as e:
        logger.error(f"Error creating formatted_time -- {e}")
        return None


@bot.event
async def setup_hook():
    bot.client = await connect_mongo()
    await asyncio.sleep(1)
    bot.channel_ids = await get_database(bot.client)
    await load_extensions()


@bot.event
async def on_ready():
    # random_status = random.choice(ranff.random_statuses)
    # await bot.change_presence(activity=discord.Streaming(platform="Twitch", name="PettyBear's OnlyFans", url="https://www.onlyfans.com/roningt"))
    # await bot.change_presence(activity=discord.Streaming(platform="OnlyFans", name="PettyBear's OnlyFans", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
    # await bot.change_presence(activity=discord.Streaming(platform="PettyBear", name="PettyBear's OnlyFans", url="https://www.pettybear.com/"))
    await bot.change_presence(activity=discord.Game(name='Counting Is Tuff'))
    # await bot.tree.sync()
    formatted_time = await fortime()
    logger.info(f"{ranff.long_dashes}\n{formatted_time}: Logged in as: {bot.user.name}\n{ranff.long_dashes}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandError):
        return
        # await ctx.reply(error)
        # formatted_time = await fortime()
        # logger.error(f"{formatted_time}: {error}")
        # return
    if FileNotFoundError(error, discord.ext.commands.CommandError):
        await ctx.reply(NoFileError)
        formatted_time = await fortime()
        logger.error(f"{formatted_time}: {error}")
        return


@bot.tree.command()
async def test_slasher(interaction: discord.Interaction):  #ctx):  #, interaction: discord.Interaction):
    """Just a test"""
    # noinspection PyUnresolvedReferences
    await interaction.response.send_message("Just a test")
    # await interaction.response("Just a test")  # JUST TESTING IF THIS IS "PROPER"
    # await interaction.followup("Just a followup example")  # Just an EXAMPLE


@bot.command()
async def sync_tree(ctx, spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    usersperms = await perm_check(ctx, ctx.guild.id)
    if usersperms != "owner":
        await ctx.reply(OwnPermError)
        return
    if spec == "~":
        synced = await bot.tree.sync(guild=ctx.guild)
    elif spec == "*":
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
    elif spec == "^":
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        synced = []
    else:
        synced = await bot.tree.sync()
    await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")


@bot.command()
async def kickall(ctx):
    usersperms = await perm_check(ctx, ctx.guild.id)
    if usersperms != "owner":
        await ctx.reply(OwnPermError)
        formatted_time = await fortime()
        logger.info(f"{formatted_time}: {ctx.author.name} tried to use thee kickall command from within {ctx.guild.id}.\n{ctx.author.id}")
        return
    m = 0
    n = 1
    members_kicked = ""
    members_not_kicked = ""
    members = ctx.guild.members
    for member in members:
        try:
            if len(member.roles) == 1:
                await member.kick()
                members_kicked += f"{n}:: {member.id} :: {member.name} :: {member.display_name}\n"
                formatted_time = await fortime()
                logger.info(f"{formatted_time}: {n}: {member.id}/{member.name}/{member.display_name} kicked successfully")
                n += 1
        except Exception as e:
            m += 1
            members_not_kicked += f"{m}:: {member.id}:: {member.name} :: {e}\n"
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: {m}: {member.id}/{member.name}/{member.display_name} not kicked :: {e}")
            continue
    await ctx.reply(f"Done, {n} members kicked.")
    for i in range(0, len(members_kicked), 2000):
        await ctx.reply(f"{members_kicked[i:i+2000]}")
    if m != 0:
        await ctx.reply(f"{m} failed to kick")
        for i in range(0, len(members_not_kicked), 2000):
            await ctx.reply(f"{members_not_kicked[i:i+2000]}")


@bot.command()
async def botmsg(ctx, message_event="down", message_channels="global", custom_time=180, custom_message=None, silent_mode=True):
    """Bot Owner Specific
    $msgbot 'message_event' 'message_channels' 'custom_time' 'custom_message' 'silent_mode'"""
    usersperms = await perm_check(ctx, ctx.guild.id)
    if usersperms != "owner":
        await ctx.reply(OwnPermError)
        return
    msg_to_keep_track_of = bot.channel_ids.get_collection('msg_to_keep_track_of')
    if custom_message is not None:
        custom_message = custom_message.replace('_', ' ')
    if message_event == "down":
        response = f"I will be down for an estimated {str(custom_time)} seconds. Await my up message before continuing thee game(s)/using any commands.\n{'Hold Fast' if custom_message is None else custom_message}"
    elif message_event == "up":
        response = f"Back up and running, thanks for thee patience.\n{'Much Love' if custom_message is None else custom_message}"
    elif message_event == "rules_change":
        response = f"Thee rules have been updated, please check the pinned comment for changes.\n{'Much Love' if custom_message is None else custom_message}"
    else:
        await ctx.reply(f"{message_event} not valid")
        return

    if message_channels == "global":
        channels_to_update = guifo.spc_channels_to_update
    elif message_channels == "count":
        channels_to_update = guifo.spc_count_channels
    elif message_channels == "guess":
        channels_to_update = guifo.spc_guess_channels
    elif message_channels == "hangman":
        channels_to_update = guifo.spc_hangman_channels
    elif message_channels == "sent":
        channels_to_update = guifo.spc_sent_channels
    elif message_channels == "test":
        channels_to_update = guifo.spc_test_run
    elif message_channels == "triv":
        channels_to_update = guifo.spc_triv_channels
    else:
        await ctx.reply(f"{message_channels} not valid")
        return
    m = 1
    errors = "Start of Errors:"
    if message_event in ("down", "rules_change"):
        for channelid in channels_to_update:
            try:
                channel = bot.get_channel(channelid)
                message = await channel.send(response, silent=silent_mode)
                new_document = MsgToKeepTrackOf(message_id=message.id, channel_name=channel.name, channel_id=channel.id,
                                                guild_name=channel.guild.name,
                                                message_event=message_event, message_channels=message_channels,
                                                time_down=custom_time)
                new_document_dict = new_document.to_mongo()
                msg_to_keep_track_of.insert_one(new_document_dict)
            except Exception as e:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error creating messages/documents :: {m}::{channelid}: {e}")
                errors = f"{errors}\n{m}::{channelid}: {e}"
                m += 1
                continue
        if errors != "Start of Errors:":
            await ctx.reply(f"Errors creating {message_event} messages/documents\n{errors}")
    elif message_event == "up":
        documents = msg_to_keep_track_of.find({})
        for channelid in channels_to_update:
            try:
                channel = bot.get_channel(channelid)
                await channel.send(response, silent=silent_mode, delete_after=custom_time)
            except Exception as e:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error Creating Up Messages :: {m}::{channelid}: {e}")
                errors = f"{errors}\n{m}: {e}"
                m += 1
                continue
        if errors != "Start of Errors:":
            await ctx.reply(f"Errors creating {message_event} messages/documents\n{errors}")
            errors = "Start of Errors:"
            m = 1
        await asyncio.sleep(custom_time / 4)
        for document in documents:
            try:
                if document['message_event'] == "down":
                    channel = bot.get_channel(document['channel_id'])
                    await channel.delete_messages([discord.Object(id=document['_id'])])
                    msg_to_keep_track_of.delete_one({"_id": document['_id']})
            except Exception as e:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error deleting messages/documents :: {m}: {e} :: {document}")
                new_errors = f"{errors}\n{m}: {e}"
                errors = new_errors
                m += 1
                continue
        if errors != "Start of Errors:":
            await ctx.reply(f"Errors deleting {message_event} messages/documents\n{errors}")


@bot.command()
async def kick(ctx, user: discord.Member, reason="Blank"):
    usersperms = await perm_check(ctx, ctx.guild.id)
    if usersperms not in ("owner", "admin", "mod"):
        await ctx.reply(PermError)
        return
    if user.server_permissions.administrator and usersperms not in ("owner", "admin"):
        await ctx.reply(f"Cannot kick admins")
        return
    await user.kick(reason=reason)
    embed = discord.Embed(title=f"{ctx.author.mention} kicked {user.name}", description=f"Reason: {reason}", color=0xff0000)
    await ctx.send(embed=embed)


@bot.command()
async def load(ctx, cog_name):
    """Loads a cog"""
    usersperms = await perm_check(ctx, ctx.guild.id)
    if usersperms in ("owner", "admin"):
        try:
            await bot.load_extension(f'cogs.{cog_name}')
            formatted_time = await fortime()
            logger.info(f"{formatted_time}: {cog_name} loaded by {ctx.author.name}")
            await ctx.send(f"Loaded {cog_name}")
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: {ctx.author.name} Failed to Load {cog_name}: {exc}")
            await ctx.send(f"Failed to Load {cog_name}: {exc}")
    else:
        await ctx.reply(PermError)
        return


@bot.command()
async def unload(ctx, cog_name):
    """Unloads a cog"""
    usersperms = await perm_check(ctx, ctx.guild.id)
    if usersperms in ("owner", "admin"):
        # adding a sleep to allow cog to finish before unloading
        await asyncio.sleep(1)
        try:
            await bot.unload_extension(f"cogs.{cog_name}")
            formatted_time = await fortime()
            logger.info(f"{formatted_time}: {cog_name} unloaded by {ctx.author.name}")
            await ctx.send(f"Unloaded {cog_name}")
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: {ctx.author.name} Failed to unload {cog_name}: {exc}")
            await ctx.send(f"Failed to unload {cog_name}: {exc}")
    else:
        await ctx.reply(PermError)
        return


@bot.command()
async def reload(ctx, cog_name):
    """Reloads a cog"""
    usersperms = await perm_check(ctx, ctx.guild.id)
    if usersperms in ("owner", "admin"):
        try:
            await unload(ctx, cog_name)
            await asyncio.sleep(1)
            await load(ctx, cog_name)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: {ctx.author.name} Failed to reload {cog_name}: {exc}")
            await ctx.send(f"Failed to reload {cog_name}: {exc}")
    else:
        await ctx.reply(PermError)
        return


@bot.command()
async def checkdb(ctx):
    usersperms = await perm_check(ctx, ctx.guild.id)
    if usersperms in ("owner", "admin", "mod"):
        if ctx.channel.id in (guifo.chodeling_logs, guifo.spc_priv_test, guifo.cemetery_logs, guifo.chroniclers_logs, guifo.pettysqad_logs, guifo.queenpalace_logs):
            try:
                await ctx.reply(f"DB String is: {bot.channel_ids}")
                formatted_time = await fortime()
                logger.info(f"{formatted_time}: Database checked by {ctx.author.name} in {ctx.channel.name} in {ctx.guild.name}")
            except Exception as e:
                await ctx.reply(f"DB isn't loaded: {e}")
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: DB isn't loaded. {ctx.author.name} tried checking it in {ctx.channel.name}" in {ctx.guild.name})
        else:
            prev_author = ctx.author
            await ctx.message.delete()
            await ctx.reply(f"Try again in a 'chodebot-logs' channel {prev_author.mention}. Message TheeChody for clarity if you're unsure", delete_after=10)
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Database check attempt by {ctx.author.name} in {ctx.channel.name}")
    else:
        await ctx.reply(PermError)
        return


@bot.command()
async def reloaddb(ctx):
    """Reloads the whole database"""
    usersperms = await perm_check(ctx, ctx.guild.id)
    if usersperms in ("owner", "admin"):
        try:
            await asyncio.sleep(2)
            disconnect(DEFAULT_CONNECTION_NAME)
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: {ctx.author.name} disconnected the client in {ctx.guild.name}")
        except Exception as e:
            await ctx.reply(f"Client could NOT be disconnected: {e}")
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: {ctx.author.name} attempted to disconnect the client in {ctx.guild.name}\n{e}")
            return
        await asyncio.sleep(2)
        try:
            bot.client = await connect_mongo()
            await asyncio.sleep(1)
            bot.channel_ids = await get_database(bot.client)
            formatted_time = await fortime()
            logger.info(f"{formatted_time}: Database reloaded by {ctx.author.name} in {ctx.guild.name}")
            await ctx.reply(f"Database Reloaded.")
        except Exception as e:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: {ctx.author.name} attempted to reconnect the client and load the db in {ctx.guild.name}\n{e}")
            await ctx.reply(f"The database could NOT be reloaded: {e}")
    else:
        await ctx.reply(PermError)
        return


@bot.command()  # Think This Is Fixed??!???
async def updatedocs(ctx, collection_name, new_field, new_value):
    """Bot Owner Specific
    $updatedocs 'collection_name' 'new_field' 'new_value'"""
    if ctx.author.id != OWNERID:
        await ctx.reply(OwnPermError)
        return
    try:
        if collection_name == "count":
            db_collection = bot.channel_ids.get_collection('count_channel')
        elif collection_name == "economy":
            db_collection = bot.channel_ids.get_collection('economy_data')
        elif collection_name == "sentence":
            db_collection = bot.channel_ids.get_collection('sentence_channel')
        else:
            await ctx.reply(f"{collection_name} isn't valid, try again")
            return
        if new_value.is_digit():
            new_value = int(new_value)
        try:
            db_collection.update_many(
                {},
                {"$set": {new_field: new_value}}
            )
        except Exception as f:
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Updating Docs Errored out: {f}")
            return
        await ctx.reply(f"Documents have been updated")
    except Exception as e:
        await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
        formatted_time = await fortime()
        logger.error(f"{formatted_time}: Updating Docs Errored out: {e}")
        return


async def main():
    try:
        async with bot:
            await bot.start(DISTOKEN)
    except Exception as e:
        formatted_time = await fortime()
        logger.error(f"{formatted_time}: Bot could not be started\n{e}")


if __name__ == "__main__":  # Pretty sure we do this to prevent 'cogs' from running thee bot when referencing code/snippets from thee '__main__' file
    asyncio.run(main())
