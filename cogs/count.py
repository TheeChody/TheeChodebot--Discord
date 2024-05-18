import os
import ast
import random
import discord
import wolframalpha
from dotenv import load_dotenv
from discord.ext import commands
from cogs.mondocs import CountChannel, CountUser
from cogs.economy import add_points, remove_points
from chodebot import logger, perm_check, fortime, number_emojis, guifo, PermError, ErrorMsgOwner, OWNERTAG, ignore_keys  #, ranff

load_dotenv()
wolframalphatoken = os.getenv("wolframalphatoken")


class CountCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wolframalphaclient = wolframalpha.Client(wolframalphatoken)

    @staticmethod
    async def update_game_stats(message, document, correct: bool = False, died: bool = False):
        try:
            new_rankability = document['streakrankability']
            new_highscore = document['highscore']
            new_infraction_count = document['infraction_count']
            if correct:
                previous_author = message.author.name
                new_goal_number = document['goal_number'] + document['step']
                new_warninglevel = document['warninglevel']
                if document['goal_number'] > document['highscore'] and document['streakrankability']:
                    new_highscore = document['goal_number']
                if document['warninglevel'] >= 1 and document['infraction_count'] + 500 <= document['goal_number']:
                    new_warninglevel = document['warninglevel'] - 1
                    if new_warninglevel == 0:
                        new_infraction_count = 0
                        await message.channel.send(f"Warning level back @ 0.")
                    else:
                        new_infraction_count = document['goal_number']
                        await message.channel.send(f"Warning level reduced by 1. Next reduction @ {new_infraction_count+500:,}.")
            elif not correct:
                if died:
                    new_infraction_count = 0
                    new_goal_number = document['step']
                    new_rankability = True
                    previous_author = ""
                    new_warninglevel = 0
                else:
                    new_infraction_count = document['goal_number'] - document['step']
                    new_goal_number = document['goal_number']
                    previous_author = document['previous_author']
                    new_warninglevel = document['warninglevel'] + 1
            else:
                await message.channel.send(ErrorMsgOwner.format(OWNERTAG, "Not Correct, Not InCorrect, something else in count update_game_stats"))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Not Correct, Not InCorrect, something else in count update_game_stats")
                return
            document.update(channel_name=message.channel.name, guild_name=message.guild.name, previous_author=previous_author, goal_number=new_goal_number,
                            warninglevel=new_warninglevel, highscore=new_highscore, infraction_count=new_infraction_count, streakrankability=new_rankability)
            document.save()
        except Exception as e:
            await message.channel.send(ErrorMsgOwner.format(OWNERTAG, e))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error updating game stats for counting game :: {e}")
            return

    @staticmethod
    async def update_user_stats(message, user_document, add_times_counted: int, add_times_failed: int, add_times_warned: int, compare_count_highest: int):
        try:
            new_times_counted = user_document['times_counted'] + add_times_counted
            new_times_failed = user_document['times_failed'] + add_times_failed
            new_times_warned = user_document['times_warned'] + add_times_warned
            new_total_counted = user_document['total_counted'] + compare_count_highest
            if compare_count_highest > user_document['count_highest']:
                new_count_highest = compare_count_highest
            else:
                new_count_highest = user_document['count_highest']
            user_document.update(user_nick_name=message.author.display_name, guild_name=message.guild.name, channel_name=message.channel.name,
                                 times_counted=new_times_counted, times_failed=new_times_failed, times_warned=new_times_warned,
                                 total_counted=new_total_counted, count_highest=new_count_highest)
            user_document.save()
        except Exception as e:
            await message.channel.send(ErrorMsgOwner.format(OWNERTAG, e))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error updating user stats -- {e}")
            return

    @staticmethod
    async def solve_wolframalpha(self, expression):
        res = self.wolframalphaclient.query(expression)
        if not res.success:
            return
        for idmatch in (
                "IntegerSolution", "Solution", "SymbolicSolution",
                "Result", "DecimalApproximation",
                "RealAlternateForm", "AlternateForm"):
            for pod in res.pods:
                if pod.id == idmatch:
                    answers = []
                    for subpod in pod.subpods:
                        answers.append(subpod.plaintext)
                    return answers

    @staticmethod
    async def parse_and_evaluate_expression(expression):
        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError:
            return
        if not all(
                isinstance(node, (ast.Expression, ast.UnaryOp, ast.unaryop, ast.BinOp, ast.operator, ast.Num)) for node
                in ast.walk(tree)):
            raise ArithmeticError(expression + " is not a valid or safe expression.")
        result = eval(compile(tree, filename='', mode='eval'))
        return result

    @staticmethod
    async def attempt_count(self, message, guess, channelid):
        document = CountChannel.objects.get(channel_id=channelid)
        if document['pro_channel']:
            if message.author.id not in document['pro_users']:
                author = message.author
                await message.delete()
                await message.channel.send(f"{author.mention} You cannot count here! :P", delete_after=20)
                return
        try:
            user_document = CountUser.objects.get(user_id=message.author.id, channel_id=channelid)
        except Exception as e:
            if FileNotFoundError:
                try:
                    new_document_id = str(message.author.id)[:5] + str(channelid)[:5] + str(random.randint(1, 99))
                    new_document_id = int(new_document_id)
                    count_user = self.bot.channel_ids.get_collection('count_user')
                    new_document = CountUser(document_id=new_document_id, user_id=message.author.id, user_name=message.author.name,
                                             user_nick_name=message.author.display_name, guild_name=message.guild.name, channel_id=channelid)
                    new_document_dict = new_document.to_mongo()
                    count_user.insert_one(new_document_dict)
                    user_document = CountUser.objects.get(user_id=message.author.id, channel_id=channelid)
                except Exception as f:
                    if FileExistsError:
                        try:
                            new_document_id = str(message.author.id)[:5] + str(channelid)[:5] + str(random.randint(1, 999))
                            new_document_id = int(new_document_id)
                            count_user = self.bot.channel_ids.get_collection('count_user')
                            new_document = CountUser(document_id=new_document_id, user_id=message.author.id,
                                                     user_name=message.author.name,
                                                     user_nick_name=message.author.display_name,
                                                     guild_name=message.guild.name, channel_id=channelid)
                            new_document_dict = new_document.to_mongo()
                            count_user.insert_one(new_document_dict)
                            user_document = CountUser.objects.get(user_id=message.author.id, channel_id=channelid)
                        except Exception as g:
                            formatted_time = await fortime()
                            logger.error(f"{formatted_time}: Error creating document for {message.author.name, message.author.id, message.channel.id} :: {g}")
                            await message.reply(ErrorMsgOwner.format(OWNERTAG, "Something went wrong creating a document for your stats"))
                            return
                    else:
                        formatted_time = await fortime()
                        logger.error(f"{formatted_time}: Error creating document for {message.author.name, message.author.id, message.channel.id} :: {f}")
                        await message.reply(ErrorMsgOwner.format(OWNERTAG, "Something went wrong creating a document for your stats"))
                        return
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error finding user document for {message.author.name, message.author.id, message.channel.id} :: {e}")
                await message.reply(ErrorMsgOwner.format(OWNERTAG, "Something went wrong finding your stat document"))
                return
        if document['roundallguesses']:
            guess = int(round(guess))
            goal_number = round(document['goal_number'])
        else:
            guess = round(guess, 8)
            goal_number = round(document['goal_number'], 8)
        died = False
        if message.author.name == document['previous_author'] and not document['allowedmultguesses']:
            if document['allowedwarning']:
                if document['warninglevel'] == document['warningmax']:
                    await message.reply(f"Oof. {message.author.mention} counted twice in a row.\n\nThe next number is {document['step']}.", silent=True)
                    died = True
                else:
                    await message.add_reaction("⚠️")
                    await self.update_game_stats(message, document, False, False)
                    document = CountChannel.objects.get(channel_id=channelid)
                    warningsleft = abs(document['warninglevel'] - document['warningmax'])
                    await message.reply(f"Woooaahh there {message.author.mention}, slow down eh? Multiple guesses is turned off right now.\n{warningsleft} warnings left.\nCan earn back a warning level in 500 successful counts", silent=True)
                    await self.update_user_stats(message, user_document, 0, 0, 1, 0)
                    return
            else:
                await message.reply(f"Oof. {message.author.mention} counted twice in a row.\n\nThe next number is {document['step']}.", silent=True)
                died = True
        elif guess == goal_number:
            await self.update_game_stats(message, document, True, False)
            document = CountChannel.objects.get(channel_id=channelid)
            if guess >= document['highscore'] and document['streakrankability']:
                await message.add_reaction("☑️")
            else:
                await message.add_reaction("✅")
            reaction = await number_emojis(guess)
            if reaction is not None:
                await message.add_reaction(reaction)
            await add_points(self, message, message.author.id, 5, False)
            await self.update_user_stats(message, user_document, 1, 0, 0, guess)
        elif guess != goal_number:
            if document['allowedwarning']:
                if document['warninglevel'] == document['warningmax']:
                    await message.reply(f"Oof. The next number was {document['goal_number']}, but {message.author.mention} guessed {guess}.\nThe next number is {document['step']}.", silent=True)
                    died = True
                else:
                    await message.add_reaction("⚠️")
                    await self.update_game_stats(message, document, False, False)
                    document = CountChannel.objects.get(channel_id=channelid)
                    warningsleft = abs(document['warninglevel'] - document['warningmax'])
                    await message.reply(f"{message.author.mention} guessed {guess} but it wasn't correct.\n{warningsleft} warnings left.\nCan earn back a warning level in 500 successful counts", silent=True)
                    await remove_points(self, message, message.author.id, 10, False)
                    await self.update_user_stats(message, user_document, 0, 0, 1, 0)
                    return
        if died:
            await message.add_reaction("🛑")
            await self.update_game_stats(message, document, False, True)
            await remove_points(self, message, message.author.id, 25, False)
            await self.update_user_stats(message, user_document, 0, 1, 0, 0)

    @commands.Cog.listener()
    async def on_message(self, message):
        channelid = message.channel.id
        try:
            document = CountChannel.objects.get(channel_id=channelid)
        except Exception as m:
            if FileNotFoundError:
                return
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error loading count document for {channelid} -- {m}")
                return
        if message.author.bot:
            return
        if message.content.startswith(ignore_keys, 0, 2):
            return
        usersperms = await perm_check(message, message.guild.id)
        if usersperms is None:
            await message.reply(PermError)
            return
        print(f"countlistener -- {message.author.name} -- {channelid} --")  # {message.content} -- {CountChannel.objects.get(channel_id=channelid)} --")  # {message.author}")
        if message.content.startswith("|"):
            query = message.content[1:]
            if not document['enablewolframalpha']:
                await message.add_reaction("‼")
                await message.reply('Wolfram|Alpha queries have been disabled by an administrator.')
                return
            res = await self.solve_wolframalpha(self, query)
            if res is None or res == [] or res == [""]:
                await message.reply('Wolfram|Alpha did not return an answer for that query.')
                return
            if type(res) == list:
                res = res[0]
            try:
                if "\n" in res:
                    res = res.split("\n")[0]
            except Exception as e:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Debugging 254\n{e}")
                pass
            while res.count(".") > 1:
                splitres = res.split(".")
                res = splitres[0] + ("".join(splitres[1:]))
            try:
                res = float("".join(list(filter(lambda x: x.isnumeric() or x in ".-", res))))
            except Exception as e:
                await message.add_reaction("<:Blunder:887422389040844810>")
                await message.reply(f'The answer to that does not seem to convert nicely into a number. ({e})')
                raise ArithmeticError(f"Could not convert answer {res} into a number")
            await self.attempt_count(self, message, res, channelid)
        elif document['expressionenabled']:
            firstword = message.content.split(" ")[0]
            contains_digit = False
            digits = "0123456789"
            if "0x" in firstword:
                digits += "abcdefABCDEF"
            for digit in digits:
                if digit in firstword:
                    contains_digit = True
            if not contains_digit:
                return
            try:
                ex = await self.parse_and_evaluate_expression(firstword)
            except Exception as e:
                await message.reply(f"{e} is tripping an error, try again")
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Debugging 282\n{e}")
                pass
            else:
                if not type(ex) in (int, float):
                    return
                await self.attempt_count(self, message, ex, channelid)
        else:
            firstword = message.content.split(" ")[0]
            contains_digit = False
            digits = "0123456789"
            if "0x" in firstword:
                digits += "abcdefABCDEF"
            for digit in digits:
                if digit in firstword:
                    contains_digit = True
            if not contains_digit:
                return
            # firstword = message.content.split(" ")[0]
            # if type(firstword) != int:
            #     return
            # else:
            try:
                ex = float(firstword)
                if ex.is_integer():
                    ex = int(ex)
            except Exception as e:
                await message.reply(f"{e} is tripping an error, try again")
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Debugging 310\n{e}")
                return
            await self.attempt_count(self, message, ex, channelid)

    @commands.command()
    async def wolframalpha(self, ctx):
        """Not Used"""
        # message = str(await self.solve_wolframalpha(" ".join(expression)))
        # if message in ("", "None"):
        #     message = "[Empty output]"
        message = """As of 3/19/2022, 8:30 PM CEST, the c#wolframalpha command has been disabled to prevent it from being overused and single-handedly using up the API key. From now on, please use the official Wolfram|Alpha website. https://wolframalpha.com/"""
        await ctx.reply(message)

    @commands.command()
    async def expr(self, ctx, message, *expression):
        """To Test Expressions?"""
        try:
            message = str(await self.parse_and_evaluate_expression(" ".join(expression)))
        except ArithmeticError:
            await ctx.reply(f"ArithmeticError: {expression} is not a valid or safe expression.")
        if message in ("", "None"):
            message = "[Empty output]"
        await ctx.reply(message)

    @commands.command()
    async def count(self, ctx, operator):
        """Perform operations on this channel
        $count operator
        :OPERATOR:
        add (Mods & Up)
        remove (Mods & Up)
        lastguess
        listservers
        listusers
        globalusers
        highscoreservers
        highscoreusers
        rankable
        warninglevel
        warninglevelreset"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            await ctx.reply(PermError)
            return
        channelid = int(ctx.channel.id)
        count_user_collection = self.bot.channel_ids.get_collection('count_user')
        count_channel_collection = self.bot.channel_ids.get_collection('count_channel')

        def check(m):
            return m.content.lower() == "yes" or "no" and m.channel.id == ctx.channel.id
        if operator == "add":
            if usersperms == "normal":
                await ctx.reply(PermError)
                return
            try:
                new_document = CountChannel(channel_id=channelid, channel_name=ctx.channel.name, guild_id=ctx.guild.id, guild_name=ctx.guild.name)
                new_document_dict = new_document.to_mongo()
                count_channel_collection.insert_one(new_document_dict)
                await ctx.reply(f"Count game has begun!")
            except Exception as e:
                if FileExistsError:
                    await ctx.reply(f"A document with {channelid} has been found, would you like to erase it and create a new one?")
                    response = await self.bot.wait_for("message", check=check, timeout=60)
                    if response.content == "yes":
                        count_channel_collection.delete_one({"_id": channelid})
                        await ctx.reply(f"Old document deleted:{response.content}")
                        new_document = CountChannel(channel_id=channelid, channel_name=ctx.channel.name, guild_name=ctx.guild.name)
                        new_document_dict = new_document.to_mongo()
                        count_channel_collection.insert_one(new_document_dict)
                        await ctx.reply(f"Count game has begun!")
                        return
                    elif response.content == "no":
                        await ctx.reply(f"Document NOT deleted")
                        return
                    else:
                        await ctx.reply(f"{response.content} is not valid, try again.")
                        return
                else:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Something went wrong adding document\n{channelid}: {e}")
                    return
        elif operator == "remove":
            if usersperms == "normal":
                await ctx.reply(PermError)
                return
            try:
                if count_channel_collection.find_one({"_id": channelid}):
                    count_channel_collection.delete_one({"_id": channelid})
                    user_documents = count_user_collection.find({})
                    n = 0
                    for document in user_documents:
                        if document['channel_id'] == channelid:
                            count_user_collection.delete_one({"_id": document['_id']})
                            n += 1
                    await ctx.reply(f"Old Document Deleted\n{f'{n} user documents deleted as well.' if n>0 else ''}")
                    return
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"There isn't a document yet matching {channelid}.")
                    return
                else:
                    await ctx.reply(f'something went wrong, either {channelid} or error msg ( {e} )')
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Something went wrong removing document\n{channelid}: {e}")
                    return
        elif operator in ("lastguess", "lastguessed"):
            try:
                document = CountChannel.objects.get(channel_id=channelid)
                lastguess = document['goal_number'] - document['step']
                await ctx.reply(f"The last valid guess was {lastguess}")
                return
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"This channel is not registered")
                    return
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error lastguess count command: {e}")
                    return
        elif operator in ("listserver", "listservers"):
            try:
                countdocuments = count_channel_collection.find({})
                countdocuments_sorted = sorted(countdocuments, key=lambda document: document['goal_number'], reverse=True)
                n = 1
                channel = self.bot.get_channel(channelid)
                embed = discord.Embed(title=f"List of Servers Playing Thee Counting Game:", description="Current(step)", color=0x006900)
                for document in countdocuments_sorted:
                    displaycount = document['goal_number'] - document['step']
                    embed.add_field(name=f"{n}: {document['guild_name']}: {displaycount}({document['step']})", value=f"{document['channel_name'] if document['guild_id'] == guifo.chodeling_id else ''}", inline=False)
                    n += 1
                await channel.send(channel, embed=embed)
                return
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something went wrong listing server documents data\n{channelid}: {e}")
                return
        elif operator in ("listuser", "listusers"):
            try:
                userdocuments = count_user_collection.find({"channel_id": channelid})
                userdocuments_sorted = sorted(userdocuments, key=lambda document: document['times_counted'], reverse=True)
                embed = discord.Embed(title=f"Top 10 List of Users in This Channel by 'Times Counted':", description="", color=0x006900)
                n = 1
                for document in userdocuments_sorted:
                    infraction_total = document['times_failed'] + document['times_warned']
                    if infraction_total == 0:
                        user_accuracy = 100
                    else:
                        user_accuracy = 100 - infraction_total / document['times_counted'] * 100
                    embed.add_field(name=f"{n}: {document['times_counted']}: {document['user_nick_name']} -- Accuracy: {round(user_accuracy, 2)}%", value="", inline=False)
                    n += 1
                    if n == 11:
                        break
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something went wrong listing users documents data\n{channelid}: {e}")
                return
        elif operator in ("highscoreserver", "highscoreservers"):
            try:
                top_scores = count_channel_collection.find({})
                top_scores = sorted(top_scores, key=lambda document: document['highscore'], reverse=True)
                n = 1
                channel = self.bot.get_channel(channelid)
                embed = discord.Embed(title=f"List of High Scores:", description="HighScore(step)", color=0x006900)
                for document in top_scores:
                    embed.add_field(name=f"{n}: {document['guild_name']}: {document['highscore']}({document['step']})", value=f"{document['channel_name'] if document['guild_id'] == guifo.chodeling_id else ''}", inline=False)
                    n += 1
                await channel.send(channel, embed=embed)
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something went wrong listing highscores data\n{channelid}: {e}")
                return
        elif operator in ("highscoreuser", "highscoreusers"):
            try:
                top_user_scores = count_user_collection.find({"channel_id": channelid})
                top_user_scores_sorted = sorted(top_user_scores, key=lambda document: document['count_highest'], reverse=True)
                n = 1
                embed = discord.Embed(title=f"Top 10 List of Users in This Channel by 'Highest Counted'", description="", color=0x006900)
                for document in top_user_scores_sorted:
                    infraction_total = document['times_failed'] + document['times_warned']
                    if infraction_total == 0:
                        user_accuracy = 100
                    else:
                        user_accuracy = 100 - infraction_total / document['times_counted'] * 100
                    embed.add_field(name=f"{n}: {document['count_highest']}: {document['user_nick_name']} -- Accuracy: {round(user_accuracy, 2)}%", value="", inline=False)
                    n += 1
                    if n == 11:
                        break
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something went wrong listing users documents data\n{channelid}: {e}")
                return
        elif operator in ("globalhighscoreuser", "globalhighscoreusers"):
            if usersperms != "owner":
                await ctx.reply(f"Command is still in progress")
                return
            # try:
            #     pipeline = [
            #         {
            #             "$match": {
            #                 "_id": "$user_id"
            #             }
            #         },
            #         {
            #             "$sort": {
            #                 "count_highest": pymongo.ASCENDING
            #             }
            #         }
            #     ]
            #     user_id_sorted = count_user_collection.aggregate(pipeline)
            #     for user in user_id_sorted:
            #         if
            #
            #
            #     top_global_user_scores = count_user_collection.find({})
            #     for document in top_global_user_scores:
        elif operator in ("globaluser", "globalusers"):
            if usersperms != "owner":
                await ctx.reply(f"Command is still in progress")
                return
            # try:
            #     count_user_documents = count_user_collection.find({})
            #     count_user_documents_sorted = sorted(count_user_documents, key=lambda document: document['times_counted'], reverse=True)
            #     ten_count_user_documents_sorted = count_user_documents_sorted[:10]
            #     embed = discord.Embed(title=f"Top 10 Global Users By 'Times Counted'", description="", colour=0x060900)
            #     for n, document in enumerate(ten_count_user_documents_sorted):
            #         infraction_total = document['times_warned'] + document['times_failed']
            #         if infraction_total == 0:
            #             user_accuracy = 100
            #         else:
            #             user_accuracy = 100 - infraction_total / document['times_counted'] * 100
            #         embed.add_field(name=f"{n+1}: {document['user_nick_name']}", value=f"{document['times_counted']}/{infraction_total}:: {round(user_accuracy, 2)}%", inline=False)
            #     await ctx.channel.send(embed=embed)
            # except Exception as e:
            #     await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
            #     formatted_time = await fortime()
            #     logger.error(f"{formatted_time}: Something went wrong listing users documents data\n{channelid}: {e}")
            #     return
        elif operator == "rankable":
            try:
                channelid = ctx.channel.id
                document = CountChannel.objects.get(channel_id=channelid)
                if document is None:
                    await ctx.reply(f"This channel is not registered in the collection")
                    return
                rankable = document['streakrankability']
                await ctx.reply(f"{rankable}")
                if rankable:
                    await ctx.reply(f"{ctx.channel.name} is rankable")
                else:
                    await ctx.reply(f"{ctx.channel.name} is NOT rankable")
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"This channel is not registered in the collection")
                    return
                else:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Something went wrong getting rankable data\n{channelid}: {e}")
                    return
        elif operator in ("warninglevel", "warnlevel"):
            try:
                channelid = ctx.channel.id
                document = CountChannel.objects.get(channel_id=channelid)
                if document is None:
                    await ctx.reply(f"This channel is not registered to play thee count game")
                    return
                warningsleft = abs(document['warninglevel'] - document['warningmax'])
                await ctx.reply(f"Y'all got {warningsleft} warnings left")
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"This channel is not registered to play thee count game")
                    return
                else:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Something went wrong getting warning's left data\n{channelid}: {e}")
                    return
        elif operator == "warninglevelreset":
            try:
                document = CountChannel.objects.get(channel_id=channelid)
                if document['warninglevel'] == 0:
                    await ctx.reply(f"There is no warning level in this channel.. Yet.")
                    return
                else:
                    last_guessed = document['goal_number'] - document['step']
                    warning_level_reset = document['infraction_count'] + 500
                    await ctx.reply(f"Thee next warning level reduction is in {abs(last_guessed - warning_level_reset)} counts.")
                    return
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"This channel is not registered")
                    return
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error warninglevelreset count command: {e}")
                    return
        else:
            await ctx.reply(f"Try again, {operator} isn't valid")
            return

    @commands.command()
    async def countuser(self, ctx, operator, user=None):
        """$countuser operator user
        :OPERATOR:
        stats
        globalstats
        :User:
        Can be left blank to return your own stats, or @target_user to retrieve their stats"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            await ctx.reply(PermError)
            return
        channelid = ctx.channel.id
        count_user_collection = self.bot.channel_ids.get_collection('count_user')
        if user is None:
            userid = int(ctx.author.id)
        else:
            userid = int(user[2:-1])
        if operator in ("stat", "stats"):
            try:
                document = CountUser.objects.get(user_id=userid, channel_id=channelid)
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"You don't have a document yet, because you haven't started playing. If this is wrong, contact {OWNERTAG}.")
                    return
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error displaying stats for {ctx.author.name, ctx.author.id} in {channelid} ::{e}")
                    return
            infraction_total = document['times_failed'] + document['times_warned']
            if infraction_total == 0:
                accuracy_perc = 100
            else:
                accuracy_perc = 100 - infraction_total / document['times_counted'] * 100
            embed = discord.Embed(title="Your stats are:" if user is None else f"{document['user_nick_name']}'s stats are", description="", color=0x00FF00)
            embed.add_field(name=f"Times Counted: {document['times_counted']:,}\nWarned: {document['times_warned']:,}\nFailed: {document['times_failed']:,}\nAccuracy: {round(accuracy_perc, 2)}%\nTotal Counted:{document['total_counted']:,}\nHighest Counted: {document['count_highest']:,}", value="", inline=False)
            await ctx.reply(embed=embed)
        elif operator in ("globalstat", "globalstats"):
            try:
                users_documents = count_user_collection.find({"user_id": userid})
                pro_user = False
                user_name = await self.bot.fetch_user(userid)
                users_total_times_counted, users_total_times_failed, users_total_times_warned = 0, 0, 0
                users_total_total_counted, users_total_count_highest = 0, 0
                pro_users_total_times_counted, pro_users_total_times_failed, pro_users_total_times_warned = 0, 0, 0
                pro_users_total_total_counted, pro_users_total_count_highest = 0, 0
                for document in users_documents:
                    if document['channel_id'] == guifo.spc_count_pro:
                        pro_users_total_times_counted += document['times_counted']
                        pro_users_total_times_failed += document['times_failed']
                        pro_users_total_times_warned += document['times_warned']
                        pro_users_total_total_counted += document['total_counted']
                        if document['count_highest'] > pro_users_total_count_highest:
                            pro_users_total_count_highest = document['count_highest']
                        pro_user = True
                    else:
                        users_total_times_counted += document['times_counted']
                        users_total_times_failed += document['times_failed']
                        users_total_times_warned += document['times_warned']
                        users_total_total_counted += document['total_counted']
                        if document['count_highest'] > users_total_count_highest:
                            users_total_count_highest = document['count_highest']
                users_infractions_total = users_total_times_warned + users_total_times_failed
                if users_infractions_total == 0:
                    users_accuracy = 100
                else:
                    users_accuracy = 100 - users_infractions_total / users_total_times_counted * 100
                embed = discord.Embed(title="Your Global Stats:" if user is None else f"{user_name.display_name}'s Global Stats:", description="", color=0x006900)
                embed.add_field(name=f"Times Counted: {users_total_times_counted:,}\nTimes Warned: {users_total_times_warned:,}\nTimes Failed: {users_total_times_failed:,}\nTotal Accuracy: {round(users_accuracy, 2)}%\nHighest Counted: {users_total_count_highest:,}\nTotal Counted: {users_total_total_counted:,}", value="", inline=False)
                if pro_user:
                    pro_users_infraction_total = pro_users_total_times_warned + pro_users_total_times_failed
                    if pro_users_infraction_total == 0:
                        pro_users_accuracy = 100
                    else:
                        pro_users_accuracy = 100 - pro_users_infraction_total / pro_users_total_times_counted * 100
                    embed.add_field(name=f"Pro Channel Stats:", value="---------------------------", inline=False)
                    embed.add_field(name=f"Times Counted: {pro_users_total_times_counted:,}\nTimes Warned: {pro_users_total_times_warned:,}\nTimes Failed: {pro_users_total_times_failed:,}\nTotal Accuracy: {round(pro_users_accuracy, 2)}%\nHighest Counted: {pro_users_total_count_highest:,}\nTotal Counted: {pro_users_total_total_counted:,}", value="", inline=False)
                await ctx.send(embed=embed)
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"You don't have a document yet, because you haven't started playing. If this is wrong, contact {OWNERTAG}.")
                    return
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error getting GLOBAL stats for {ctx.author.id, ctx.author.name} in {ctx.channel.id} -- {e}")
                    return
        else:
            await ctx.send(f"{operator} isn't valid, try again", ephemeral=True)

    @commands.command()
    async def procount(self, ctx, operator=None, user=None):
        """For Current Pro Players TO Add New Players To Their Channel
        $procount operator USERID
        :OPERATOR:
        add
        remove"""
        channelid = ctx.channel.id
        document = CountChannel.objects.get(channel_id=channelid)
        if not document['pro_channel']:
            await ctx.reply(f"This isn't a pro count channel, these operations cannot be performed here")
            return
        elif ctx.author.id not in document['pro_users']:
            prev_author = ctx.author
            await ctx.message.delete()
            await ctx.channel.send(f"{prev_author.mention}You cannot add/remove members here, you aren't on thee list", delete_after=20)
            formatted_time = await fortime()
            logger.info(f"{formatted_time}: {prev_author.id, prev_author.name, prev_author.display_name} attempted to add {user} to {channelid} pro count channel.")
            return
        if operator is None:
            await ctx.channel.send(f"Operator is missing!!")
            return
        elif user is None:
            await ctx.channel.send(f"User is missing!! Must have the userid for the person you want to add. ")
            return
        if operator.lower() == "add":
            new_pro_users = document['pro_users']
            new_pro_users.append(user)
            document.update(pro_users=new_pro_users)
            document.save()
            return
        elif operator.lower() == "remove":
            usersperms = await perm_check(ctx, ctx.guild.id)
            if usersperms not in ("owner", "admin", "mod"):
                target_user = await self.bot.fetch_user(user)
                await ctx.reply(f"You cannot do that, get a mod/admin who is in the game to or reach out to {OWNERTAG}")
                formatted_time = await fortime()
                logger.info(f"{formatted_time}: {ctx.author.id, ctx.author.name, ctx.author.display_name} attempted to removed {user, target_user.name, target_user.display_name} from {channelid} pro count channel")
                return
            new_pro_users = document['pro_users']
            new_pro_users.remove(user)
            document.update(pro_users=new_pro_users)
            document.save()
            return
        else:
            await ctx.reply(f"{operator} isn't valid, try again")
            return

    @commands.command()
    async def countconfig(self, ctx, setting, value):
        """Performs Configuration Operations on This Channel
        Settings are:
        rankable
        roundguess
        multguess
        resethighscore
        allowmaths
        allowwarn
        warnlimit
        setcurrent
        setstep"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms in ("normal", None):
            await ctx.reply(PermError)
            return
        channelid = int(ctx.channel.id)
        try:
            document = CountChannel.objects.get(channel_id=channelid)
            if setting == "rankable":
                if value.lower() == "true":
                    if document['streakrankability']:
                        await ctx.reply(f"The streak is already rankable!!")
                        return
                    else:
                        rankable = True
                        document.update(streakrankability=rankable)
                        document.save()
                        await ctx.reply(f"Rankable updated to {rankable}")
                elif value.lower() == "false":
                    if not document['streakrankability']:
                        await ctx.reply(f"The streak is already not rankable!!")
                        return
                    else:
                        rankable = False
                        document.update(streakrankability=rankable)
                        document.save()
                        await ctx.reply(f"Rankable updated to {rankable}")
                else:
                    await ctx.reply(f"{value} wasn't valid, try again")
                    return
                formatted_time = await fortime()
                logger.info(f"{formatted_time}: {ctx.author.name} changed the rankability to {rankable} for {channelid}")
            elif setting == "roundguess":
                if value.lower() == "true":
                    if document['roundallguesses']:
                        await ctx.reply(f"Round All Guesses is already set to True")
                        return
                    else:
                        document.update(roundallguesses=True)
                        document.save()
                        await ctx.reply(f"Round All Guesses updated to True")
                elif value.lower() == "false":
                    if not document['roundallguesses']:
                        await ctx.reply(f"Round All Guesses is already False")
                        return
                    else:
                        document.update(roundallguesses=False)
                        document.save()
                        await ctx.reply(f"Round All Guesses updated to False")
                else:
                    await ctx.reply(f"{value} wasn't valid, try again")
                    return
            elif setting == "multguess":
                if value.lower() == "true":
                    if document['allowedmultguesses']:
                        await ctx.reply(f"Multiple Guesses is already allowed")
                        return
                    else:
                        document.update(allowedmultguesses=True)
                        document.save()
                        await ctx.reply(f"Multiple Guesses now allowed")
                elif value.lower() == "false":
                    if not document['allowedmultguesses']:
                        await ctx.reply(f"Multiple Guesses already not allowed")
                        return
                    else:
                        document.update(allowedmultguesses=False)
                        document.save()
                        await ctx.reply(f"Multiple Guesses now not allowed")
                else:
                    await ctx.reply(f"{value} wasn't valid, try again")
                    return
            elif setting == "resethighscore":
                if value.lower() == "true":
                    document.update(highscore=0)
                    document.save()
                    await ctx.reply(f"The highscore has been reset to 0")
                elif value.lower() == "false":
                    await ctx.reply(f"Then why you triggering me?? :P HAHA")
            elif setting == "allowmaths":
                if value.lower() == "true":
                    if document['expressionenabled']:
                        await ctx.reply(f"Maths is already allowed")
                        return
                    else:
                        document.update(expressionenabled=True)
                        document.save()
                        await ctx.reply(f"Maths is now functioning")
                elif value.lower() == "false":
                    if not document['expressionenabled']:
                        await ctx.reply(f"Maths is already not allowed")
                        return
                    else:
                        document.update(expressionenabled=False)
                        document.save()
                        await ctx.reply(f"Maths is now not functioning")
                else:
                    await ctx.reply(f"{value} wasn't valid, try again")
            elif setting == "allowwarn":
                if value.lower() == "true":
                    if document['allowedwarning']:
                        await ctx.reply(f"This channel is already allowed 1 warning")
                        return
                    else:
                        document.update(allowedwarning=True)
                        document.save()
                        await ctx.reply(f"Channel has been updated to allow 1 warning per streak")
                elif value.lower() == "no":
                    if not document['allowedwarning']:
                        await ctx.reply(f"The channel is already not allowed warnings")
                        return
                    else:
                        document.update(allowedwarning=False)
                        document.save()
                        await ctx.reply(f"The channel has been updated to not allow any warnings per streak")
                else:
                    await ctx.reply(f"{value} wasn't valid, try again")
            elif setting == "warnlimit":
                if value.isdigit():
                    if value == document['warningmax']:
                        await ctx.reply(f"The warning limit is already the same")
                        return
                    else:
                        document.update(warningmax=int(value))
                        document.save()
                        await ctx.reply(f"Warning limit has been set to {value}")
            elif setting == "setcurrent":
                if value.isdigit():
                    new_goal = int(value) + document['step']
                    document.update(goal_number=int(new_goal), streakrankability=False)
                    document.save()
                    await ctx.reply(f"{value} has been set. Next guess is {new_goal}")
                    await ctx.send(f"This streak is no longer rankable!")
                else:
                    await ctx.reply(f"{value} is not valid here, try a number")
            elif setting == "setstep":
                if value.isdigit():
                    oldcurrent = document['goal_number'] - document['step']
                    new_goal = int(value) + oldcurrent
                    document.update(goal_number=new_goal, step=int(value))
                    document.save()
                    await ctx.reply(f"{value} has been set. Next guess is {new_goal}")
                else:
                    await ctx.reply(f"{value} is not valid here, try a number")
            else:
                await ctx.reply(f"{setting} or {value} was not valid, try again.")
        except Exception as e:
            if FileNotFoundError:
                await ctx.reply(f"There is no document matching {channelid}")
                return
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
            formatted_time = await fortime()
            logger.info(f"{formatted_time}: countconfig -- {channelid}\n{e}")


async def setup(bot):
    await bot.add_cog(CountCog(bot))
