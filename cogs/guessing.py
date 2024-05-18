import random
# import asyncio
import discord
from discord.ext import commands
# from cogs.economy import add_points  #, remove_points
from cogs.mondocs import GuessChannel  #,GuessPrivate
from chodebot import logger, fortime, perm_check, ranword_comparasion, guifo, PermError, ErrorMsgOwner, OWNERTAG, ignore_keys  #,number_emojis


class GuessingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def reset_game(message, document):
        if document['gametype'] == 'randomnumber':
            numlowvalue = 0
            numhighvalue = 99999
            answer = random.randint(numlowvalue, numhighvalue)
            maxguessesmade = 20
            allowedmultguesses = True
            response = f"Guessing game started. Random number between {numlowvalue} and {numhighvalue:,}. Y'all got {maxguessesmade} guesses. Good luck!\nTrying something new, hint every guess"
            document.update(guessesmade=0, previous_author="", lastguessed=0, guessesbetweenhints=0, answer=answer,
                            maxguessesmade=maxguessesmade, lowestguess=0, highestguess=0, maxguessesbetweenhints=0,
                            total_authors="", allowedmultguesses=allowedmultguesses)
            document.save()
        elif document['gametype'] == 'randomword':
            with open("refs/english", "r") as file:
                wordlist = file.read()
                wordsplit = list(map(str, wordlist.splitlines()))
            answer = random.choice(wordsplit)
            maxguessesmade = len(answer) * 10
            allowedmultguesses = True
            response = f"Guessing game started. Random word list up to {len(wordsplit):,} loaded. One chosen at random. Good Luck!"
            document.update(guessesmade=0, previous_author="", lastguessed="", answer=answer,
                            maxguessesmade=maxguessesmade, total_authors="", allowedmultguesses=allowedmultguesses)
            document.save()
        else:
            await message.channel.send(ErrorMsgOwner.format(OWNERTAG, f"Something went wrong restarting {document['gametype']} in {message.channel.name} within {message.guild.name}"))
            return
        await message.channel.send(response)

    @commands.Cog.listener()
    async def on_message(self, message):  # ToDo Add Counting Down Warning Thing after 5, 3 last guess
        async def numbercheck(message):
            try:
                if len(message.split(" ")) > 1:
                    message = message.split(" ")[0]
                if message.isdigit():
                    return int(message)
                elif not message.isdigit():
                    return "not"
                else:
                    return "soft_error"
            except Exception as e:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Something went wrong, numbercheck -- {e}")
                    return "error"

        async def wordcheck(message):
            try:
                # Check if the message contains multiple words
                if len(message.split(" ")) > 1:
                    message = message.split(" ")[0]
                if message.isdigit():
                    return "not"
                elif not message.isdigit():
                    return message.lower()
                else:
                    return "soft_error"
            except Exception as e:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something went wrong, wordcheck -- {e}")
                return "error"

        channelid = message.channel.id
        try:
            document = GuessChannel.objects.get(channel_id=channelid)
        except Exception as m:
            if FileNotFoundError:
                return
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error loading hangman document for {channelid} -- {m}")
                return
        if message.author.bot:
            return
        if message.content.startswith(ignore_keys, 0, 2):
            return
        usersperms = await perm_check(message, message.guild.id)
        if usersperms is None:
            await message.reply(PermError)
            return
        died = False
        print(f"guesslistener -- {message.author.name} -- {message.channel.id} --")
        if message.author.name == document['previous_author'] and not document['allowedmultguesses']:
            prevauthor = message.author
            await message.delete()
            if message.guild.id in (guifo.chodeling_id, guifo.cemetery_id, guifo.queenpalace_id):
                await message.channel.send(f"{prevauthor.mention} 1 point deducted from the grand total for guessing twice in a row. :P", silent=True, delete_after=10)
                new_grandtotal = document['grandtotal'] - 1
                document.update(grandtotal=new_grandtotal)
                document.save()
            else:
                await message.channel.send(f"{prevauthor.mention} you cannot guess twice in a row.", silent=True, delete_after=10)
            return
        if document['gametype'] in ("randomnumber", "randomnumber_test_values1", "randomnumber_test_values2"):
            guess = await numbercheck(message.content)
            if type(guess) != int:
                pass
            else:
                if guess > document['highestguess'] or guess < document['lowestguess']:
                    prev_author = message.author
                    if guess > document['highestguess'] > 0:
                        response = f"{prev_author.mention} {guess} is higher than thee last logical guess ({document['highestguess']})"
                    elif guess < document['lowestguess'] > 0:
                        response = f"{prev_author.mention} {guess} is lower than thee last logical guess ({document['lowestguess']})"
                    else:
                        response = None
                        # if response is None:
                        # if document['highestguess'] == 0:
                        if guess < document['answer']:
                            document.update(lowestguess=guess)
                            document.save()
                        elif guess > document['answer']:
                            document.update(highestguess=guess)
                            document.save()
                    # else:
                    if response is not None:
                        await message.delete()
                        await message.channel.send(f"{response}\nBetween {document['lowestguess']} and {document['highestguess']}", silent=True, delete_after=10)
                        return
                else:
                    if guess > document['lowestguess'] > document['highestguess']:
                        document.update(lowestguess=guess)
                        document.save()
                    elif guess < document['highestguess'] < document['lowestguess']:
                        document.update(highestguess=guess)
                        document.save()
        elif document['gametype'] == "randomword":
            guess = await wordcheck(message.content)
        else:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Something wen't wrong detecting gametype for {message.channel.name}'s private game. {message.channel.id}")
            await message.channel.send(ErrorMsgOwner.format(OWNERTAG, "Something wen't wrong, y'all should never see this."))
            return
        if guess == "not":
            # await message.add_reaction("❌")
            return
        elif guess == "error":
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Something wen't wrong detecting gametype for {message.channel.name}'s private game. {message.channel.id}")
            await message.channel.send(ErrorMsgOwner.format(OWNERTAG, "Something wen't wrong, y'all should never see this"))
            return
        elif guess == "soft_error":
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Something wen't wrong or maybe didn't? Look closer, something ain't acting right. {message.channel.name} -- {message.channel.id}")
            await message.channe.send(ErrorMsgOwner.format(OWNERTAG, "Something wen't wrong or maybe didn't? Look closer, something ain't acting right"))
            return
        elif guess is None:
            return
        new_guessesmade = document['guessesmade'] + 1
        if guess == document['answer']:
            await message.add_reaction("🌟")
            await message.channel.send(f"You answered correctly!!!! Wow that is amazing! Only took {new_guessesmade} guesses.")
            if message.guild.id == guifo.chodeling_id:
                await message.channel.send(f"This will be fixed eventually, for now y'all just won. Relish in that you won :P")
                # try:  # ToDo: Fix This
                #     if message.author.id in document['total_authors'].split(""):
                #         pass
                #     else:
                #         total_authors_updated = document['total_authors'] + message.author.id
                #         document.update(total_authors=total_authors_updated)
                #         document.save()
                #     document = GuessChannel.objects.get(channel_id=channelid)
                #     author_ids_share = document['total_authors']
                #     author_names = ""
                #     users_to_split = len(author_ids_share.split("")) / document['grandtotal']
                #     for authid in author_ids_share.split(""):
                #         try:
                #             await add_points(self, message, authid, users_to_split, False)
                #             username = self.bot.get_user(authid)
                #             author_names += f"{username}\n"
                #         except FileNotFoundError:
                #             pass
                #     channel = self.bot.get_channel(channelid)
                #     embed = discord.Embed(title=f"List of whom are sharing 1000 points", description=f"Each user got {users_to_split}", color=0x0F0F0F)
                #     embed.add_field(name=author_names, value=f"If you played but don't see your name, you don't have a points sheet. Look into it for next time :P")
                #     await channel.send(channel, embed=embed)
                # except Exception as e:
                #     if FileNotFoundError:
                #         pass
                #     else:
                #         await message.channel.send(f"Something wen't wrong adding points, pass this error message if any to TheeChody Please. {e}")
                #         formatted_time = await fortime()
                #         logger.error(f"{formatted_time}: Something wen't wrong adding points, dm channel.. {message.author.name}\n{e}")
            # else:
            #     await message.channel.send(f"Thee chodepoints system is disabled on this server, otherwise y'all would've had {document['grandtotal']} to split", delete_after=15)
            await self.reset_game(message, document)
            return
        elif guess != document['answer'] and guess is not None:
            new_guessesbetweenhints = 0
            channel = self.bot.get_channel(channelid)
            guesses_left = abs(new_guessesmade - document['maxguessesmade'])
            if document['gametype'] == "randomword":
                await message.add_reaction("☠️")
                try:
                    correct_position, correct_letter, wrong_letter = await ranword_comparasion(guess, document)
                except Exception as e:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Something went wrong in randomword guess != document['answer'] after ranword_comp :: {e}")
                    return
                if correct_position is None:
                    embed = discord.Embed(title="Something went wrong in generating thee Hint", description=ErrorMsgOwner.format(OWNERTAG, wrong_letter))
                    await message.reply(channel, embed=embed)
                    return
                if guesses_left <= 25:
                    response = f"\nThere are {guesses_left} guesses left"
                else:
                    response = ""
                embed = discord.Embed(title="Hint:", description="", color=0x006900)
                embed.add_field(name=f"{correct_position} in thee right spot\n{correct_letter} correct but in thee wrong spot\n{wrong_letter} are not in the answer", value=f"There may/may not be multiple same letters in thee answer that may/may not be accounted for here{response}", inline=False)
                await message.reply(channel, embed=embed)
            elif document['gametype'] in ("randomnumber", "randomnumber_test_values1", "randomnumber_test_values2"):
                await message.add_reaction("❎")
                if document['guessesbetweenhints'] >= document['maxguessesbetweenhints']:  # or document['guessesmade'] == 0:
                    embed = discord.Embed(title="Hint:", description="", color=0x006900)
                    if guess < document['answer']:
                        document.update(lowestguess=guess)
                        document.save()
                        embed.add_field(name=f"{guess:,} is lower than thee answer", value=f"{guesses_left} guesses left", inline=False)
                    elif guess > document['answer']:
                        document.update(highestguess=guess)
                        document.save()
                        embed.add_field(name=f"{guess:,} is higher than thee answer", value=f"{guesses_left} guesses left", inline=False)
                    document = GuessChannel.objects.get(channel_id=channelid)
                    if (document['lowestguess'] or document['highestguess']) == 0:
                        if document['lowestguess'] == 0:
                            lowest_guess = 'UnKnown'
                        else:
                            lowest_guess = document['lowestguess']
                        if document['highestguess'] == 0:
                            highest_guess = 'UnKnown'
                        else:
                            highest_guess = document['highestguess']
                    else:
                        lowest_guess = document['lowestguess']
                        highest_guess = document['highestguess']
                    embed.add_field(name="Lowest/Highest Known Guesses:", value=f"{lowest_guess:,}/{highest_guess:,}")
                    await message.reply(channel, embed=embed)
                else:
                    new_guessesbetweenhints = document['guessesbetweenhints'] + 1
            document.update(guessesmade=new_guessesmade, previous_author=message.author.name, lastguessed=guess, guessesbetweenhints=new_guessesbetweenhints)
            document.save()
            if new_guessesmade >= document['maxguessesmade']:
                died = True
            else:
                # if document['gametype'] in ("randomnumber", "randomnumber_test_values1", "randomnumber_test_values2"):
                #     if document['guessesmade'] == 6:
                #         document.update(maxguessesbetweenhints=1)
                #         document.save()
                #     elif document['guessesmade'] == 13:
                #         # print(f"Before update in 13")
                #         document.update(maxguessesbetweenhints=2)
                #         document.save()
                #         # print(f"After update in 13")
                #     elif document['guessesmade'] == 20:
                #         document.update(maxguessesbetweenhints=3)
                #         document.save()
                #     elif document['guessesmade'] == 27:
                #         document.update(maxguessesbetweenhints=4)
                #         document.save()
                if message.guild.id in (guifo.chodeling_id, guifo.cemetery_id, guifo.queenpalace_id):
                    economy_data_collection = self.bot.channel_ids.get_collection('economy_data')
                    if economy_data_collection.find_one({"_id": message.author.id}):
                        total_authors = document['total_authors']
                        if str(message.author.id) in total_authors.split("|"):
                            pass
                        else:
                            if total_authors == "":
                                total_authors_updated = f"{message.author.id}"
                            else:
                                total_authors_updated = f"{total_authors}|{message.author.id}"
                            document.update(total_authors=total_authors_updated)
                            document.save()
        if died:
            await message.channel.send(f"Well better luck next time y'all, ran outta guesses.\nThee Answer was: {document['answer']}")
            await self.reset_game(message, document)
            return

    @commands.command()
    async def guess(self, ctx, operator):
        """$guess operator
        :Operators:
        gametype
        guessesmade
        lastguessed
        whoguessedlast"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            await ctx.reply(PermError)
            return
        channelid = ctx.channel.id
        document = GuessChannel.objects.get(channel_id=channelid)
        if operator.lower() == "gametype":
            await ctx.reply(f"Thee gametype being played right now is: {document['gametype']}")
            return
        elif operator.lower() == "guessesmade":
            await ctx.reply(f"Thee current number of guesses made is: {document['guessesmade']}")
            return
        elif operator.lower() == "lastguessed":
            await ctx.reply(f"Thee last valid guess was {document['lastguessed']}")
            return
        elif operator.lower() == "whoguessedlast":
            await ctx.reply(f"{document['previous_author']} was thee last one to put in a valid guess")
            return
        else:
            await ctx.reply(f"Thee operator '{operator}' is not valid, please try again")
            return

    @commands.command()
    async def guessconfig(self, ctx, setting, value):
        """$guessconfig setting value
        :Settings:
        multguess
        :Values:
        true
        false"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin", "mod"):
            await ctx.reply(PermError)
            return
        channelid = ctx.channel.id
        document = GuessChannel.objects.get(channel_id=channelid)
        if setting.lower() == "multguess":
            if value.lower() == "true" and document['allowedmultguesses']:
                await ctx.reply(f"Mult-Guesses already enabled")
                return
            elif value.lower() == "false" and not document['allowedmultguesses']:
                await ctx.reply(f"Mult-Guesses already disabled")
                return
            if value.lower() == "true" and not document['allowedmultguesses']:
                new_mult_guess = True
            elif value.lower() == "false" and document['allowedmultguesses']:
                new_mult_guess = False
            else:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f"Something went wrong, either '{setting}' or '{value}' was registered wrong. Inside GuessConfig"))
                return
            document.update(allowedmultguesses=new_mult_guess)
            document.save()
            await ctx.reply(f"The new value has been set to: {new_mult_guess}")
            return
        else:
            await ctx.reply(f"'{setting}' is not a valid choice, please try again")
            return

    @commands.command()
    async def guess_start(self, ctx, gametype, gamemode="channel"):
        """Stress Testing Mode. Go Ham Peeps
        Starts the guessing game, takes two arguments: "gametype" & "gamemode".
        GameTypes:
        randomnumber
        randomword
        GameModes: (If left empty, defaults to channel)
        channel
        private (Currently Disabled)"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            await ctx.reply(PermError)
            return
        channelid = ctx.channel.id
        guess_channel_collection = self.bot.channel_ids.get_collection('guess_channel')
        if guess_channel_collection.find_one({"_id": channelid}):
            await ctx.reply(f"There is already a game going")
            return
        if gametype in "randomnumber":
            numlowvalue = 0
            numhighvalue = 99999
            answer = random.randint(numlowvalue, numhighvalue)
            maxguessesmade = 30
            allowedmultguesses = True
            response = f"Guessing game started. Random number between {numlowvalue} and {numhighvalue:,}. Y'all got {maxguessesmade} guesses. Good luck!"
        elif gametype == "randomword":
            with open("refs/english", "r") as file:
                wordlist = file.read()
                wordsplit = list(map(str, wordlist.splitlines()))
            answer = random.choice(wordsplit)
            maxguessesmade = len(answer) * 10
            allowedmultguesses = True
            response = f"Guessing game started. Random word list up to {len(wordsplit):,} loaded with one chosen at random. Good Luck!"
        else:
            await ctx.reply(f"Gametype ({gametype}) wasn't valid, try again")
            return
        if gamemode == "channel":
            try:
                new_document = GuessChannel(channel_id=channelid, channel_name=ctx.channel.name,
                                            guild_name=ctx.guild.name,
                                            gametype=gametype, answer=answer, maxguessesmade=maxguessesmade,
                                            allowedmultguesses=allowedmultguesses)
                new_document_dict = new_document.to_mongo()
                guess_channel_collection.insert_one(new_document_dict)
                await ctx.channel.send(response)
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something went wrong here.. {e}")
                return
        elif gamemode == "private":
            await ctx.reply(f"Thee Private Version is disabled, may not return..")
            return
        else:
            await ctx.reply(f"GameMode ({gamemode}) Wasn't detected properly, try again")
            return


async def setup(bot):
    await bot.add_cog(GuessingCog(bot))
