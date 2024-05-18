import os
import random
import discord
from pytube import YouTube
from discord.ext import commands
from cogs.mondocs import EconomyData
from pyprobs import Probability as pr
from cogs.economy import add_points, remove_points
from chodebot import perm_check, fortime, logger, guifo, ranff, ErrorMsgOwner, OWNERTAG, PermError, main_path


yt_filepath = f"{main_path}/yt_downloads"


class CustCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ########## LIST OF COMMANDS ##########

    @commands.command()
    async def stuffz(self, ctx, specifics=None):
        """See What You Can Do"""
        channel = self.bot.get_channel(ctx.channel.id)
        embed = discord.Embed(title=f"Stuffz you can do:", description="", color=0x006900)
        if ctx.guild.id == guifo.chodeling_id:
            economy = True
        elif ctx.guild.id == guifo.cemetery_id:
            economy = True
        elif ctx.guild.id == guifo.queenpalace_id:
            economy = True
        else:
            economy = False
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            embed.add_field(name=f"You Can:", value=ranff.noneresponse, inline=False)
            return
        if specifics == "count":
            embed.add_field(name=f"Count Commands:", value=ranff.countresponse, inline=False)
        elif specifics == "economy":
            if economy:
                embed.add_field(name=f"Economy Commands:", value=ranff.economyresponse, inline=False)
            else:
                embed.add_field(name=f"Economy Not enabled in {ctx.guild.name}'s server", value="", inline=False)
        elif specifics == "guess":
            embed.add_field(name=f"Guess Commands:", value=ranff.guessresponse, inline=False)
        elif specifics == "hangman":
            embed.add_field(name=f"Hangman Commands:", value=ranff.hangmanresponse, inline=False)
        elif specifics == "sentence":
            embed.add_field(name=f"Sentence Commands:", value=ranff.sentenceresponse, inline=False)
        elif specifics == "trivia":
            embed.add_field(name=f"Trivia Commands:", value=ranff.triviaresponse, inline=False)
        elif specifics == "warningsystem":
            if ctx.guild.id in (guifo.chodeling_id, guifo.pettysqad_id):
                embed.add_field(name=f"Warning System Commands:", value=ranff.warningsystemresponse, inline=False)
            else:
                embed.add_field(name=f"Warning System Not enabled in {ctx.guild.name}'s server", value="", inline=False)
        if specifics is not None:
            await ctx.channel.send(embed=embed)
            return
        embed.add_field(name=f"Main Stuffz", value=f"{ranff.noneresponse}\n{ranff.normresponse}", inline=False)
        if economy:
            embed.add_field(name=f"Economy Commands:", value=ranff.economyresponse, inline=False)
        embed.add_field(name=f"Count Commands:", value=ranff.countresponse, inline=False)
        embed.add_field(name=f"Guess Commands:", value=ranff.guessresponse, inline=False)
        embed.add_field(name=f"Hangman Commands:", value=ranff.hangmanresponse, inline=False)
        embed.add_field(name=f"Sentence Commands:", value=ranff.sentenceresponse, inline=False)
        embed.add_field(name=f"Trivia Commands:", value=ranff.triviaresponse, inline=False)
        if usersperms == "normal":
            await channel.send(channel, embed=embed)
            return
        embed.add_field(name=f"Mod Commands:", value=ranff.modresponse, inline=False)
        if usersperms == "mod":
            await channel.send(channel, embed=embed)
            return
        embed.add_field(name=f"Admin Commands:", value=ranff.adminresponse, inline=False)
        if usersperms == "admin":
            await channel.send(channel, embed=embed)
            return
        embed.add_field(name=f"Owner Commands:", value=ranff.ownerresponse, inline=False)
        if usersperms == "owner":
            await channel.send(channel, embed=embed)
            return
        if AttributeError:
            await ctx.reply(f"You aren't in a server are ya?")
        else:
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, "Let thee owner know you see this message in relation to thee stuffz command"))

    ########## MOD OR HIGHER ##########

    @commands.command()
    async def clear(self, ctx, limit: int):
        """Batch Delete Messages"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms in ("owner", "admin", "mod"):
            await ctx.channel.purge(limit=limit + 1)
            await ctx.send(f'{limit} messages have been cleared.')
            formatted_time = await fortime()
            logger.info(f"{formatted_time}: {ctx.author.name} cleared {limit} messages from {ctx.channel.name} in {ctx.guild.name}")
        else:
            await ctx.reply(PermError)
            return

    @commands.command()
    async def listchannels(self, ctx):
        """Umm, Maybe One Day"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms in ("owner", "admin", "mod"):
            await ctx.reply(f"I probably won't implement this, I planned to back before I rewrote the backend")
        else:
            return

    @commands.command()
    async def ping(self, ctx):
        """Sanity Check"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms in ("owner", "admin", "mod"):
            await ctx.send(f"Pong ({round(self.bot.latency * 1000)} ms)")
        else:
            await ctx.reply(PermError)
            return

    ########## Normal Commands ##########

    @commands.command(name="8ball")
    async def eight_ball(self, ctx):
        """Shake Thee Bo... 8 Ball"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            return
        if ctx.message.content.endswith("?"):
            await ctx.reply(random.choice(ranff.eightbanswers))
        else:
            await ctx.reply(f"Was that a question????")

    @commands.command()
    async def greet(self, ctx):
        """Hola"""
        wordchoices = ["Hola", "Hello", "Hi", "Whazzup", "Talk to thee hand, err bits"]
        emojichoices = ["👋", "🤪"]
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            response = await ctx.reply(wordchoices[4])
            response.add_reaction(emojichoices[0])
            return
        randomresponse = random.choice(wordchoices)
        response = await ctx.reply(randomresponse)
        if randomresponse == wordchoices[4]:
            choosenemoji = emojichoices[1]
        else:
            choosenemoji = emojichoices[0]
        await response.add_reaction(choosenemoji)

    @commands.command()
    async def hug(self, ctx):
        """I give good virtual hugs"""
        response = await ctx.reply(f"BIIIIGGG CHODEBOT HUGS!!!!!!")
        await response.add_reaction("🫂")
        await response.add_reaction("🤟")

    @commands.command()
    async def ifyouknow(self, ctx):
        """Do you??"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            return
        response = await ctx.reply("You know")
        await response.add_reaction("🧩")

    @commands.command()
    async def pewpew(self, ctx):
        """Pew"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            return
        response = await ctx.reply('Pew Pew, Pew Pew Pew Pew Pew')
        await response.add_reaction("🔫")

    @commands.command()
    async def youtubedownload(self, ctx, url=None, audio_only=None):
        """$youtubedownload url audio_only
        url:: paste whole url, or bits including 'v=characters'
        audio_only:: true/false to get mp3(audio only) or mp4(with video)"""
        try:
            usersperms = await perm_check(ctx, ctx.guild.id)
            if usersperms is None:
                await ctx.reply(PermError)
                return
            if None in (url, audio_only):
                await ctx.reply(f"Command incomplete, try again. Registered as: $youtubedownload {url} {audio_only}")
                return
            audio_only = audio_only.lower()
            youtube_object = YouTube(url)
            if audio_only == "true":
                download = youtube_object.streams.get_audio_only()
            else:
                download = youtube_object.streams.get_lowest_resolution()
            filename = f"{youtube_object.author} - {youtube_object.title}{'.mp3' if audio_only == 'true' else '.mp4'}"
            path_to_file = download.download(output_path=yt_filepath, filename=filename)
            file_to_upload = discord.File(path_to_file, filename=filename)
            await ctx.reply(f"{filename} ready", file=file_to_upload)
            if os.path.exists(path_to_file):
                os.remove(path_to_file)
        except Exception as e:
            await ctx.reply(e)
            print(e)
            return

    ########## Mini-Game Commands ##########

    @commands.command()
    async def bet(self, ctx, target_user, value):
        """Challenge someone else to a bet:
        Challenger: $bet @username amount
        Target: Reply yes or yup or no or nope in same channel
        Times out after 5 mins"""

        async def points_check():
            if challenger_document['points_value'] < int(value):
                await ctx.reply(f"You don't have enough for that, try something smaller")
                return False
            elif target_document['points_value'] < int(value):
                await ctx.reply(f"Your target doesn't have that many points, try something smaller")
                return False
            else:
                return True
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            return
        try:
            # Verify everyone has enough points before going further
            challenger_document = EconomyData.objects.get(author_id=ctx.author.id)
            target_document = EconomyData.objects.get(author_id=int(target_user[2:-1]))
            if await points_check():
                # Create a dictionary to store the users who are involved in the bet and their responses
                bet_participants = {ctx.author.id: "yes", int(target_user[2:-1]): None}
                # Wait for the target user to respond
                while True:
                    response = await self.bot.wait_for("message", check=lambda message: message.author.id in bet_participants and message.content.lower() in ["yup", "yes", "no", "nope"], timeout=300)
                    bet_participants[response.author.id] = response.content.lower()
                    # If the target user has responded, break out of the loop
                    if bet_participants[int(target_user[2:-1])] is not None:
                        break
                # Determine the outcome of the bet based on the response of the target user
                if bet_participants[int(target_user[2:-1])] == "yes" or bet_participants[int(target_user[2:-1])] == "yup":
                    if await points_check():
                        if pr.prob(1/2):
                            await add_points(self, ctx, ctx.author.id, int(value), True)
                            await remove_points(self, ctx, int(target_user[2:-1]), int(value), True)
                            await ctx.reply(f"{ctx.author.name} won {value} from {target_user}.")
                        else:
                            await remove_points(self, ctx, ctx.author.id, int(value), True)
                            await add_points(self, ctx, int(target_user[2:-1]), int(value), True)
                            await ctx.reply(f"{ctx.author.name} lost {value} to {target_user}.")
                else:
                    response = await ctx.reply(f"{target_user} chickened out")
                    await response.add_reaction("😝")
                    return
        except FileNotFoundError:
            await ctx.reply(f"Either you or your target don't have a points sheet yet, try again later")
            return
        except ValueError:
            await ctx.reply(f"Try @Mentioning your target(Only way it works right now(Make sure your target is properly tagged))")
            return
        except TimeoutError:
            await ctx.reply(f"{target_user} didn't respond in time, try again {ctx.author.mention}")
            return
        except Exception as e:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error with the bet system:: {e}")

    @commands.command()
    async def dailychode(self, ctx):
        """Daily points getter thingy"""
        await ctx.reply(f"Nope this isn't making a return anytime soon. FUCK TIME. This is back of thee burner on {OWNERTAG}'s focus levels atm")
        return
        # ToDo: Fix This BulllllllllllllShit
        # usersperms = await perm_check(ctx, ctx.guild.id)
        # if usersperms is None:
        #     return
        #
        # # Create a datetime object for the daily reset time  This is for 6am CST....
        # timezone_reset_time = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp(), tz=datetime.timezone.utc)
        # reset_time = timezone_reset_time.replace(hour=11, minute=0, second=0)
        #
        # try:
        #     document = EconomyData.objects.get(author_id=ctx.author.id)
        #
        #     # Convert the document['last_daily_done'] datetime object to the same timezone as the reset_time datetime object
        #     if document['last_daily_done'] is None:
        #         last_daily_done = None
        #         next_daily_avail = None
        #     else:
        #         last_daily_done = document['last_daily_done'].astimezone(timezone_reset_time.tzinfo)
        #         if document['next_daily_avail'] is None:
        #             next_daily_avail = None
        #         else:
        #             next_daily_avail = document['next_daily_avail'].astimezone(timezone_reset_time.tzinfo)
        #     print(f"{last_daily_done} vs {timezone_reset_time} vs {reset_time} vs {next_daily_avail}")
        #     if last_daily_done is None or last_daily_done <= reset_time:  # <= next_daily_avail:
        #         new_points_value = document['points_value'] + 100
        #         if document['highest_gained_value'] < 100:
        #             document.update(highest_gained_value=100)
        #             document.save()
        #         next_daily_avail = reset_time
        #         document.update(last_daily_done=datetime.datetime.now, next_daily_avail=next_daily_avail, points_value=new_points_value, last_gained_value=100)
        #         document.save()
        #         await ctx.reply(f"You have gained 100 points")
        #     else:
        #         await ctx.reply(f"You've already done your daily, should be reset at 6am CSTish..\nIf it's not let TheeChody know please and ty")
        # except Exception as e:
        #     await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
        #     formatted_time = await fortime()
        #     logger.error(f"{formatted_time}: Daily errored out: {e}")

    @commands.command()
    async def gamble(self, ctx, value):
        """Odds ain't in your favor, but * 10000 your bet if you win"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            return
        if not value.isdigit():
            await ctx.reply(f"Gotta use numbers bud, not {type(value)}")
            return
        try:
            document = EconomyData.objects.get(author_id=ctx.author.id)
            if document['points_value'] < int(value):
                await ctx.reply(f"You don't have enuff for that bud! Nice try :P")
                return
            if pr.prob(97.5/100):
                await remove_points(self, ctx, ctx.author.id, int(value), True)
                await ctx.reply(f"I ate your points, they tasted yummy!!")
                return
            else:
                won_amount = int(value) * 10000
                new_points_value = document['points_value'] + won_amount
                await add_points(self, ctx, ctx.author.id, int(won_amount), True)
                await ctx.reply(f"You just won {won_amount}!! Your new total is {new_points_value}")
        except Exception as e:
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Daily errored out: {e}")

    # ToDo Add fun minigames with commands like twitch games
    # ToDo tag, prank, fight, pants, poke, etc

    ########## End of Commands ##########


async def setup(bot):
    await bot.add_cog(CustCommands(bot))
