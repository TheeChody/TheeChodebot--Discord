from discord.ext import commands
from cogs.economy import add_points, remove_points
from cogs.mondocs import SentenceChannel, CountChannel
from chodebot import logger, fortime, perm_check, PermError, ErrorMsgOwner, OWNERTAG, ignore_keys


class SentenceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        channelid = message.channel.id
        try:
            document = SentenceChannel.objects.get(channel_id=channelid)
        except Exception as m:
            if FileNotFoundError:
                return
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error loading sentence document for {channelid} -- {m}")
                return
        if message.author.bot:
            return
        if message.content.startswith(ignore_keys, 0, 2):
            return
        usersperms = await perm_check(message, message.guild.id)
        if usersperms is None:
            await message.reply(PermError)
            return
        print(f"sentclistener -- {message.author.name} -- {channelid} --")
        msg = message.content
        try:
            if message.author.name == document['previous_author'] and not document['allowedmultinputs']:
                await remove_points(self, message, message.author.id, 10, False)
                prev_author = message.author
                await message.delete()
                await message.channel.send(f"{prev_author.mention} You cannot submit two words consecutively, you lost 10 points", silent=True, delete_after=10)
                return
            if len(message.content.split()) > 1:
                await remove_points(self, message, message.author.id, 10, False)
                prev_author = message.author
                await message.delete()
                await message.channel.send(f"{prev_author.mention} Only one word can be entered at a time, you lost 10 points", silent=True, delete_after=10)
                return
            if "." in msg and not document['allowedtoend']:
                prev_author = message.author
                msg = msg.replace(".", "")
                if msg == "":
                    await message.delete()
                    await message.channel.send(f"{prev_author.mention} You cannot just submit a '.', try again.", silent=True, delete_after=10)
                    return
            if "!" in msg and not document['allowedtoend']:
                prev_author = message.author
                msg = msg.replace("!", "")
                if msg == "":
                    await message.delete()
                    await message.channel.send(f"{prev_author.mention} You cannot just submit a '!', try again.", silent=True, delete_after=10)
                    return
            if "?" in msg and not document['allowedtoend']:
                prev_author = message.author
                msg = msg.replace("?", "")
                if msg == "":
                    await message.delete()
                    await message.channel.send(f"{prev_author.mention} You cannot just submit a '?', try again.", silent=True, delete_after=10)
                    return
            if message.content.startswith(" "):
                message.content = message.content.lstrip()
            if message.content.endswith(" "):
                message.content = message.content.rstrip()
            if len(message.content) > 35:
                prev_author = message.author
                await message.delete()
                await message.reply(f'{prev_author.mention} enter a word that is no longer than 35 characters.\nSometimes emojis :name_here: is rly long', silent=True, delete_after=10)
                return
            if message.content.isdigit():
                try:
                    iscountchanneltoo = CountChannel.objects.get(channel_id=channelid)
                except Exception as e:
                    if FileNotFoundError:
                        iscountchanneltoo = False
                        pass
                    else:
                        iscountchanneltoo = False
                        formatted_time = await fortime()
                        logger.error(f"{formatted_time}: Error with db file {e}")
                if iscountchanneltoo:
                    prev_author = message.author
                    await message.reply(f"{prev_author.mentino} When the a count game is going in this channel, you cannot use integers, try spelling the number instead", silent=True)
                    return
            currentsentence = document['sentence']
            new_word_count = document['word_count'] + 1
            if currentsentence == "":
                newword = f"{msg}"
            else:
                newword = f"{currentsentence} {msg}"
            document.update(previous_author=message.author.name, word_count=new_word_count, sentence=newword, channel_name=message.channel.name, guild_name=message.guild.name)
            document.save()
            await add_points(self, message, message.author.id, 5, False)
            if message.content.endswith('.') or message.content.endswith('!') or message.content.endswith('?'):
                if document['allowedtoend']:
                    document = SentenceChannel.objects.get(channel_id=channelid)
                    sentence = document['sentence']
                    await message.channel.send(f"The sentence is:\n{sentence}")
                    formatted_time = await fortime()
                    logger.info(f'{formatted_time}: Sentence Completed {message.guild.name} - {message.channel.name}\n-----------\n{sentence}\n-----------')
                    document.update(channel_name=message.channel.name, guild_name=message.guild.name, previous_author="", sentence="")
                    document.save()
        except Exception as e:
            if FileNotFoundError:
                await message.send(f"Something wen't wrong, maybe the DB isn't online? {e}")
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: File wasn't found, DB Online?? {e}")
                return
            else:
                await message.send(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something wrong happened!! {e}")

    @commands.command()
    async def sentence(self, ctx, operator):
        """Sets the channel for the Word Game
        The commands are:
        add
        remove
        list
        contents"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            await ctx.reply(PermError)
            return
        channelid = int(ctx.channel.id)
        sentence_channel_collection = self.bot.channel_ids.get_collection('sentence_channel')

        def check(m):
            return m.content.lower() == "yes" or "no" and m.channel.id == ctx.channel.id
        if operator == "add":
            if usersperms == "normal":
                await ctx.reply(PermError)
                return
            try:
                new_document = SentenceChannel(channel_id=channelid, channel_name=ctx.channel.name, guild_name=ctx.guild.name)
                new_document_dict = new_document.to_mongo()
                sentence_channel_collection.insert_one(new_document_dict)
                await ctx.reply(f"New document created")
            except Exception as e:
                if FileExistsError:
                    await ctx.reply(f"A document with {channelid} has been found, would you like to overwrite it?")
                    response = await self.bot.wait_for("message", check=check, timeout=60)
                    if response.content == "yes":
                        sentence_channel_collection.delete_one({"_id": channelid})
                        await ctx.reply(f"Old document deleted")
                        new_document = SentenceChannel(channel_id=channelid, channel_name=ctx.channel.name, guild_name=ctx.guild.name)
                        new_document_dict = new_document.to_mongo()
                        sentence_channel_collection.insert_one(new_document_dict)
                    elif response.content == "no":
                        await ctx.reply(f"Document NOT deleted")
                    else:
                        await ctx.reply(f"{response.content} is not valid, try again")
                else:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                    formatted_time = await fortime()
                    logger.error(f'{formatted_time}: Error creating document {channelid}\n{e}')
        elif operator == "remove":
            if usersperms == "normal":
                await ctx.reply(PermError)
                return
            try:
                if sentence_channel_collection.find_one({"_id": channelid}):
                    sentence_channel_collection.delete_one({"_id": channelid})
                    await ctx.reply(f"Old Document Deleted")
                elif FileNotFoundError:
                    await ctx.reply(f"There isn't a document yet matching {channelid}, would you like to create one?")
                    response = await self.bot.wait_for("message", check=check, timeout=60)
                    if response.content == "yes":
                        new_document = SentenceChannel(channel_id=channelid, channel_name=ctx.channel.name, guild_name=ctx.guild.name)
                        new_document_dict = new_document.to_mongo()
                        sentence_channel_collection.insert_one(new_document_dict)
                        await ctx.reply(f"New document created with {channelid}")
                    elif response.content == "no":
                        await ctx.reply(f"No document created")
                    else:
                        await ctx.reply(f"{response.content} is not valid, try again.")
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f'{formatted_time}: Error removing document {channelid}\n{e}')
        elif operator == "list":
            try:
                sentencedocuments = sentence_channel_collection.find({})
                sentencedocuments = sorted(sentencedocuments, key=lambda document: len(document['sentence'].split()), reverse=True)
                n = 1
                output = ""
                for document in sentencedocuments:
                    output += f"{n}: {document['guild_name']}: {len(document['sentence'].split())}\n"
                    n += 1
                await ctx.reply(f"List of channels playing Thee Never Ending Sentence Game:\n{output}")
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f'{formatted_time}: Error listing documents {channelid}\n{e}')
        elif operator == "contents" or operator == "content":
            try:
                document = SentenceChannel.objects.get(channel_id=channelid)
                await ctx.channel.send(f"Thee sentence is currently {len(document['sentence'].split(' '))} words long:")
                for i in range(0, len(document['sentence']), 2000):
                    await ctx.channel.send(document['sentence'][i:i+2000].lower())
            except Exception as e:
                if FileNotFoundError:
                    await ctx.reply(f"This channel is not registered in the collection")
                else:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error displaying contents of sentence for document['{channelid}']\n{e}")
        else:
            await ctx.reply(f"{operator} wasn't valid, try again")

    @commands.command()
    async def sentenceconfig(self, ctx, setting, value):
        """Performs Configuration Operations on This Channel
        Possible Operations are:
        multinput True/False
        allowtoend True/False"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms in ("normal", None):
            await ctx.reply(PermError)
            return
        channelid = int(ctx.channel.id)
        try:
            document = SentenceChannel.objects.get(channel_id=channelid)
            if setting == "multinput":
                if value.lower() == "true":
                    if document['allowedmultinputs']:
                        await ctx.reply(f"The channel is already accepting multiple inputs from same player")
                        return
                    else:
                        document.update(allowedmultinputs=True)
                        document.save()
                        await ctx.reply(f"Game now allows multiple inputs from same player")
                elif value.lower() == "false":
                    if not document['allowedmultinputs']:
                        await ctx.reply(f"The channel is already not accepting multiple inputs from same player")
                        return
                    else:
                        document.update(allowedmultinputs=False)
                        document.save()
                        await ctx.reply(f"Game now does not allow multiple inputs from the same player")
                else:
                    await ctx.reply(f"{value} is not valid here, try again.")
                    return
            elif setting == "allowtoend":
                if value.lower() == "true":
                    if document['allowedtoend']:
                        await ctx.reply(f"The game is already allowed to end")
                        return
                    else:
                        document.update(allowedtoend=True)
                        document.save()
                        await ctx.reply(f"The game is now allowed to end")
                elif value.lower() == "false":
                    if not document['allowedtoend']:
                        await ctx.reply(f"The game is already not allowed to end")
                        return
                    else:
                        document.update(allowedtoend=False)
                        document.save()
                        await ctx.reply(f"The game is now not allowed to end")
            else:
                await ctx.reply(f"{setting} or {value} was not valid, try again")
        except Exception as e:
            if FileNotFoundError:
                await ctx.reply(f"There is no document matching {channelid}")
                return
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
            formatted_time = await fortime()
            logger.error(f'{formatted_time}: Error sentenceconfig {channelid}\n{e}')


async def setup(bot):
    await bot.add_cog(SentenceCog(bot))
