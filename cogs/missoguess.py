import discord
import asyncio
import refs.guildsinfo
from discord.ext import commands
from cogs.mondocs import MissOCollection, MissOHistory
from chodebot import logger, fortime, perm_check, PermError, ErrorMsgOwner, OWNERID, OWNERTAG, ignore_keys

# ToDo: Convert this to PSGuessing Game. Add RoninGT, Pious, Diane, DK, Etc. Side thought, make it work so depending
#  on the document loaded, and which "gametype" aka person we're guessing about, be the key for who we ignore for the
#  guessing and commands


class MissOCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        document = MissOCollection.objects.get(channel_id=message.channel.id)
        if message.guild.id != refs.guildsinfo.pettysqad_id:
            return
        if message.author.bot:
            return
        if message.content.startswith(ignore_keys, 0, 2):
            return
        if message.author.id in (refs.guildsinfo.spc_misso_id, message.author.id == int(OWNERID)):
            return
        usersperms = await perm_check(message, message.guild.id)
        if usersperms is None:
            print(f"MissOGuess Perm Check")
            await message.reply(PermError)
            return
        print(f"missolistener -- {message.author.name} -- {message.channel.id} --")

        if message.author.name == document['previous_author'] and not document['allowedmultguesses']:
            prev_author = message.author
            await message.delete()
            await message.channel.send(f"{prev_author.mention} You cannot submit 2 guesses in a row, wait for someone else to guess", delete_after=10)
            return
        document.update(previous_author=message.author.name)
        document.save()

    @commands.command()
    async def misso_guess(self, ctx, operator=None):
        """To start the Miss O Guessing Game: $misso_guess operator question_goes_here
        Operators are:
        start ( Only time question_goes_here is used )
        question ( Have the question repeated )"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            await ctx.reply(PermError)
            return
        if ctx.guild.id != refs.guildsinfo.pettysqad_id:
            psguild = self.bot.get_guild(refs.guildsinfo.pettysqad_id)
            await ctx.reply(f"This game is only available in {psguild.name}")
            return
        if operator is None:
            await ctx.reply(f"Operator is blank. Use $help misso_guess for more details")
        miss_o_collection = self.bot.channel_ids.get_collection('miss_o_collection')

        if operator == "start":
            if ctx.author.id != refs.guildsinfo.spc_misso_id:
                if ctx.author.id == int(OWNERID):
                    pass
                else:
                    return
            question = ctx.message.content.replace("$misso_guess start ", "")
            try:
                new_document = MissOCollection(channel_id=ctx.channel.id, channel_name=ctx.channel.name, guild_name=ctx.guild.name, question=question)
                new_document_dict = new_document.to_mongo()
                miss_o_collection.insert_one(new_document_dict)
                await ctx.reply(f"The game has started with:\n{question}")
            except Exception as e:
                if FileExistsError:
                    await ctx.reply(f"Y'all already got a game going on")
                else:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Something wen't wrong in the start operation -- {e}")
                    return
        elif operator == "question":
            try:
                document = MissOCollection.objects.get(channel_id=ctx.channel.id)
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"There is no Miss O Guessing game going on at thee moment")
                    return
                else:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Something wen't wrong in the display question command -- {e}")
                    return
            await ctx.reply(f"The Miss O Guessing game question is:\n{document['question']}")
        else:
            await ctx.reply(f"Something isn't valid, either operator({operator}) or the question isn't registering correct. Contact {OWNERTAG}")
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Something wen't wrong misso_guess operations")
            return

    @commands.command()
    async def misso_answer(self, ctx, author=None):
        """Miss O Only: To choose the correct guess  $misso_answer @author1|@author2|@author3"""
        if ctx.author.id != refs.guildsinfo.spc_misso_id:
            if ctx.author.id == int(OWNERID):
                pass
            else:
                return
        if author is None:
            await ctx.reply(f"Author is missing, try again")
            return

        def check(m):
            return m.author == ctx.author and ctx.message.content is not None
        miss_o_collection = self.bot.channel_ids.get_collection('miss_o_collection')
        miss_o_history = self.bot.channel_ids.get_collection('miss_o_history')
        try:
            document = MissOCollection.objects.get(channel_id=ctx.channel.id)
        except Exception as e:
            if FileNotFoundError:
                await ctx.reply(f"There isn't a game going yet")
                return
            else:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something wen't wrong choosing a answer misso special -- {e}")
                return

        await ctx.channel.send(f"What is thee answer?")
        try:
            answer = await self.bot.wait_for("message", check=check, timeout=300)
        except asyncio.TimeoutError:
            await ctx.reply(f"Ya took to long, try again :P")
            return
        embed = discord.Embed(title=f"Thee question was: {document['question']}", description=f"Thee answer was: {answer.content}", color=0xFC0F52)
        embed.add_field(name=f"Thee correct guesser(s):", value=author, inline=True)
        channel = self.bot.get_channel(ctx.channel.id)
        await channel.send(channel, embed=embed)
        new_document = MissOHistory(message_id=ctx.message.id, channel_name=ctx.channel.name, guild_name=ctx.guild.name,
                                    question=document['question'], correct_author=author, answer=answer.content)
        new_document_dict = new_document.to_mongo()
        miss_o_history.insert_one(new_document_dict)
        miss_o_collection.delete_one({"_id": ctx.channel.id})

    @commands.command()  # ToDo: Finish this crap. To list from the history collection, the question with answer and who guessed correct nice little embeded msg
    async def misso_list(self, ctx):
        await ctx.reply(f"To Be Done")
        return


async def setup(bot):
    await bot.add_cog(MissOCog(bot))
