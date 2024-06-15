from discord.ext import commands
from mongoengine import Document, DateTimeField, BooleanField, DynamicField, IntField, StringField, ListField, FloatField


class ChannelInfo(Document):
    guild_id = IntField(primary_key=True)
    guild_name = DynamicField(default="")
    guild_owner_id = IntField(default=0)
    guild_owner_name = DynamicField(default="")
    guild_owner_nick_name = DynamicField(default="")

    mod_role_id = IntField(default=0)
    norm_role_id = IntField(default=0)

    channel_id_logs = IntField(default=0)
    channel_id_count = IntField(default=0)
    channel_id_cya = IntField(default=0)
    channel_id_gen_dir = IntField(default=0)
    channel_id_guess_num = IntField(default=0)
    channel_id_guess_word = IntField(default=0)
    channel_id_hangman = IntField(default=0)
    channel_id_sentence = IntField(default=0)
    channel_id_trivia = IntField(default=0)
    channel_id_ignore = ListField(default=[])

    welcome_message = DynamicField(default="")


class CountChannel(Document):
    channel_id = IntField(primary_key=True)
    channel_name = DynamicField(default="")
    guild_id = IntField(default=0)
    guild_name = DynamicField(default="")
    previous_author = DynamicField(default="")
    goal_number = IntField(default=1)
    highscore = IntField(default=0)
    step = IntField(default=1)
    infraction_count = IntField(default=0)
    warninglevel = IntField(default=0)
    warningmax = IntField(default=1)
    allowedwarning = BooleanField(default=True)
    streakrankability = BooleanField(default=True)
    roundallguesses = BooleanField(default=True)
    allowedmultguesses = BooleanField(default=False)
    expressionenabled = BooleanField(default=True)
    enablewolframalpha = BooleanField(default=True)
    pro_channel = BooleanField(default=False)
    pro_users = ListField(default=[])


class CountUser(Document):
    document_id = IntField(primary_key=True)
    user_id = IntField(default=0)
    user_name = DynamicField(default="")
    user_nick_name = DynamicField(default="")
    guild_name = DynamicField(default="")
    channel_id = IntField(default=0)
    channel_name = DynamicField(default="")
    times_counted = IntField(default=0)
    times_failed = IntField(default=0)
    times_warned = IntField(default=0)
    total_counted = IntField(default=0)
    count_highest = IntField(default=0)


"""Thinking split up quests into missions, using cave one as
example, intro would be thee cabb scene, mission 1 text
would consist of thee last bit of cabb scene and mission 1
type would be roll dice to move type, fighting enemies on
thee way, with thee option for thee specials to align with
mission number, eg: special 1 is only available in mission 1
special 2 only available in mission 2 etc. this would allow
for multiple quests to be made up and allow a more flexible
system that previously was going to do. special 1 would be
trader joe. once reached thee end of thee dice rolls to move
mission 2 starts at thee lab maze, with special 2 being thee
option to investigate thee 'chest' and fight thee mimic.
mission 3 would be fighting thee nothic thing, no special
and mission 4 would be returning to thee cabb, special 4
would be thee trader joe, if not visited during special 1.
once reached cabb, finale bit starts, rewards are given out, 
and transition to 'in between journeys' mode, with the option 
to sell, fix armor/weapons, buy potions weapons armor etc 
stuff, or 'rest and recover health' making player unable to 
play for x amount of time. rewards would likely be gold, xp,
bot points, etc. potential for using bot points for extras"""


class CyaAdventure(Document):
    adventure_id = IntField(primary_key=True)
    adventure_name = DynamicField(default="")
    adventure_type = DynamicField(default="")
    adventure_rewards = DynamicField(default=None)
    adventure_intro_text = DynamicField(default=None)
    adventure_finale_text = DynamicField(default=None)
    adventure_mission1_type = DynamicField(default="")
    adventure_mission2_type = DynamicField(default="")
    adventure_mission3_type = DynamicField(default="")
    adventure_mission4_type = DynamicField(default="")
    adventure_mission1_text = DynamicField(default=None)
    adventure_mission2_text = DynamicField(default=None)
    adventure_mission3_text = DynamicField(default=None)
    adventure_mission4_text = DynamicField(default=None)
    adventure_special1_type = DynamicField(default="")
    adventure_special2_type = DynamicField(default="")
    adventure_special3_type = DynamicField(default="")
    adventure_special4_type = DynamicField(default="")
    adventure_special1_text = DynamicField(default=None)
    adventure_special2_text = DynamicField(default=None)
    adventure_special3_text = DynamicField(default=None)
    adventure_special4_text = DynamicField(default=None)


class CyaMob(Document):
    mob_id = IntField(primary_key=True)
    mob_name = DynamicField(default="")
    mob_class = DynamicField(default="")
    mob_level = IntField(default=0)
    mob_hp = IntField(default=0)
    mob_ac = IntField(default=0)
    mob_spc_alive = BooleanField(default=True)
    inv_drop = IntField(default=20)


class CyaPlayer(Document):
    user_id = IntField(primary_key=True)
    user_name = DynamicField(default="")
    channel_playing_id = IntField(default=0)
    player_state = DynamicField(default="First_Journey")
    player_adventure = IntField(default=0)
    player_god = BooleanField(default=False)
    player_name = DynamicField(default="")
    player_class = DynamicField(default="")
    player_level = IntField(default=0)
    player_hp = IntField(default=0)
    player_max_hp = IntField(default=25)
    player_ac = IntField(default=0)
    inv_money = IntField(default=100)
    inv_pot_reg = IntField(default=1)
    inv_pot_spc = IntField(default=0)
    inv_upgrade_att = IntField(default=0)
    inv_upgrade_def = IntField(default=0)
    inv_key = BooleanField(default=False)
    trader_visited = BooleanField(default=False)


class CyaPlayerAdventure(Document):
    adventure_player_id = IntField(primary_key=True)
    user_name = DynamicField(default="")
    adventure_id = IntField(default=0000)
    adventure_player_state = DynamicField(default="")
    adventure_player_intro = DynamicField(default=None)
    adventure_player_finale = DynamicField(default=None)
    adventure_player_mission1 = DynamicField(default=None)
    adventure_player_mission2 = DynamicField(default=None)
    adventure_player_mission3 = DynamicField(default=None)
    adventure_player_mission4 = DynamicField(default=None)
    adventure_player_special1 = DynamicField(default=None)
    adventure_player_special2 = DynamicField(default=None)
    adventure_player_special3 = DynamicField(default=None)
    adventure_player_special4 = DynamicField(default=None)


class DirectoryChannel(Document):
    document_id = IntField(primary_key=True)
    channel_id = IntField(default=0)
    guild_id = IntField(default=0)
    guild_name = DynamicField(default="")
    channel_name = DynamicField(default="")
    directory_type = DynamicField(default="")
    directory_page = IntField(default=1)
    directory_index = IntField(default=0)
    message_id = IntField(default=0)
    prev_author_name = DynamicField(default="")
    prev_author_nick_name = DynamicField(default="")
    last_updated = DynamicField(default="")
    thread_name = ListField(default=[])
    thread_link = ListField(default=[])


class DirectoryUpdate(Document):
    message_id = IntField(primary_key=True)
    channel_id = IntField(default=0)
    guild_id = IntField(default=0)
    guild_name = DynamicField(default="")
    channel_name = DynamicField(default="")
    directory_type = DynamicField(default="")
    thread_name = DynamicField(default="")
    thread_link = DynamicField(default="")
    author_name = DynamicField(default="")
    author_nick_name = DynamicField(default="")
    date_updated = DynamicField(default="")


class EconomyData(Document):
    author_id = IntField(primary_key=True)
    author_name = DynamicField(default="")
    guild_name = DynamicField(default="")
    last_daily_done = DateTimeField(default=None)
    next_daily_avail = DateTimeField(default=None)
    points_value = DynamicField(default=0)
    last_gained_value = DynamicField(default=0)
    last_lost_value = DynamicField(default=0)
    highest_gained_value = DynamicField(default=0)
    highest_lost_value = DynamicField(default=0)
    highest_gambling_won = DynamicField(default=0)
    highest_gambling_lost = DynamicField(default=0)
    total_gambling_won = DynamicField(default=0)
    total_gambling_lost = DynamicField(default=0)
    twitch_id = IntField(default=0)


class GuessChannel(Document):
    channel_id = IntField(primary_key=True)
    channel_name = DynamicField(default="")
    guild_name = DynamicField(default="")
    previous_author = DynamicField(default="")
    total_authors = DynamicField(default="")
    gametype = DynamicField(default="none")
    answer = DynamicField(default="")
    public = BooleanField(default=True)
    allowedmultguesses = BooleanField(default=False)
    lowestguess = DynamicField(default=0)
    highestguess = DynamicField(default=0)
    guessesmade = DynamicField(default=0)
    lastguessed = DynamicField(default=0)
    maxguessesmade = DynamicField(default=0)
    guessesbetweenhints = DynamicField(default=0)
    maxguessesbetweenhints = DynamicField(default=0)
    grandtotal = DynamicField(default=1000)


class GuessPrivate(Document):
    user_id = IntField(primary_key=True)
    channel_name = DynamicField(default="")
    guild_name = DynamicField(default="")
    gametype = DynamicField(default="none")
    answer = DynamicField(default="")
    guessesmade = DynamicField(default=0)
    guessestotal = DynamicField(default=0)
    guessesbetweenhints = DynamicField(default=0)
    public = BooleanField(default=False)


class HangmanChannel(Document):
    channel_id = IntField(primary_key=True)
    channel_name = DynamicField(default="")
    guild_id = IntField(default=0)
    guild_name = DynamicField(default="")
    times_won = IntField(default=0)
    times_lost = IntField(default=0)
    answer = DynamicField(default="")
    partial_answer = DynamicField(default="")
    guessed_letters = DynamicField(default="")
    guesses_made = IntField(default=0)
    max_guesses = IntField(default=8)
    word_guesses_made = IntField(default=0)
    max_wordguesses = IntField(default=1)
    prev_author = DynamicField(default="")
    allowedmultguesses = BooleanField(default=True)


class HangmanUser(Document):
    document_id = IntField(primary_key=True)
    user_id = IntField(default=0)
    user_name = DynamicField(default="")
    user_nick_name = DynamicField(default="")
    guild_id = IntField(default=0)
    guild_name = DynamicField(default="")
    channel_id = IntField(default=0)
    channel_name = DynamicField(default="")
    total_guesses = IntField(default=0)
    right_guesses = IntField(default=0)
    wrong_guesses = IntField(default=0)


class MissOCollection(Document):
    channel_id = IntField(primary_key=True)
    channel_name = DynamicField(default="")
    guild_name = DynamicField(default="")
    previous_author = DynamicField(default="")
    question = DynamicField(default="")
    allowedmultguesses = BooleanField(default=False)


class MissOHistory(Document):
    message_id = IntField(primary_key=True)
    channel_name = DynamicField(default="")
    guild_name = DynamicField(default="")
    question = DynamicField(default="")
    answer = DynamicField(default="")
    correct_author = DynamicField(default="")


class MsgToKeepTrackOf(Document):
    message_id = IntField(primary_key=True)
    channel_name = DynamicField(default="")
    channel_id = IntField(default=0)
    guild_name = DynamicField(default="")
    message_event = DynamicField(default="")
    message_channels = DynamicField(default="")
    time_down = IntField(default=0)


class ReactionMessages(Document):
    message_id = IntField(primary_key=True)
    thread_id = IntField(default=0)
    thread_name = DynamicField(default="")
    guild_name = DynamicField(default="")
    author_id = IntField(default=0)
    author_name = DynamicField(default="")
    author_display_name = DynamicField(default="")
    message_content = DynamicField(default="")
    reaction_type = DynamicField(default="")
    yes_emoji = DynamicField(default="👍")
    no_emoji = DynamicField(default="👎")


class ReactionRoles(Document):
    message_id = IntField(primary_key=True)
    channel_name = DynamicField(default="")
    guild_name = DynamicField(default="")
    reaction_type = DynamicField(default="")
    reaction_emojis = StringField(default="")


class SentenceChannel(Document):
    channel_id = IntField(primary_key=True)
    channel_name = DynamicField(default="")
    guild_name = DynamicField(default="")
    previous_author = DynamicField(default="")
    word_count = DynamicField(default=0)
    sentence = StringField(default="")
    allowedmultinputs = BooleanField(default=False)
    allowedtoend = BooleanField(default=False)


class TempChannels(Document):
    channel_id = IntField(primary_key=True)
    guild_name = DynamicField(default="")
    author_name = DynamicField(default="")
    author_id = IntField(default=0)


class TriviaQuestions(Document):
    channel_id = IntField(primary_key=True)
    channel_name = DynamicField(default="")
    guild_name = DynamicField(default="")
    previous_author = DynamicField(default="")
    category = DynamicField(default="")
    sub_category = DynamicField(default="")
    topic = DynamicField(default="")
    sub_topic = DynamicField(default="")
    question = DynamicField(default="")
    answer = DynamicField(default="")
    lastguessed = DynamicField(default="")
    lasttoskip = DynamicField(default="")
    allowedmultguesses = BooleanField(default=True)
    guessesmade = DynamicField(default=0)
    guessedlist = DynamicField(default="")
    guessedlist_nice = DynamicField(default="")
    maxguessesmade = DynamicField(default=10)
    grandtotal = DynamicField(default=666)
    gameswon = DynamicField(default=0)
    gameslost = DynamicField(default=0)


class Users(Document):
    user_id = IntField(primary_key=True)
    user_discord_id = IntField(default=0)
    user_name = DynamicField(default="")
    user_login = DynamicField(default="")
    user_level = IntField(default=1)
    user_xp_points = FloatField(default=0)
    user_points = IntField(default=0)
    user_pp = ListField(default=[None, None, ""])
    first_chat_date = DateTimeField(default=None)
    latest_chat_date = DateTimeField(default=None)
    meta = {"db_alias": "Twitch_Database"}


class WarningsLoggerChannel(Document):
    message_id = IntField(primary_key=True)
    guild_name = DynamicField(default="")
    guild_id = IntField(default=0)
    channel_name = DynamicField(default="")
    channel_id = IntField(default=0)
    mod_author = DynamicField(default="")
    last_updated = DynamicField(default="")
    users_written_up = IntField(default=0)
    page = IntField(default=1)
    index = IntField(default=0)


class WarningsLoggerIndividual(Document):
    document_id = IntField(primary_key=True)
    guild_name = DynamicField(default="")
    guild_id = IntField(default=0)
    channel_id = IntField(default=0)
    message_id = IntField(default=0)
    author_id = IntField(default=0)
    author_name = DynamicField(default="")
    author_nick_name = DynamicField(default="")
    warning_level = IntField(default=0)
    action_level = IntField(default=0)
    date_last_offense = DynamicField(default="")
    dates_written_up = DynamicField(default="")


class WarningsLoggerMessage(Document):
    message_id = IntField(primary_key=True)
    message_date_time = DynamicField(default="")
    guild_name = DynamicField(default="")
    guild_id = IntField(default=0)
    channel_name = DynamicField(default="")
    channel_id = IntField(default=0)
    mod_author = DynamicField(default="")
    offender_id = IntField(default=0)
    offender_name = DynamicField(default="")
    offender_nick_name = DynamicField(default="")
    message_content = DynamicField(default="")
    raw_message_content = DynamicField(default="")


class MonDocs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(MonDocs(bot))
