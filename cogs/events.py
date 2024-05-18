import re
import discord
from discord.ext import commands
from cogs.economy import add_points
from cogs.mondocs import ReactionRoles, ReactionMessages, CountChannel, GuessChannel, TriviaQuestions
from chodebot import fortime, logger, keyds, reans, guifo, perm_check, OwnPermError, OWNERID, ErrorMsgOwner, OWNERTAG, ignore_keys, rannumb_comparasion, ranword_comparasion


class CustEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def count_embed(document, message):
        try:
            embed = None
            if len(message.content.split(" ")) > 1:
                messagenumber = ""
                for char in message.content:
                    if char.isdigit():
                        messagenumber += char
                    if char.isalpha():
                        break
                print(messagenumber, '-', 000000000000)
                if messagenumber == "":
                    pass
                elif int(messagenumber) == document['goal_number'] - document['step']:
                    embed = discord.Embed(
                        title=f"{message.author} deleted thee last count, it was {document['goal_number'] - document['step']}",
                        description=f"Thee next probable number is {document['goal_number']}. Check with $count lastguess , to be certain if you're in doubt",
                        color=0xFF0000)
                    embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
                else:
                    embed = discord.Embed(title=f"{message.author} deleted a guess {messagenumber}",
                                          description=f"The next probable number is {document['goal_number']}. Check with $count lastguess , that will show the last valid guess.",
                                          color=0xFF0000)
                    embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
            else:
                if message.content.isdigit():
                    embed = discord.Embed(title=f"{message.author} deleted a guess {message.content}",
                                          description=f"The next probable number is {document['goal_number']}. Check with $count lastguess , that will show the last valid guess.",
                                          color=0xFF0000)
                    embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
            embed_logger = discord.Embed(title=f"{message.author} deleted a message", description=f"{message.guild.name} - {message.channel.name}", color=0x005270)
            embed_logger.add_field(name=message.content, value="", inline=False)
            return embed, embed_logger
        except Exception as e:
            print(e)
            return None, None

    async def create_embed(self, spc_channel, message=None, message_before=None, message_after=None):
        try:
            if spc_channel is None:
                channel_object = None
            elif spc_channel == "count":
                channel_object = CountChannel
            elif spc_channel == "guess":
                channel_object = GuessChannel
            else:
                print(f"Something wrong -- Create_Embed -- spc_channel is:: {spc_channel}")
                return False
            try:
                if channel_object is None:
                    document = None
                else:
                    document = channel_object.objects.get(channel_id=message.channel.id)
            except Exception as f:
                print(f)
                return False
            if message is not None and document is not None:
                if spc_channel == "count":
                    embed, embed_logger = self.count_embed(document, message)
                    if embed is None or embed_logger is None:
                        print(f"Either Embed or Embed Logger is None\nEmbed:: {embed}\nEmbedLogger:: {embed_logger}")
                else:
                    return False
            else:
                return False
            if embed is not None:
                channel = self.bot.get_channel(message.channel.id)
                await channel.send(channel, embed=embed)
            if embed_logger is not None:
                channel_logger = self.bot.get_channel(guifo.spc_game_logger)
                await channel_logger.send(channel_logger, embed=embed_logger)
            return True
        except Exception as e:
            print(e)
            return False

    @commands.Cog.listener()  # ToDo: Add id'er to sentence(Not just sentence game, like everytime we have thee bot delete msgs due to mult input)
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        try:
            # spc_channel = None  # ..........when done
            if message.author.id in guifo.spc_delete:
                channel = self.bot.get_channel(guifo.chroniclers_logsspec)
                spc_case = self.bot.get_user(message.author.id)
                embed = discord.Embed(title=f"{spc_case.name} deleted a message in {message.guild.name}",
                                      description=f"{message.channel.name}", color=0xFF0000)
                embed.add_field(name=message.content, value="")
                await channel.send(channel, embed=embed)
            if message.channel.id in guifo.spc_count_channels:
                # Attempting to create new more robust create_embed format to be used for both delete, edit and post--2-when-dones
                spc_channel = "count"
                successful_count = await self.create_embed(spc_channel, message)  # Put this at thee bottom before guild checks..........when done
                if not successful_count:
                    document = CountChannel.objects.get(channel_id=message.channel.id)
                    channel = self.bot.get_channel(message.channel.id)
                    if len(message.content.split(" ")) > 1:
                        messagenumber = ""
                        for char in message.content:
                            if char.isdigit():
                                messagenumber += char
                            if char.isalpha():
                                break
                        print(messagenumber, '-', 000000000000)
                        if messagenumber == "":
                            pass
                        elif int(messagenumber) == document['goal_number'] - document['step']:
                            embed = discord.Embed(title=f"{message.author} deleted thee last count, it was {document['goal_number'] - document['step']}",
                                                  description=f"Thee next probable number is {document['goal_number']}. Check with $count lastguess , to be certain if you're in doubt",
                                                  color=0xFF0000)
                            embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
                            await channel.send(channel, embed=embed)
                        else:
                            embed = discord.Embed(title=f"{message.author} deleted a guess {messagenumber}",
                                                  description=f"The next probable number is {document['goal_number']}. Check with $count lastguess , that will show the last valid guess.",
                                                  color=0xFF0000)
                            embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
                            await channel.send(channel, embed=embed)
                    else:
                        if message.content.isdigit():
                            embed = discord.Embed(title=f"{message.author} deleted a guess {message.content}",
                                                  description=f"The next probable number is {document['goal_number']}. Check with $count lastguess , that will show the last valid guess.",
                                                  color=0xFF0000)
                            embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
                            await channel.send(channel, embed=embed)
                    channel = self.bot.get_channel(guifo.spc_game_logger)
                    embed = discord.Embed(title=f"{message.author} deleted a message",
                                          description=f"{message.guild.name} - {message.channel.name}", color=0x005270)
                    embed.add_field(name=message.content, value="", inline=False)
                    await channel.send(channel, embed=embed)
            elif message.channel.id in guifo.spc_guess_channels:
                document = GuessChannel.objects.get(channel_id=message.channel.id)
                channel = self.bot.get_channel(message.channel.id)
                if document['gametype'] == "randomnumber":
                    if len(message.content.split(" ")) > 1:
                        messagenumber = ""
                        for char in message.content:
                            if char.isdigit():
                                messagenumber += char
                            if char.isalpha():
                                break
                        if not messagenumber.isdigit():
                            pass
                        elif int(messagenumber) != document['lastguessed']:
                            pass
                        else:
                            embed = discord.Embed(title=f"{message.author} deleted a guess {messagenumber}",
                                                  description="", color=0x0FC9FC)
                            if document['guessesbetweenhints'] == 0:
                                field = await rannumb_comparasion(document)
                                if field is None:
                                    field = f"{ErrorMsgOwner.format(OWNERTAG, 'Something went wrong in a rannum_comp')}"
                                embed.add_field(name=field, value="", inline=False)
                                embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
                            await channel.send(channel, embed=embed)
                    elif message.content.isdigit() and int(message.content) != document['lastguessed']:
                        return
                    else:
                        # print(f"else")
                        if message.content.isdigit():
                            embed = discord.Embed(title=f"{message.author} deleted a guess {message.content}",
                                                  description="", color=0x0FC9FC)
                            if document['guessesbetweenhints'] == 0:
                                field = await rannumb_comparasion(document)
                                if field is None:
                                    field = f"{ErrorMsgOwner.format(OWNERTAG, 'Something went wrong in a rannum_comp')}"
                                embed.add_field(name=field, value="", inline=False)
                                embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
                            await channel.send(channel, embed=embed)
                    channel = self.bot.get_channel(guifo.spc_game_logger)
                    embed = discord.Embed(title=f"{message.author} deleted a message",
                                          description=f"{message.guild.name} - {message.channel.name}", color=0x0FC9FC)
                    embed.add_field(name=message.content, value="", inline=False)
                    if document['guessesbetweenhints'] == 0:
                        field = await rannumb_comparasion(document)
                        if field is None:
                            field = f"{ErrorMsgOwner.format(OWNERTAG, 'Something went wrong in a rannum_comp')}"
                        embed.add_field(name=field, value="", inline=False)
                        embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
                    await channel.send(channel, embed=embed)
                elif document['gametype'] == "randomword":
                    if len(message.content.split(" ")) > 1:
                        guess_text = message.content.split(" ")[0]
                        embed = discord.Embed(title=f"{message.author} deleted a guess '{guess_text}'", description="",
                                              color=0x0FC9FC)
                        if guess_text == document['lastguessed']:
                            if document['guessesbetweenhints'] >= 0:
                                correct_position, correct_letter, wrong_letter = await ranword_comparasion(guess_text,
                                                                                                           document)
                                embed.add_field(
                                    name=f"{correct_position} in thee right spot\n{correct_letter} correct but in thee wrong spot\n{wrong_letter} is just not even in the answer",
                                    value="There may be missing letters though", inline=False)
                        await channel.send(channel, embed=embed)
                    else:
                        embed = discord.Embed(title=f"{message.author} deleted a guess '{message.content}'",
                                              description="", color=0x0FC9FC)
                        if message.content == document['lastguessed']:
                            if document['guessesbetweenhints'] >= 0:
                                correct_position, correct_letter, wrong_letter = await ranword_comparasion(
                                    message.content, document)
                                embed.add_field(
                                    name=f"{correct_position} in thee right spot\n{correct_letter} correct but in thee wrong spot\n{wrong_letter} is just not even in the answer",
                                    value="There may be missing letters though", inline=False)
                        await channel.send(channel, embed=embed)
                    channel = self.bot.get_channel(guifo.spc_game_logger)
                    embed = discord.Embed(title=f"{message.author} deleted a message",
                                          description=f"{message.guild.name} - {message.channel.name}", color=0x0FC9FC)
                    embed.add_field(name=message.content, value="", inline=False)
                    if document['guessesbetweenhints'] >= 0:
                        correct_position, correct_letter, wrong_letter = await ranword_comparasion(message.content,
                                                                                                   document)
                        embed.add_field(
                            name=f"{correct_position} in thee right spot\n{correct_letter} correct but in thee wrong spot\n{wrong_letter} is just not even in the answer",
                            value="There may be missing letters though", inline=False)
                    await channel.send(channel, embed=embed)
            elif message.channel.id in guifo.spc_triv_channels:  # Starting to think I really don't need an on_delete for triv, just edit
                try:
                    document = TriviaQuestions.objects.get(channel_id=message.channel.id)
                except FileNotFoundError:
                    document = None
                    pass
                message_squashed = message.content.replace(" ", "")
                # print(message_squashed, document['guessedlist'], type(message_squashed), type(document['guessedlist']))
                if message_squashed not in document['guessedlist']:
                    # print("made it delete triv")
                    channel = self.bot.get_channel(message.channel.id)
                    embed = discord.Embed(title=f"{message.author} deleted a message",
                                          description=message.content, color=0x0FC9FC)
                    await channel.send(channel, embed=embed)
                    channel = self.bot.get_channel(guifo.spc_game_logger)
                    embed = discord.Embed(title=f"{message.author} deleted a message",
                                          description=f"{message.guild.name, '-', message.channel.name}", color=0x005270)
                    embed.add_field(name=message.content, value="", inline=False)
                    await channel.send(channel, embed=embed)
            if message.channel.id in (guifo.chodeling_count, guifo.chodeling_guess, guifo.chodeling_triv, guifo.chodeling_hangman):
                return
            elif message.guild.id == guifo.chodeling_id:
                channel = self.bot.get_channel(guifo.chodeling_logs)
            elif message.guild.id == guifo.chroniclers_id:
                return
            elif message.guild.id == guifo.cemetery_id:
                channel = self.bot.get_channel(guifo.cemetery_logs)
            elif message.guild.id == guifo.pettysqad_id:
                return
            elif message.guild.id == guifo.queenpalace_id:
                channel = self.bot.get_channel(guifo.queenpalace_logs)
            elif message.guild.id == guifo.mellowzone_id:
                return
            elif message.guild.id == guifo.catino_id:
                channel = self.bot.get_channel(guifo.catino_logs)
            else:
                return
            embed = discord.Embed(title=f"{message.author} deleted a message", description=message.channel.name,
                                  color=0xFF0000)
            embed.add_field(name=message.content, value="", inline=False)
            await channel.send(channel, embed=embed)
        except Exception as e:
            if FileNotFoundError:
                pass
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Something went wrong on_message_delete. {message.guild.name}({message.channel.name}): {message.author.name}: {message.content}\n{e}")

    @commands.Cog.listener()  # ToDo: Figure out why the adding/removing embeded links is triggering an edit log
    async def on_message_edit(self, message_before, message_after):
        if message_after.author.bot:
            return
        try:
            if message_before.author.id in guifo.spc_edit:  # Spc Cases Tracker
                channel = self.bot.get_channel(guifo.chroniclers_logsspec)
                spc_case = self.bot.get_user(message_before.author.id)
                embed = discord.Embed(title=f"{spc_case.name} edited a message in {message_after.guild.name}",
                                      description=f"{message_after.channel.name}", color=0x0000FF)
                embed.add_field(name=f"Before Edit", value=message_before.content, inline=False)
                embed.add_field(name=f"After Edit", value=message_after.content, inline=False)
                await channel.send(channel, embed=embed)
            if message_after.channel.id in (guifo.spc_count_channels, guifo.spc_priv_channels):
                document = CountChannel.objects.get(channel_id=message_after.channel.id)
                channel = self.bot.get_channel(message_after.channel.id)
                beforemessagenumber = ""
                for char in message_before.content:
                    if char.isdigit():
                        beforemessagenumber += char
                    if char.isalpha():
                        break
                aftermessagenumber = ""
                for char in message_after.content:
                    if char.isdigit():
                        aftermessagenumber += char
                    if char.isalpha():
                        break
                if beforemessagenumber == "" and aftermessagenumber == "":
                    pass
                elif int(beforemessagenumber) != int(aftermessagenumber):
                    embed = discord.Embed(title=f"{message_after.author} edited a guess.",
                                          description=f"The next probable number is {document['goal_number']}.\nCheck with $count lastguess , that will show the last valid guess.",
                                          color=0xFF0000)
                    embed.add_field(name="Before Edit", value=beforemessagenumber, inline=False)
                    embed.add_field(name="After Edit", value=aftermessagenumber, inline=False)
                    embed.add_field(name=f"If you are unsure,", value=f"contact {OWNERTAG}")
                    await channel.send(channel, embed=embed)
                elif int(beforemessagenumber) == int(aftermessagenumber):
                    pass
                else:
                    await channel.send(
                        f"'{message_after.author}' edited a message from '{beforemessagenumber}' to '{aftermessagenumber}' . {OWNERTAG}")
                channel = self.bot.get_channel(guifo.spc_game_logger)  # My Log Channel
                embed = discord.Embed(title=f"{message_after.author} edited a message",
                                      description=f"{message_after.guild.name} - {message_after.channel.name}",
                                      color=0x005270)
                embed.add_field(name="Before Edit", value=message_before.content, inline=False)
                embed.add_field(name="After Edit", value=message_after.content, inline=False)
                await channel.send(channel, embed=embed)
            elif message_after.channel.id in (guifo.spc_guess_channels, guifo.spc_priv_channels):
                document = GuessChannel.objects.get(channel_id=message_after.channel.id)
                channel = self.bot.get_channel(message_after.channel.id)
                if document['gametype'] == "randomnumber":
                    beforemessagenumber = ""
                    for char in message_before.content:
                        if char.isdigit():
                            beforemessagenumber += char
                        if char.isalpha():
                            break
                    aftermessagenumber = ""
                    for char in message_after.content:
                        if char.isdigit():
                            aftermessagenumber += char
                        if char.isalpha():
                            break
                    if beforemessagenumber == "" and aftermessagenumber == "":
                        pass
                    elif int(beforemessagenumber) != int(aftermessagenumber):
                        embed = discord.Embed(title=f"{message_after.author} edited a guess.", description="",
                                              color=0x0FC9FC)
                        embed.add_field(name="Before Edit", value=beforemessagenumber, inline=False)
                        embed.add_field(name="After Edit", value=aftermessagenumber, inline=False)
                        if document['guessesbetweenhints'] >= 0:
                            field = await rannumb_comparasion(document)
                            if field is None:
                                field = f"{ErrorMsgOwner.format(OWNERTAG, 'Something went wrong in a rannum_comp')}"
                            embed.add_field(name=field, value="", inline=False)
                            embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
                        await channel.send(channel, embed=embed)
                    elif int(beforemessagenumber) == int(aftermessagenumber):
                        pass
                    else:
                        await channel.send(
                            f"'{message_after.author}' edited a message from '{beforemessagenumber}' to '{aftermessagenumber}' . {OWNERTAG}")
                    channel = self.bot.get_channel(guifo.spc_game_logger)
                    embed = discord.Embed(title=f"{message_after.author} edited a message",
                                          description=f"{message_after.guild.name} - {message_after.channel.name}",
                                          color=0x0FC9FC)
                    embed.add_field(name="Before Edit", value=message_before.content, inline=False)
                    embed.add_field(name="After Edit", value=message_after.content, inline=False)
                    if document['guessesbetweenhints'] >= 0:
                        field = await rannumb_comparasion(document)
                        if field is None:
                            field = f"{ErrorMsgOwner.format(OWNERTAG, 'Something went wrong in a rannum_comp')}"
                        embed.add_field(name=field, value="", inline=False)
                        embed.add_field(name=f"If you're unsure", value=f"contact {OWNERTAG}", inline=False)
                    await channel.send(channel, embed=embed)
                elif document['gametype'] == "randomword":
                    if len(message_before.content.split()) > 1:
                        guess_before = message_before.content.split()[0]
                    else:
                        guess_before = message_before.content
                    if len(message_after.content.split()) > 1:
                        guess_after = message_after.content.split()[0]
                    else:
                        guess_after = message_after.content
                    if guess_before == guess_after:
                        pass
                    else:
                        embed = discord.Embed(title=f"{message_after.author} edited a guess.", description="",
                                              color=0x0FC9FC)
                        embed.add_field(name="Before Edit", value=guess_before, inline=False)
                        embed.add_field(name="After Edit", value=guess_after, inline=False)
                        if document['guessesbetweenhints'] >= 0:
                            correct_position, correct_letter, wrong_letter = await ranword_comparasion(guess_before,
                                                                                                       document)
                            embed.add_field(
                                name=f"{correct_position} in thee right spot\n{correct_letter} correct but in thee wrong spot\n{wrong_letter} is just not even in the answer",
                                value="There may be missing letters though", inline=False)
                        await channel.send(channel, embed=embed)
                    channel = self.bot.get_channel(guifo.spc_game_logger)
                    embed = discord.Embed(title=f"{message_after.author} edited a guess.", description="",
                                          color=0x0FC9FC)
                    embed.add_field(name="Before Edit", value=message_before.content, inline=False)
                    embed.add_field(name="After Edit", value=message_after.content, inline=False)
                    if document['guessesbetweenhints'] >= 0:
                        correct_position, correct_letter, wrong_letter = await ranword_comparasion(guess_before,
                                                                                                   document)
                        embed.add_field(
                            name=f"{correct_position} in thee right spot\n{correct_letter} correct but in thee wrong spot\n{wrong_letter} is just not even in the answer",
                            value="There may be missing letters though", inline=False)
                    await channel.send(channel, embed=embed)
            elif message_after.channel.id in guifo.spc_triv_channels:
                if message_before.content.startswith(ignore_keys):
                    pass
                else:
                    channel = self.bot.get_channel(message_after.channel.id)
                    embed = discord.Embed(title=f"{message_after.author} edited a message",
                                          description=f"",
                                          color=0x0FC9FC)
                    embed.add_field(name=f"Before Edit:", value=message_before.content, inline=False)
                    embed.add_field(name=f"After Edit:", value=message_after.content, inline=False)
                    await channel.send(channel, embed=embed)
                    channel = self.bot.get_channel(guifo.spc_game_logger)
                    embed = discord.Embed(title=f"{message_before.author} deleted a message",
                                          description=f"{message_before.guild.name, '-', message_before.channel.name}",
                                          color=0x005270)
                    embed.add_field(name=f"Before Edit:", value=message_before.content, inline=False)
                    embed.add_field(name=f"After Edit:", value=message_after.content, inline=False)
                    await channel.send(channel, embed=embed)
            if message_after.channel.id in (guifo.chodeling_count, guifo.chodeling_guess, guifo.spc_priv_channels):
                return
            elif message_after.guild.id == guifo.chodeling_id:
                channel = self.bot.get_channel(guifo.chodeling_logs)
            elif message_after.guild.id == guifo.chroniclers_id:
                return
            elif message_after.guild.id == guifo.cemetery_id:
                channel = self.bot.get_channel(guifo.cemetery_logs)
            elif message_after.guild.id == guifo.pettysqad_id:
                return
            elif message_after.guild.id == guifo.queenpalace_id:
                channel = self.bot.get_channel(guifo.queenpalace_logs)
            elif message_after.guild.id == guifo.mellowzone_id:
                return
            elif message_after.guild.id == guifo.catino_id:
                channel = self.bot.get_channel(guifo.catino_logs)
            else:
                return
            embed = discord.Embed(title=f"{message_before.author} edited a message",
                                  description=message_before.channel.name, color=0x8A5000)
            embed.add_field(name="Before Edit", value=message_before.content, inline=False)
            embed.add_field(name="After Edit", value=message_after.content, inline=False)
            await channel.send(channel, embed=embed)
        except Exception as e:
            formatted_time = await fortime()
            logger.error(
                f"{formatted_time}: Something went wrong on_message_edit. '{message_after.guild.name}'({message_after.channel.name}): '{message_after.author.name}'\n'{message_before.content}' vs '{message_after.content}'\n{e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        channelid = message.channel.id
        if message.content.startswith(ignore_keys, 0, 2):
            return
        if message.guild.id == guifo.pettysqad_id:
            print(f"psentlistener -- {message.author.name} -- {message.channel.id}")
            if message.channel.id == guifo.pettysqad_rantrave:
                if message.author.bot:
                    pass
                else:
                    message_content = message.content
                    message_author = message.author
                    await message.delete()
                    formatted_time = await fortime()
                    logger.info(f"{formatted_time}: {message_author.name} posted a message in Rant_Rave\n{message_content}")
                    return
            elif message.channel.id in guifo.spc_petty_sug_group:
                if message.author.bot:
                    pass
                print(f"pssugelistener -- {message.author.name} -- {message.channel.id} --")
                usersperms = await perm_check(message, message.guild.id)
                if usersperms in ("owner", "admin", "mod"):
                    return
                reaction_messages = self.bot.channel_ids.get_collection('reaction_messages')
                repost_message = message
                repost_user = message.author
                await message.delete()
                await message.channel.send(f"{repost_user.mention} Your message has been redirected to thee mods for link approval. I will repost your message if/when it is approved.", silent=True)
                channel = self.bot.get_channel(guifo.pettysqad_suggested_zone)
                embed = discord.Embed(title=f"{repost_user.display_name} posted a suggestion in {repost_message.channel.name}", description=f"{repost_message.content}", color=0x00ff00)
                message_sent = await channel.send(embed=embed)
                new_document = ReactionMessages(message_id=message_sent.id, thread_id=repost_message.channel.id, thread_name=repost_message.channel.name,
                                                guild_name=repost_message.guild.name, author_id=repost_user.id, author_name=repost_user.name,
                                                author_display_name=repost_user.display_name, message_content=repost_message.content, reaction_type="suggested_zone")
                new_document_dict = new_document.to_mongo()
                reaction_messages.insert_one(new_document_dict)
                await message_sent.add_reaction("👍")
                await message_sent.add_reaction("👎")
                return
            elif message.channel.id == guifo.pettysqad_selfpromo:
                await message.add_reaction("🍎")
                return
            elif message.channel.id == guifo.pettysqad_live_updates and message.author.bot:
                await message.add_reaction("🍎")
                return
            elif message.channel.id == guifo.pettysqad_system and message.author.bot:
                if message.content.startswith("Hey"):
                    await message.add_reaction("👋")
                elif message.content.startswith("GG"):
                    await message.add_reaction("👏")
                return
            elif message.channel.id == guifo.pettysqad_birthday and message.author.bot:
                if message.content.startswith("It's the birthday of"):
                    await message.add_reaction("🎂")
                    return
        elif message.guild.id == guifo.cemetery_id:
            if message.channel.id == guifo.cemetery_welc and message.author.bot:
                if message.content.startswith("Hey"):
                    await message.add_reaction("👋")
                elif message.content.startswith("GG"):
                    await message.add_reaction("👏")
                return
        if message.author.bot:
            return
        print(f"eventlistener -- {message.author.name} -- {message.channel.id} --")  # {message.content} --")
        if message.author.id in guifo.spc_post:  # in (guifo.spc_mantis_id):  #, guifo.spc_commandac_id):
            channel = self.bot.get_channel(guifo.chroniclers_logsspec)
            spc_case = self.bot.get_user(message.author.id)
            embed = discord.Embed(title=f"{spc_case.name} wrote a message in {message.guild.name}",
                                  description=f"{message.channel.name}", color=0x083600)
            embed.add_field(name=message.content, value="")
            await channel.send(channel, embed=embed)
        if channelid in guifo.spc_ign_group:
            return
        await add_points(self, message, message.author.id, 1, False)
        if message.guild.id == guifo.chodeling_id:
            keywords = keyds.chodeling_keywords
        elif message.guild.id == guifo.cemetery_id:
            keywords = keyds.joes_keywords
        elif message.guild.id == guifo.chroniclers_id:
            keywords = keyds.xboxs_keywords
        elif message.guild.id == guifo.mellowzone_id:
            keywords = keyds.mellow_keywords
        elif message.guild.id == guifo.queenpalace_id:
            keywords = keyds.queenpalace_keywords
        elif message.guild.id == guifo.pettysqad_id:
            keywords = keyds.petty_keywords
        elif message.guild.id == guifo.catino_id:
            keywords = keyds.catino_keywords
        else:
            return

        messagecont = message.content.lower()
        for keyword, properties in keyds.global_keywords.items():
            if re.search(keyword, messagecont):
                response = await message.reply(properties["response"].format(message.author.display_name))
                if properties["emoji"]:
                    await response.add_reaction(properties["emoji"])
                if properties["emoji2"]:
                    await response.add_reaction(properties["emoji2"])
        for keyword, properties in keywords.items():
            if re.search(keyword, messagecont):
                response = await message.reply(properties["response"].format(message.author.display_name))
                if properties["emoji"]:
                    await response.add_reaction(properties["emoji"])
                if properties["emoji2"]:
                    await response.add_reaction(properties["emoji2"])

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == guifo.chodeling_id:
            color = 0x006900
            welctitle = guifo.msg_chodeling_welc
            normalrole = member.guild.get_role(guifo.chodeling_norm)
            channel = self.bot.get_channel(guifo.chodeling_welc)
        elif member.guild.id == guifo.fire_floozie_id:
            color = 0xFF0000
            welctitle = guifo.msg_fire_floozie_welc
            normalrole = member.guild.get_role(guifo.fire_floozie_norm)
            channel = self.bot.get_channel(guifo.fire_floozie_welc)
        elif member.guild.id == guifo.dark_lair_id:
            color = 0x199832
            welctitle = guifo.msg_darklair_welc
            normalrole = member.guild.get_role(guifo.dark_lair_norm)
            channel = self.bot.get_channel(guifo.dark_lair_welc)
        elif member.guild.id == guifo.queenpalace_id:
            color = 0xD40CEE
            welctitle = guifo.msg_queenpalace_welc
            normalrole = member.guild.get_role(guifo.queenpalace_norm)
            channel = self.bot.get_channel(guifo.queenpalace_welc)
        else:
            return
        try:
            emb = discord.Embed(title=welctitle, description=f"{normalrole.mention}'s welcome in {member.display_name}!!", color=color)
            welcmsg = await channel.send(embed=emb, silent=True)
            await welcmsg.add_reaction("👋")
        except Exception as e:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: on_member_join -- {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == guifo.chodeling_id:
            channel = self.bot.get_channel(guifo.chodeling_logs)
        elif member.guild.id == guifo.cemetery_id:
            channel = self.bot.get_channel(guifo.cemetery_logs)
        elif member.guild.id == guifo.queenpalace_id:
            channel = self.bot.get_channel(guifo.queenpalace_logs)
        elif member.guild.id == guifo.fire_floozie_id:
            channel = self.bot.get_channel(guifo.fire_floozie_logs)
        elif member.guild.id == guifo.dark_lair_id:
            channel = self.bot.get_channel(guifo.dark_lair_logs)
        else:
            return
        try:
            departmsg = await channel.send(f"{member} has left {member.guild.name}")
            await departmsg.add_reaction("🤝")
        except Exception as e:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: on_member_leave -- {e} -- {member.guild.name} -- {member}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        print(f"onrealistener -- {payload.member.name} -- {payload.message_id} -- {payload.emoji.name}")
        try:
            document = ReactionRoles.objects.get(message_id=payload.message_id)
        except Exception as e:
            if FileNotFoundError:
                try:
                    document = ReactionMessages.objects.get(message_id=payload.message_id)
                except Exception as ee:
                    if FileNotFoundError:
                        return
                    else:
                        formatted_time = await fortime()
                        logger.error(f"{formatted_time}: on_raw_reaction_add ee -- {ee}")
                    return
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: on_raw_raction_add -- {e}")
                return
        if document['reaction_type'] == "suggested_zone":
            pass
        else:
            emojistocheck = document['reaction_emojis']
            if payload.emoji.name not in emojistocheck.split("|"):
                return
        if payload.guild_id == guifo.pettysqad_id:
            if document['reaction_type'] == "suggested_zone":
                reaction_messages = self.bot.channel_ids.get_collection('reaction_messages')
                if str(payload.emoji) == document['yes_emoji']:
                    channel = self.bot.get_channel(document['thread_id'])
                    embed = discord.Embed(title=f"{document['author_display_name']} sent a suggestion", description=f"{document['message_content']}", color=0x0000ff)
                    await channel.send(embed=embed)
                    reaction_messages.delete_one({"_id": document['message_id']})
                elif str(payload.emoji) == document['no_emoji']:
                    reaction_messages_rejected = self.bot.channel_ids.get_collection('reaction_messages_rejected')
                    new_document = ReactionMessages(message_id=document['message_id'], thread_id=document['thread_id'], thread_name=document['thread_name'],
                                                    guild_name=document['guild_name'], author_id=document['author_id'], author_name=document['author_name'],
                                                    author_display_name=document['author_display_name'], message_content=document['message_content'], reaction_type=document['reaction_type'])
                    new_document_dict = new_document.to_mongo()
                    reaction_messages_rejected.insert_one(new_document_dict)
                    reaction_messages.delete_one({"_id": document['message_id']})
            return
        elif payload.guild_id == guifo.chodeling_id:
            if document['reaction_type'] == "test":
                emoji_name = reans.test_reaction_roles.get(payload.emoji.name)
            elif document['reaction_type'] == "welcome":
                emoji_name = reans.welcome_roles_chodeling.get(payload.emoji.name)
            elif document['reaction_type'] == "reactroles":
                emoji_name = reans.react_for_roles_chodeling.get(payload.emoji.name)
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error finding emoji_name -- ")
                return
        elif payload.guild_id == guifo.cemetery_id:
            if document['reaction_type'] == "test":
                emoji_name = reans.test_reaction_roles.get(payload.emoji.name)
            elif document['reaction_type'] == "welcome":
                emoji_name = reans.welcome_roles_cemetery.get(payload.emoji.name)
            elif document['reaction_type'] == "reactroles":
                emoji_name = reans.react_for_roles_cemetery.get(payload.emoji.name)
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error finding emoji_name -- ")
                return
        elif payload.guild_id == guifo.queenpalace_id:
            if document['reaction_type'] == "test":
                emoji_name = reans.test_reaction_roles.get(payload.emoji.name)
            elif document['reaction_type'] == "welcome":
                emoji_name = reans.welcome_roles_queenpalace.get(payload.emoji.name)
            elif document['reaction_type'] == "reactroles":
                emoji_name = reans.react_for_roles_queenpalace.get(payload.emoji.name)
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error finding emoji_name -- ")
                return
        elif payload.guild_id == guifo.fire_floozie_id:
            if document['reaction_type'] == "test":
                emoji_name = reans.test_reaction_roles.get(payload.emoji.name)
            elif document['reaction_type'] == "welcome":
                emoji_name = reans.welcome_roles_firefloozie.get(payload.emoji.name)
            elif document['reaction_type'] == "reactroles":
                return
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error finding emoji_name -- ")
                return
        elif payload.guild_id == guifo.dark_lair_id:
            if document['reaction_type'] == "test":
                emoji_name = reans.test_reaction_roles.get(payload.emoji.name)
            elif document['reaction_type'] == "welcome":
                emoji_name = reans.welcome_roles_darklair.get(payload.emoji.name)
            elif document['reaction_type'] == "reactroles":
                emoji_name = reans.react_for_roles_darklair.get(payload.emoji.name)
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error finding emoji_name -- ")
                return
        else:
            return
        try:
            role = discord.utils.get(payload.member.guild.roles, name=emoji_name)
            await payload.member.add_roles(role)
        except Exception as e:
            user = await self.bot.fetch_user(payload.member.id)
            await payload.remove_reaction(payload.emoji.name, user)
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: on_raw_raction_add -- {e} -- ")

    @commands.Cog.listener()  #ToDo: FIX THIS SHIT
    async def on_raw_reaction_remove(self, payload):
        # if payload.member.bot:
        #     return
        print(f"ofrealistener -- {payload.member.name} -- {payload.message_id} -- {payload.emoji.name}")
        try:
            document = ReactionRoles.objects.get(message_id=payload.message_id)
        except Exception as e:
            if FileNotFoundError:
                return
            else:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: on_raw_raction_remove -- {e} -- ")
                return
        try:
            emojistocheck = document['reaction_emojis']
            if payload.emoji.name not in emojistocheck.split("|"):
                return
            if payload.guild_id == guifo.chodeling_id:
                if document['reaction_type'] == "test":
                    emoji_name = reans.test_reaction_roles.get(payload.emoji.name)
                elif document['reaction_type'] == "welcome":
                    emoji_name = reans.welcome_roles_chodeling.get(payload.emoji.name)
                elif document['reaction_type'] == "reactroles":
                    emoji_name = reans.react_for_roles_chodeling.get(payload.emoji.name)
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error finding emoji_name -- ")
                    return
            elif payload.guild_id == guifo.cemetery_id:
                if document['reaction_type'] == "test":
                    emoji_name = reans.test_reaction_roles.get(payload.emoji.name)
                elif document['reaction_type'] == "welcome":
                    emoji_name = reans.welcome_roles_cemetery.get(payload.emoji.name)
                elif document['reaction_type'] == "reactroles":
                    emoji_name = reans.react_for_roles_cemetery.get(payload.emoji.name)
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error finding emoji_name -- ")
                    return
            elif payload.guild_id == guifo.queenpalace_id:
                if document['reaction_type'] == "test":
                    emoji_name = reans.test_reaction_roles.get(payload.emoji.name)
                elif document['reaction_type'] == "welcome":
                    emoji_name = reans.welcome_roles_queenpalace.get(payload.emoji.name)
                elif document['reaction_type'] == "reactroles":
                    emoji_name = reans.react_for_roles_queenpalace.get(payload.emoji.name)
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error finding emoji_name -- ")
                    return
            else:
                return
            guild = self.bot.get_guild(payload.guild_id)
            member = discord.utils.get(guild.members, id=payload.member.id)  # MAYBE FIXED THIS??? IDK   Was payload.user_id
            role = discord.utils.get(guild.roles, name=emoji_name)
            await member.remove_roles(role)
        except Exception as e:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: on_raw_raction_remove -- {e} -- ")

    @commands.command(name="reactionroles")
    async def create_reaction_roles_message(self, ctx, msgtocreate):
        if ctx.author.id != int(OWNERID):
            await ctx.reply(OwnPermError)
            return
        try:
            reactiontype = None
            reaction_role_collection = self.bot.channel_ids.get_collection('reaction_roles')

            async def create_embed(raw):
                nonlocal reactiontype
                if raw == "test":
                    reactiontype = "test"
                    embed = discord.Embed(title="Embedded Reaction Message")
                    for emoji, role in reans.test_reaction_roles.items():
                        embed.add_field(name=role, value=emoji, inline=True)
                    return embed
                elif raw == "welcomemsgchodeling":
                    reactiontype = "welcome"
                    embed = discord.Embed(title=f"Welcome to {ctx.guild.name}", description=reans.ReactWelcMsgChodeling)
                    return embed
                elif raw == "welcomemsgcemetery":
                    reactiontype = "welcome"
                    embed = discord.Embed(title=f"Welcome to {ctx.guild.name}", description=reans.ReactWelcMsgCemetery)
                    return embed
                elif raw == "welcomemsgpalace":
                    reactiontype = "welcome"
                    embed = discord.Embed(title=f"Welcome to {ctx.guild.name}", description=reans.ReactWelcMsgQueenPalace)
                    return embed
                elif raw == "welcomemsgfire":
                    reactiontype = "welcome"
                    embed = discord.Embed(title=f"Welcome to {ctx.guild.name}", description=reans.ReactWelcMsgFireFloozie)
                    return embed
                elif raw == "welcomemsgdark":
                    reactiontype = "welcome"
                    embed = discord.Embed(title=f"Welcome to {ctx.guild.name}", description="")
                    for entry in reans.ReactWelcMsgDarkLair:
                        embed.add_field(name=entry, value="", inline=False)
                    return embed
                elif raw == "reactroleschodeling":
                    reactiontype = "reactroles"
                    embed = discord.Embed(title="React 4 Roles Here")
                    for emoji, role in reans.react_for_roles_chodeling.items():
                        embed.add_field(name=role, value=emoji, inline=True)
                    return embed
                elif raw == "reactrolescemetery":
                    reactiontype = "reactroles"
                    embed = discord.Embed(title="React 4 Roles Here")
                    for emoji, role in reans.react_for_roles_cemetery.items():
                        embed.add_field(name=role, value=emoji, inline=True)
                    return embed
                elif raw == "reactrolespalace":
                    reactiontype = "reactroles"
                    embed = discord.Embed(title="React 4 Roles Here")
                    for emoji, role in reans.react_for_roles_queenpalace.items():
                        embed.add_field(name=role, value=emoji, inline=True)
                    return embed
                elif raw == "reactrolesdark":
                    reactiontype = "reactroles"
                    embed = discord.Embed(title=f"React 4 Roles Here")
                    for emoji, role in reans.react_for_roles_darklair.items():
                        embed.add_field(name=role, value=emoji, inline=True)
                    return embed
                else:
                    return None

            async def create_emoji_list(raw):
                emojis_str = ""
                if raw == "test":
                    for emoji in reans.test_reaction_roles:
                        emojis_str += f"{emoji}|"
                        print(f"raw {emojis_str}")
                    return emojis_str
                elif raw == "welcomemsgchodeling":
                    for emoji in reans.welcome_roles_chodeling:
                        emojis_str += f"{emoji}|"
                        print(f"raw {emojis_str}")
                    return emojis_str
                elif raw == "welcomemsgcemetery":
                    for emoji in reans.welcome_roles_cemetery:
                        emojis_str += f"{emoji}|"
                        print(f"raw {emojis_str}")
                    return emojis_str
                elif raw == "welcomemsgpalace":
                    for emoji in reans.welcome_roles_queenpalace:
                        emojis_str += f"{emoji}|"
                        print(f"raw {emojis_str}")
                    return emojis_str
                elif raw == "welcomemsgfire":
                    for emoji in reans.welcome_roles_firefloozie:
                        emojis_str += f"{emoji}|"
                        print(f"raw {emojis_str}")
                    return emojis_str
                elif raw == "welcomemsgdark":
                    for emoji in reans.welcome_roles_darklair:
                        emojis_str += f"{emoji}|"
                        print(f"raw {emojis_str}")
                    return emojis_str
                elif raw == "reactroleschodeling":
                    for emoji in reans.react_for_roles_chodeling:
                        emojis_str += f"{emoji}|"
                        print(f"raw {emojis_str}")
                    return emojis_str
                elif raw == "reactrolescemetery":
                    for emoji in reans.react_for_roles_cemetery:
                        emojis_str += f"{emoji}|"
                        print(f"raw {emojis_str}")
                    return emojis_str
                elif raw == "reactrolespalace":
                    for emoji in reans.react_for_roles_queenpalace:
                        emojis_str += f"{emoji}|"
                        print(f"raw {emojis_str}")
                    return emojis_str
                elif raw == "reactrolesdark":
                    for emoji in reans.react_for_roles_darklair:
                        emojis_str += f"{emoji}|"
                        print(f"raw {emojis_str}")
                    return emojis_str
            try:
                tosendmessage = await create_embed(msgtocreate)
                if tosendmessage is None:
                    await ctx.reply(f"{msgtocreate} isn't valid, try again")
                    return
                emojis = await create_emoji_list(msgtocreate)
                message = await ctx.channel.send(embed=tosendmessage)
                messageid = message.id
                new_document = ReactionRoles(message_id=messageid, channel_name=ctx.channel.name, guild_name=ctx.guild.name, reaction_type=reactiontype, reaction_emojis=emojis)
                new_document_dict = new_document.to_mongo()
                reaction_role_collection.insert_one(new_document_dict)
                for emojiadd in emojis.split("|"):
                    print(emojiadd)
                    if emojiadd == "":
                        return
                    await message.add_reaction(emojiadd)
            except Exception as e:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f'{formatted_time}: Error creating ReactionRolesMsg\n{e}')
                return
        except Exception as e:
            print(e)
            return


async def setup(bot):
    await bot.add_cog(CustEvents(bot))
