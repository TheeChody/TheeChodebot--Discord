import random
# import asyncio
import discord
from discord.ext import commands
# from typing import Literal, Optional
from cogs.economy import add_points, remove_points
from cogs.mondocs import TriviaQuestions
from chodebot import logger, fortime, perm_check, PermError, ErrorMsgOwner, OWNERTAG, ignore_keys  #, guifo


class TriviaGame(commands.GroupCog, group_name="trivia-questions"):
    def __init__(self, bot):
        self.bot = bot

    async def new_game(self, message, status, skip=False):
        channelid = message.channel.id
        trivia_question_collection = self.bot.channel_ids.get_collection('trivia_questions')
        with open("refs/trivia_questions.txt", "r") as file:
            trivia_list = file.read()
            trivia_split = list(map(str, trivia_list.splitlines()))
        trivia_line = random.choice(trivia_split)
        try:
            trimmed_trivia_line = trivia_line.strip("[")
            trimmed_trivia_line = trimmed_trivia_line.strip("]")
            trivia_question, trivia_answer = trimmed_trivia_line.split('", ')
            trivia_question = trivia_question.replace('"', "")
            trivia_answer = trivia_answer.replace('"', "")
            trivia_answer = trivia_answer.lower()
            trivia_category = ""
            trivia_sub_category = ""
            trivia_topic = ""
            trivia_sub_topic = ""
            number_of_brackets = trivia_question.count(": ")
            embed = discord.Embed(title=f"Trivia Question", description="", color=0x0f0f0f)
            if number_of_brackets == 0:
                embed.add_field(name=f"Question:", value=trivia_question, inline=False)
            elif number_of_brackets == 1:
                trivia_category, trivia_question = trivia_question.split(": ")
                embed.add_field(name=f"Category/Topic:", value=trivia_category, inline=False)
                embed.add_field(name=f"Question:", value=trivia_question, inline=False)
            elif number_of_brackets == 2:
                trivia_category, trivia_topic, trivia_question = trivia_question.split(": ")
                embed.add_field(name=f"Category:", value=trivia_category, inline=False)
                embed.add_field(name=f"Topic:", value=trivia_topic, inline=False)
                embed.add_field(name=f"Question:", value=trivia_question, inline=False)
            elif number_of_brackets == 3:
                trivia_category, trivia_topic, trivia_sub_topic, trivia_question = trivia_question.split(": ")
                embed.add_field(name=f"Category:", value=trivia_category, inline=False)
                embed.add_field(name=f"Topic:", value=trivia_topic, inline=False)
                embed.add_field(name=f"Sub-Topic:", value=trivia_sub_topic, inline=False)
                embed.add_field(name=f"Question:", value=trivia_question, inline=False)
            elif number_of_brackets == 4:
                trivia_category, trivia_topic, trivia_sub_topic, trivia_sub_category, trivia_question = trivia_question.split(": ")
                embed.add_field(name=f"Category:", value=trivia_category, inline=False)
                embed.add_field(name=f"Sub-Category:", value=trivia_sub_category, inline=False)
                embed.add_field(name=f"Topic:", value=trivia_topic, inline=False)
                embed.add_field(name=f"Sub-Topic:", value=trivia_sub_topic, inline=False)
                embed.add_field(name=f"Question:", value=trivia_question, inline=False)
            if skip:
                document = TriviaQuestions.objects.get(channel_id=channelid)
                last_to_skip = message.author.name
                await message.channel.send(f"Thee answer to the skipped question was: {document['answer']}")
            else:
                last_to_skip = ""
            if status == "new":
                try:
                    new_document = TriviaQuestions(channel_id=channelid, channel_name=message.channel.name, guild_name=message.guild.name,
                                                   category=trivia_category, sub_category=trivia_sub_category, topic=trivia_topic,
                                                   sub_topic=trivia_sub_topic, question=trivia_question, answer=trivia_answer)
                    new_document_dict = new_document.to_mongo()
                    trivia_question_collection.insert_one(new_document_dict)
                except FileExistsError:
                    await message.reply(f"There is already a document matching {channelid}.")
                    return
            elif status == "restart":
                document = TriviaQuestions.objects.get(channel_id=channelid)
                document.update(channel_name=message.channel.name, guild_name=message.guild.name, category=trivia_category,
                                sub_category=trivia_sub_category, topic=trivia_topic, sub_topic=trivia_sub_topic, question=trivia_question,
                                answer=trivia_answer, previous_author="", lastguessed="", lasttoskip=last_to_skip, guessesmade=0, grandtotal=666, guessedlist="", guessedlist_nice="")
                document.save()
            elif status == "restart_testing":
                trivia_question_collection.delete_one({"_id": channelid})
                new_document = TriviaQuestions(channel_id=channelid, channel_name=message.channel.name, guild_name=message.guild.name,
                                               category=trivia_category, sub_category=trivia_sub_category, topic=trivia_topic,
                                               sub_topic=trivia_sub_topic, question=trivia_question, answer=trivia_answer)
                new_document_dict = new_document.to_mongo()
                trivia_question_collection.insert_one(new_document_dict)

            await message.channel.send(embed=embed)
            formatted_time = await fortime()
            logger.info(f"{formatted_time}: New Trivia Game Started in {channelid}.\nCat/topic/sub-topic/sub-category: {trivia_category, trivia_topic, trivia_sub_topic, trivia_sub_category}\nQuestion: {trivia_question} -- Answer: {trivia_answer}")
            return
        except Exception as e:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error starting trivia game in {channelid} -- {e} -- {trivia_line}")
            await message.channel.send(f"Try using $trivia skip or guess the last answer again, to get a new game.\n{ErrorMsgOwner.format(OWNERTAG, 'There was an error starting a new trivia game.')}")
            return

    @commands.Cog.listener()
    async def on_message(self, message):
        channelid = message.channel.id
        try:
            document = TriviaQuestions.objects.get(channel_id=channelid)
        except Exception as m:
            if FileNotFoundError:
                return
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error loading trivia document for {channelid} -- {m}")
                return
        if message.author.bot:
            return
        if message.content.startswith(ignore_keys, 0, 2):
            return
        # Check if user has perms to play
        usersperms = await perm_check(message, message.guild.id)
        if usersperms is None:
            await message.reply(PermError)
            return
        try:
            dead = False
            guess = message.content.lower()
            guess_stripped = guess.replace(" ", "")
            answer_stripped = document['answer'].replace(" ", "")
            if message.author == document['previous_author'] and not document['allowedmultguesses']:
                author = message.author
                await message.delete()
                await message.channel.send(f"{author.mention} you cannot guess twice in a row! You lost 10 points", silent=True, delete_after=15)
                await remove_points(self, message, message.author.id, 10, False)
                return
            elif guess_stripped in document['guessedlist'].split("|"):
                author = message.author
                content = message.content
                await message.delete()
                await message.channel.send(f"{author.mention} '{content}' has already been guessed, I know it's hard to keep track of, try again.", silent=True, delete_after=15)
                return
            elif guess_stripped == answer_stripped:
                guessed = f"{document['guessedlist_nice']}|{message.content.lower()}"
                guessedlist_nice = guessed.split("|")
                formatted_time = await fortime()
                logger.info(f"{formatted_time}: {message.author.name} got thee answer '{document['answer']}' from thee question '{document['question']}'. Only took {document['guessesmade']+1} to get it. Full list of guesses:\n'{', '.join(map(str, guessedlist_nice[1:]))}'")
                await message.reply(f"Congratz {message.author.mention} you got thee answer!!\nNew game incoming!!", silent=True)
                await self.new_game(message, "restart")
                await add_points(self, message, message.author.id, 150, False)
                return
            elif guess_stripped != answer_stripped:
                if document['guessesmade'] + 1 >= document['maxguessesmade']:
                    await message.add_reaction("☠️")
                    dead = True
                else:
                    await message.add_reaction("❎")
                    new_guessedlist = f"{document['guessedlist']}|{guess_stripped}"
                    new_guessesmade = document['guessesmade'] + 1
                    new_guessedlist_nice = f"{document['guessedlist_nice']}|{message.content.lower()}"
                    document.update(previous_author=message.author.name, guessedlist=new_guessedlist, guessedlist_nice=new_guessedlist_nice, guessesmade=new_guessesmade, lastguessed=message.content.lower())
                    document.save()
                    await remove_points(self, message, message.author.id, 10, False)
            if dead:
                formatted_time = await fortime()
                logger.info(f"{formatted_time}: Ran outta guesses in {message.channel.id}. Question was: '{document['question']}'. Answer was: '{document['answer']}'.\nGuesses made: '{document['guessedlist'].split('|')}'")
                guessed = f"{document['guessedlist_nice']}|{message.content.lower()}"
                guessedlist_nice = guessed.split("|")
                await message.channel.send(f"oof, y'all ran outta guesses. Thee answer was: {document['answer']}.\nGuesses made: '{', '.join(map(str, guessedlist_nice[1:]))}'. Try again\nNew game incoming!!")
                await self.new_game(message, "restart")
                await remove_points(self, message, message.author.id, 10, False)
                return
            else:
                document = TriviaQuestions.objects.get(channel_id=channelid)
                guesses_left = abs(document['guessesmade'] - document['maxguessesmade'])
                if guesses_left <= 5:
                    await message.channel.send(f"{guesses_left} guesses left")
        except Exception as e:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error within trivia game {e}")
            await message.channel.send(ErrorMsgOwner.format(OWNERTAG, "Error within trivia games, logged error background"))
            return

    @commands.command()
    async def trivia(self, ctx, operator=None):  #, value=None):
        """$trivia 'operator' 'value'
        :Operators:
        list
        alreadyguessed
        question
        skip
        :Values:
        true
        false"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            await ctx.reply(PermError)
            return
        channelid = ctx.channel.id
        try:
            document = TriviaQuestions.objects.get(channel_id=channelid)
        except Exception as e:
            if FileNotFoundError:
                await ctx.reply(f"There is not currently a game running")
                formatted_time = await fortime()
                logger.info(f"{formatted_time}: {ctx.author.name} tried accessing $trivia {operator} command in a channel with no trivia game running {channelid} -- {e}")
                return
            else:
                await ctx.reply(f"{ErrorMsgOwner.format(OWNERTAG, 'Error retrieving document for trivia game --', e)}")
                formatted_time = await fortime()
                logger.info(f"{formatted_time}: {ctx.author.name} tried accessing $trivia {operator} command in a channel with no trivia game running {channelid} -- {e}")
                return
        if operator is None:
            await ctx.reply(f"Operator is missing")
            return
        elif operator == "list":
            await ctx.reply(f"TBD")
            return
        elif operator == "alreadyguessed":
            embed = discord.Embed(title=f"Already Guessed List:", description="", color=0x0000FF)
            for word in document['guessedlist_nice']:
                try:
                    embed.add_field(name=word, value="", inline=False)
                except Exception as e:
                    await ctx.reply(f"Don't ya just hate in dev stuff? It errored out bud -- {e}")
                    break
            await ctx.reply(embed=embed)
        elif operator == "question":
            await ctx.reply(f"TBD")
            return
        elif operator == "skip":
            if ctx.author.name == document['lasttoskip']:
                await ctx.reply(f"You skipped thee last question, try this one or wait for someone else to skip it.")
                return
            else:
                await self.new_game(ctx, "restart", True)
                return
        else:
            await ctx.reply(f"{operator} isn't valid, try again")
            return

    # ToDo: FIX command to redisplay question. ^^^^^^^^^^ Tis Shit IS BROKE ^^^^^^^^^^
    @commands.command()
    async def trivia_config(self, ctx, operator=None, value=None):
        """Mod and Up Command
        $trivia_config 'operator' 'value'
        :Operators:
        start
        stop
        multguess
        :Values:
        true
        false"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin", "mod"):
            await ctx.reply(PermError)
            return
        channelid = ctx.channel.id
        trivia_question_collection = self.bot.channel_ids.get_collection('trivia_questions')
        if operator.lower() == "start":
            await self.new_game(ctx, "new")
        elif operator.lower() == "stop":
            try:
                if trivia_question_collection.find_one({"_id": channelid}):
                    trivia_question_collection.delete_one({"_id": channelid})
                    await ctx.reply(f"Old Document Deleted")
                elif FileNotFoundError:
                    await ctx.reply(f"There isn't a document yet matching {channelid}.")
                    return
            except Exception as e:
                await ctx.reply(f'something went wrong, either {channelid} or error msg ( {e} )')
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something went wrong removing document\n{channelid}: {e}")
            return
        elif operator.lower() == "multguess":
            if value.lower() == "true":
                await ctx.channel.send(f"Multi guesses is now allowed")
                return
            elif value.lower() == "false":
                await ctx.channel.send(f"Multi guesses is now not allowed")
                return
        else:
            await ctx.reply(f"{operator.lower()} was not valid, try again")
            return


async def setup(bot):
    await bot.add_cog(TriviaGame(bot))
