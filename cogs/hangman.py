import discord
import random
from discord.ext import commands
from cogs.mondocs import HangmanChannel, HangmanUser
from cogs.economy import add_points, remove_points
from chodebot import ignore_keys, logger, perm_check, fortime, PermError, ErrorMsgOwner, OWNERTAG


class HangmanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def reset_game(self, message, status="restart"):
        channelid = message.channel.id
        with open("refs/english", "r") as file:
            wordlist = file.read()
            wordsplit = list(map(str, wordlist.splitlines()))
        while True:
            answer = random.choice(wordsplit)
            if len(answer) >= 5:
                partial_answer = "-" * len(answer)
                partial_answer = list(partial_answer)
                break
        if status == "restart":
            document = HangmanChannel.objects.get(channel_id=channelid)
            document.update(answer=answer, partial_answer=partial_answer, guessed_letters="", guesses_made=0, word_guesses_made=0, prev_author="")
            document.save()
        elif status == "start":
            hangman_channel_collection = self.bot.channel_ids.get_collection('hangman_channel')
            new_document = HangmanChannel(channel_id=channelid, channel_name=message.channel.name, guild_id=message.guild.id,
                                          guild_name=message.guild.name, answer=answer, partial_answer=partial_answer)
            new_document_dict = new_document.to_mongo()
            hangman_channel_collection.insert_one(new_document_dict)
        else:
            await message.channel.send(f"{OWNERTAG} is silly, and messed up internal code!!! {status} ISN't VALID!!!!")
            return
        document = HangmanChannel.objects.get(channel_id=channelid)
        await self.get_post(message, document, "new_game")
        return

    @staticmethod
    async def update_user_stats(message, user_document, add_total, add_right, add_wrong):
        try:
            if user_document is None:
                pass
            else:
                new_total_guesses = user_document['total_guesses'] + add_total
                new_right_guesses = user_document['right_guesses'] + add_right
                new_wrong_guesses = user_document['wrong_guesses'] + add_wrong
                user_document.update(user_nick_name=message.author.display_name, total_guesses=new_total_guesses, right_guesses=new_right_guesses,
                                     wrong_guesses=new_wrong_guesses, guild_name=message.guild.name, channel_name=message.channel.name)
                user_document.save()
        except Exception as e:
            await message.channel.send(f"Error updating your user stats, I'll let {OWNERTAG} know. You can keep playing", delete_after=20)
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error updating {message.author.id}'s user stats in {message.channel.id, message.guild.id} -- {e}")
            pass

    @staticmethod
    async def get_post(message, document, status="mid_game"):
        stages = [
            # 0
            """
               --------
               |      
               |      
               |    
               |     
               | 
               | 
               |    
               ----
            """,
            # 1
            """
               --------
               |.......|
               |      
               |
               |    
               |      
               |  
               |   
               ----
            """,
            # 2
            """
               --------
               |.......|
               |......O
               |
               |    
               |      
               | 
               |    
               ----
            """,
            # 3
            """
               --------
               |.......|
               |......O
               |.......|
               |
               |
               |  
               |   
               ----
            """,
            # 4
            """
               --------
               |.......|
               |......O
               |.......|
               |.......|
               |
               |   
               |  
               ----
            """,
            # 5
            """
               --------
               |.......|
               |......O
               |...../|
               |.......|
               |
               | 
               |    
               ----
            """,
            # 6
            """
               --------
               |.......|
               |......O
               |...../|/
               |.......|
               |
               |   
               |   
               ----
            """,
            # 7
            """
               --------
               |.......|
               |......O
               |...../|/
               |.......|
               |....../ 
               |
               |
               ----
            """,
            # 8
            """
               --------
               |.......|
               |.......|
               |......O
               |...../|/
               |.......|
               |....../L
               |
               ----
            """
        ]
        end_response = None
        if status == "mid_game":
            status_response = 'Next Update'
            cust_send = message.reply
        elif status == "new_game":
            status_response = 'New Game Started'
            cust_send = message.channel.send
        elif status == "end_game":
            new_times_lost = document['times_lost'] + 1
            document.update(times_lost=new_times_lost)
            document.save()
            document = HangmanChannel.objects.get(channel_id=message.channel.id)
            status_response = 'Stick Person Hung'
            cust_send = message.reply
            end_response = f"Answer was: '{document['answer']}'"
        elif status == "end_game_win":
            new_times_won = document['times_won'] + 1
            document.update(times_won=new_times_won)
            document.save()
            document = HangmanChannel.objects.get(channel_id=message.channel.id)
            status_response = "Y'all saved thee stick person"
            cust_send = message.reply
            # end_response = f"Answer was: '{document['answer']}'"
        else:
            await message.reply(f"Nope Chody Messed {status} status up in get_post")
            return
        guesses_left = abs(document['guesses_made'] - document['max_guesses'])
        embed = discord.Embed(title=status_response, description=f"{stages[document['guesses_made']]}\n{''.join(document['partial_answer'])}\n{guesses_left} stick-person pieces left")
        embed.add_field(name=f"Already Guessed:", value=f"{document['guessed_letters']}\n{'' if end_response is None else end_response}", inline=False)
        await cust_send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        channelid = message.channel.id
        try:
            document = HangmanChannel.objects.get(channel_id=channelid)
        except Exception as m:
            if FileNotFoundError:
                return
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error loading hangman document for {channelid} -- {m}")
                return
        if message.author.bot:
            return
        if message.content.startswith(ignore_keys):
            return
        usersperms = await perm_check(message, message.guild.id)
        if usersperms is None:
            await message.reply(PermError)
            return
        answer_completed, match_detected = False, False
        try:
            user_document = HangmanUser.objects.get(user_id=message.author.id, channel_id=channelid)
        except Exception as e:
            if FileNotFoundError:
                try:
                    hangman_user_collection = self.bot.channel_ids.get_collection('hangman_user')
                    user_document_id = str(message.author.id)[:5] + str(channelid)[:5] + str(random.randint(1, 99))
                    user_document_id = int(user_document_id)
                    new_user_document = HangmanUser(document_id=user_document_id, user_id=message.author.id, user_name=message.author.name,
                                                    user_nick_name=message.author.display_name, guild_id=message.guild.id,
                                                    guild_name=message.guild.name, channel_id=channelid, channel_name=message.channel.name)
                    new_user_document_dict = new_user_document.to_mongo()
                    hangman_user_collection.insert_one(new_user_document_dict)
                    user_document = HangmanUser.objects.get(user_id=message.author.id, channel_id=channelid)
                    pass
                except Exception as f:
                    user_document = None
                    await message.reply(ErrorMsgOwner.format(OWNERTAG, f"Error creating/reading user document file -- {f} -- You can ignore this, and keep playing"), delete_after=20)
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error creating/reading user document file -- {f}")
                    pass
            else:
                user_document = None
                await message.reply(ErrorMsgOwner.format(OWNERTAG, f"Error creating/reading user document file -- {e} -- You can ignore this, and keep playing"), delete_after=20)
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error creating/reading user document file -- {e}")
                pass

        print(f"Hangmnlistener -- {message.author.name} -- {channelid} --")
        if len(message.content.split()) > 1:
            prev_author = message.author
            await message.delete()
            await message.channel.send(f"{prev_author.mention} Only one word can be entered at a time, you lost 10 points", silent=True, delete_after=10)
            await remove_points(self, message, message.author.id, 10, False)
            return
        elif len(message.content) > 1:
            if len(message.content) != len(document['answer']):
                prev_author = message.author
                await message.delete()
                await message.channel.send(f"{prev_author.mention} your guess isn't thee right amount of letters, you lost 10 points, try again", silent=True, delete_after=20)
                await remove_points(self, message, message.author.id, 10, False)
                return
            letter_guess = False
        else:
            letter_guess = True
        guess = message.content.lower()
        if letter_guess:
            if guess in document['guessed_letters']:
                prev_author = message.author
                await message.delete()
                await message.channel.send(f"{prev_author.mention} {guess} has already been guessed, you lost 10 points, try again with a different letter", silent=True, delete_after=20)
                await remove_points(self, message, message.author.id, 10, False)
                return
            for i, letter in enumerate(document['answer']):
                if letter == guess:
                    match_detected = True
                    new_partial_answer = document['partial_answer']
                    new_partial_answer[i] = guess
                    document.update(partial_answer=new_partial_answer)
                    document.save()
                    document = HangmanChannel.objects.get(channel_id=channelid)
                    if ''.join(document['partial_answer']) == document['answer']:
                        answer_completed = True
                        break
        elif not letter_guess:
            if document['word_guesses_made'] >= document['max_wordguesses'] and guess != document['answer']:
                await message.reply(f"Ooof, {message.author.mention} attempted to guess thee whole word, but the max attempts have been breached, you lost 10 points.", silent=True)
                await self.update_user_stats(message, user_document, 1, 0, 1)
                await self.get_post(message, document, status="end_game")
                await self.reset_game(self, message)
                await remove_points(self, message, message.author.id, 10, False)
                return
            elif guess == document['answer']:
                await self.update_user_stats(message, user_document, 1, 1, 0)
                await self.get_post(message, document, status="end_game_win")
                await self.reset_game(self, message)
                await add_points(self, message, message.author.id, 100, False)
                return
            elif guess != document['answer']:
                new_word_guesses_made = document['word_guesses_made'] + 1
                if document['word_guesses_made'] >= document['max_wordguesses']:
                    response = "Y'all are outta word guesses"
                else:
                    new_word_guesses_left = abs(new_word_guesses_made - document['max_wordguesses'])
                    response = f"Y'all have {new_word_guesses_left} word guesses left"
                await self.update_user_stats(message, user_document, 1, 0, 1)
                new_word_guesses_made = document['word_guesses_made'] + 1
                document.update(word_guesses_made=new_word_guesses_made, prev_author=message.author.name)
                document.save()
                await message.channel.send(f"{message.author.name} that wasn't correct, you lost 20 points. {response}")
                await remove_points(self, message, message.author.id, 20, False)
                return
        if answer_completed:
            new_guessed_letters = document['guessed_letters'] + guess
            document.update(guessed_letters=new_guessed_letters)
            document.save()
            document = HangmanChannel.objects.get(channel_id=channelid)
            await self.update_user_stats(message, user_document, 1, 1, 0)
            await self.get_post(message, document, status="end_game_win")
            await self.reset_game(self, message)
            await add_points(self, message, message.author.id, 100, False)
            return
        elif match_detected:
            new_guessed_letters = document['guessed_letters'] + guess
            document.update(guessed_letters=new_guessed_letters, prev_author=message.author.name)
            document.save()
            document = HangmanChannel.objects.get(channel_id=channelid)
            await self.update_user_stats(message, user_document, 1, 1, 0)
            await self.get_post(message, document)
            await add_points(self, message, message.author.id, 5, False)
            return
        elif not answer_completed:
            new_guesses_made = document['guesses_made'] + 1
            if new_guesses_made >= document['max_guesses']:
                new_guessed_letters = document['guessed_letters'] + guess
                document.update(guesses_made=new_guesses_made, guessed_letters=new_guessed_letters)
                document.save()
                document = HangmanChannel.objects.get(channel_id=channelid)
                await self.update_user_stats(message, user_document, 1, 0, 1)
                await self.get_post(message, document, status="end_game")
                await self.reset_game(self, message)
                await remove_points(self, message, message.author.id, 10, False)
                return
            new_guessed_letters = document['guessed_letters'] + guess
            document.update(guessed_letters=new_guessed_letters, guesses_made=new_guesses_made, prev_author=message.author.name)
            document.save()
            document = HangmanChannel.objects.get(channel_id=channelid)
            await self.update_user_stats(message, user_document, 1, 0, 1)
            await self.get_post(message, document)
            await remove_points(self, message, message.author.id, 10, False)
            return

    @commands.command()
    async def hangman(self, ctx, operator=None):
        """$hangman 'operator'
        :OPERATOR:
        listservers
        listusers
        highscoreservers
        highscoreusers"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            await ctx.reply(PermError)
            return
        channelid = ctx.channel.id
        hangman_collection = self.bot.channel_ids.get_collection('hangman_channel')
        hangman_user_collection = self.bot.channel_ids.get_collection('hangman_user')
        if operator is None:
            await ctx.reply(f"Operator is missing, please try again")
            return
        elif operator == "listservers":
            try:
                hangman_documents = hangman_collection.find({})
                hangman_documents_sorted = sorted(hangman_documents, key=lambda document: document['times_won'], reverse=True)
                embed = discord.Embed(title=f"Servers Playing Hangman Sorted By 'Times Won'", description="", color=0x069000)
                for n, document in enumerate(hangman_documents_sorted):
                    if document['times_won'] == 0:
                        win_loss = 0
                    else:
                        total_games_played = document['times_won'] + document['times_lost']
                        win_loss = 100 - document['times_lost'] / total_games_played * 100
                    embed.add_field(name=f"{n+1}: {document['guild_name']}:\nW/L: {document['times_won']}/{document['times_lost']} ({round(win_loss, 2)}%)", value="", inline=False)
                await ctx.channel.send(embed=embed)
                return
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something went wrong listing server documents data\n{channelid}: {e}")
                return
        elif operator == "listusers":
            try:
                hangman_user_collection = hangman_user_collection.find({"channel_id": channelid})
                hangman_user_collection_sorted = sorted(hangman_user_collection, key=lambda document: document['total_guesses'], reverse=True)
                embed = discord.Embed(title=f"Top 10 Users Playing In This Channel Sorted By: 'Total Guesses'", description="", color=0x069000)
                for n, document in enumerate(hangman_user_collection_sorted):
                    if n >= 10:
                        break
                    if document['total_guesses'] == 0:
                        user_accuracy = 0
                    elif document['wrong_guesses'] == 0:
                        user_accuracy = 100
                    else:
                        user_accuracy = 100 - document['wrong_guesses'] / document['total_guesses'] * 100
                    embed.add_field(name=f"{n+1}: {document['total_guesses']}: {document['user_nick_name']}", value=f"Accuracy: {round(user_accuracy, 2)}%", inline=False)
                await ctx.channel.send(embed=embed)
                return
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something went wrong listing highscores data\n{channelid}: {e}")
                return
        elif operator == "highscoreservers":
            await ctx.reply(f"TBD")
            return
        elif operator == "highscoreusers":
            await ctx.reply(f"TBD")
            return
        else:
            await ctx.reply(f"Either {operator} wasn't valid, or your command isn't programmed yet")
            return

    @commands.command()
    async def hangmanuser(self, ctx, operator=None, user=None):
        """$hangmanuser 'operator'
        :OPERATOR:
        stats
        globalstats"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            await ctx.reply(PermError)
            return
        hangman_user_collection = self.bot.channel_ids.get_collection('hangman_user')
        if user is None:
            userid = ctx.author.id
        else:
            userid = int(user[2:-1])
        if operator is None:
            await ctx.reply(f"Operator is missing, try again")
            return
        elif operator in ("stat", "stats"):
            try:
                user_document = HangmanUser.objects.get(user_id=ctx.author.id, channel_id=ctx.channel.id)
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"You haven't started playing in this channel yet")
                    return
                else:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error fetching user document in {ctx.guild.id, ctx.channel.id} for {ctx.author.name, ctx.author.id}")
                    return
            if user_document['wrong_guesses'] == 0:
                user_accuracy = 100
            else:
                user_accuracy = 100 - user_document['wrong_guesses'] / user_document['total_guesses'] * 100
            embed = discord.Embed(title=f"Your channel stats are:", description="", color=0x000069)
            embed.add_field(name=f"Total Times Guessed: {user_document['total_guesses']}\nTotal Right Guessed: {user_document['right_guesses']}\nTotal Wrong Guesses: {user_document['wrong_guesses']}\nTotal Accuracy: {round(user_accuracy, 2)}%", value="", inline=False)
            await ctx.reply(embed=embed)
        elif operator in ("globalstat", "globalstats"):
            try:
                user_name = await self.bot.fetch_user(userid)
                users_documents = hangman_user_collection.find({"user_id": userid})
                users_total_guesses = 0
                users_right_guesses = 0
                users_wrong_guesses = 0
                for document in users_documents:
                    users_total_guesses += document['total_guesses']
                    users_right_guesses += document['right_guesses']
                    users_wrong_guesses += document['wrong_guesses']
                if users_wrong_guesses == 0:
                    user_accuracy = 100
                else:
                    user_accuracy = 100 - users_wrong_guesses / users_total_guesses * 100
                embed = discord.Embed(title="Your Global Stats:" if user is None else f"{user_name.display_name}'s Global Stats:", description="", color=0x000690)
                embed.add_field(name=f"Total Guesses: {users_total_guesses:,}\nRight Guesses: {users_right_guesses:,}\nWrong Guesses: {users_wrong_guesses:,}\nTotal Accuracy: {round(user_accuracy, 2)}%", value="", inline=False)
                await ctx.channel.send(embed=embed)
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"You don't have a document yet, because you haven't started playing. If this is wrong, contact {OWNERTAG}.")
                    return
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error getting GLOBAL stats for {ctx.author.id, ctx.author.name} in {ctx.channel.id} -- {e}")
                    return
        else:
            await ctx.reply(f"TBD/{operator} isn't valid, u pick")
            return

    @commands.command()
    async def hangmanconfig(self, ctx, operator=None, value=None):
        """MOD & UP USE ONLY
        $hangmanconfig 'operator' 'value'
        :OPERATOR:
        add
        remove
        multipleguesses
        :VALUE: -- ONLY Needed For MultipleGuesses OPERATOR
        true
        false"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin", "mod"):
            await ctx.reply(PermError)
            return
        if operator is None:
            await ctx.reply(f"Operator is missing, please try again")
            return
        channelid = ctx.channel.id
        hangman_channel_collection = self.bot.channel_ids.get_collection('hangman_channel')
        hangman_user_collection = self.bot.channel_ids.get_collection('hangman_user')
        if operator == "add":
            try:
                if hangman_channel_collection.find_one({"_id": channelid}):
                    await ctx.reply(f"There is already a document for hangman in this channel")
                    return
                else:
                    await self.reset_game(self, ctx, "start")
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f"Error creating/reading document -- {e}"))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error creating/reading document for Hangman Channel in {channelid} -- {e}")
                return
        elif operator == "remove":
            try:
                if hangman_channel_collection.find_one({"_id": channelid}):
                    hangman_channel_collection.delete_one({"_id": channelid})
                    user_documents = hangman_user_collection.find({})
                    n = 0
                    for document in user_documents:
                        if document['channel_id'] == channelid:
                            hangman_user_collection.delete_one({"_id": document['_id']})
                            n += 1
                    await ctx.reply(f"Old document deleted.\n{f'{n} user documents deleted as well' if n>0 else ''}")
                    return
                else:
                    await ctx.reply(f"There isn't a document for hangman in this channel yet")
                    return
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f"Error deleting/reading document -- {e}"))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error deleting/reading document for Hangman Channel in {channelid} -- {e}")
                return
        elif operator == "multipleguesses":
            if value is None:
                await ctx.reply(f"Value is missing, try again")
                return
            try:
                document = HangmanChannel.objects.get(channel_id=channelid)
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"There is no document for hangman in this channel yet")
                    return
                else:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error loading document for hangman in {channelid} channel. -- {e}")
                    return
            if value.lower() == "true":
                if document['allowedmultguesses']:
                    await ctx.reply(f"Multiple guesses is already on")
                    return
                else:
                    document.update(allowedmultguesses=True)
                    document.save()
                    await ctx.reply(f"Multiple guesses is now on")
                    return
            elif value.lower() == "false":
                if document['allowedmultguesses']:
                    document.update(allowedmultguesses=False)
                    document.save()
                    await ctx.reply(f"Multiple guesses is now off")
                    return
                else:
                    await ctx.reply(f"Multiple guesses is already off")
                    return
            else:
                await ctx.reply(f"{value} isn't correct, try again")
                return
        else:
            await ctx.reply(f"{operator} isn't valid, try again")
            return


async def setup(bot):
    await bot.add_cog(HangmanCog(bot))
