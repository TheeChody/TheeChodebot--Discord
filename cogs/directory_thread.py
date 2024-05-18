import random
import discord
from discord.ext import commands
from cogs.mondocs import DirectoryChannel, DirectoryUpdate
from chodebot import perm_check, fortime, logger, PermError, guildid_check, ErrorMsgOwner, OWNERTAG, guifo


class ThreadDirectory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        try:
            try:
                document = DirectoryChannel.objects.get(message_id=payload.message_id)
                channel = self.bot.get_channel(document['channel_id'])
                user = await self.bot.fetch_user(payload.member.id)
            except Exception as f:
                if FileNotFoundError:
                    return
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error in on_raw_reaction_add in directory_threads -- {f}")
                    return
            print(f"direallistener -- {payload.member.name} -- {payload.message_id} -- {payload.emoji.name}")
            await self.change_page(self, channel, document, user, payload.emoji.name)
        except Exception as e:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error in on_raw_reaction_add in directory_threads -- {e}")
            return

    @staticmethod
    async def get_page(self, document, emoji):
        skip = 10
        embed = None
        try:
            current_page = document['directory_page']
            next_page = current_page
            start_index = document['directory_index']
            max_page = 0
            remainder = len(document['thread_link'])
            while remainder > 0:
                remainder -= skip
                max_page += 1
            directory_update_collection = self.bot.channel_ids.get_collection('directory_update')
            channel_directory_updates = directory_update_collection.find({"channel_id": document['channel_id']})
            channel_directory_updates_sorted = sorted(channel_directory_updates, key=lambda document: document['thread_name'].lower(), reverse=False)
            if emoji == "⬅️" and current_page > 1:
                next_page = current_page - 1
                start_index -= skip
            elif emoji == "➡️" and current_page < max_page:
                next_page = current_page + 1
                start_index += skip
            channel_directory_updates_sorted_current = channel_directory_updates_sorted[start_index:]
            embed = discord.Embed(title=f"Thread Directory", description=f"Last Updated:\n{document['last_updated']} MST", colour=0x0000FF)
            m = 0
            for n, update_document in enumerate(channel_directory_updates_sorted_current, start=start_index):
                m += 1
                embed.add_field(name=f"{n+1}: {update_document['thread_name'].title()}", value=update_document['thread_link'], inline=False)
                if m == skip or n >= len(channel_directory_updates_sorted):
                    break
            embed.add_field(name=f"Page {next_page}/{max_page}", value="", inline=False)
            try:
                document.update(directory_page=next_page, directory_index=start_index)
                document.save()
            except Exception as f:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error within get_page directory_thread saving/updating document -- {f}")
                pass
            return embed
        except Exception as e:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error within get_page directory_thread -- {e}")
            return embed

    @staticmethod
    async def change_page(self, channel, document, user, emoji):
        message_to_edit = await channel.fetch_message(document['message_id'])
        embed = await self.get_page(self, document, emoji)
        if embed is None:
            await channel.send(f"{user.mention} something wen't wrong changing pages, alerting {OWNERTAG} to thee issue")
        else:
            await message_to_edit.edit(embed=embed)
        if emoji != "none":
            await message_to_edit.remove_reaction(emoji, user)

    @staticmethod
    async def create_directory(self, ctx, channel, channel_type, get_thread):
        try:
            directory_channel_collection = self.bot.channel_ids.get_collection('directory_channel')
            directory_update_collection = self.bot.channel_ids.get_collection('directory_update')
            channel_directory_updates = directory_update_collection.find({"channel_id": channel.id})
            embed = discord.Embed(title=f"{channel_type.title()} Thread Directory", description="", colour=0x0000FF)
            new_message = await channel.send(embed=embed)
            await new_message.add_reaction("⬅️")
            await new_message.add_reaction("➡️")
            new_document_id = str(ctx.guild.id)[:5] + str(channel.id)[:5] + str(random.randint(1, 999))
            new_document_id = int(new_document_id)
            new_document = DirectoryChannel(document_id=new_document_id, channel_id=channel.id, guild_id=ctx.guild.id,
                                            guild_name=ctx.guild.name, message_id=new_message.id, directory_type=channel_type)
            new_document_dict = new_document.to_mongo()
            directory_channel_collection.insert_one(new_document_dict)

            for update in channel_directory_updates:
                directory_document = DirectoryChannel.objects.get(channel_id=channel.id)
                new_thread_name = directory_document['thread_name']
                new_thread_link = directory_document['thread_link']
                new_thread_name.append(update['thread_name'])
                new_thread_link.append(update['thread_link'])
                directory_document.update(thread_name=new_thread_name, thread_link=new_thread_link, prev_author_name=update['author_name'],
                                          prev_author_nick_name=update['author_nick_name'], last_updated=update['date_updated'])
                directory_document.save()
            if get_thread:
                directory_document = DirectoryChannel.objects.get(channel_id=channel.id)
                user = await self.bot.fetch_user(ctx.author.id)
                await self.change_page(self, channel, directory_document, user, "none")
        except Exception as e:
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, "Error within thee backend, logged"))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error within create_directory -- {e}")
            return

    @commands.command()
    async def create_dir(self, ctx, channel_type="general"):
        """Mod and Up
        $create_directory channel_type
        :CHANNEL_TYPE:
        general (DEFAULT)"""
        try:
            usersperms = await perm_check(ctx, ctx.guild.id)
            if usersperms not in ("owner", "admin", "mod"):
                await ctx.reply(PermError)
                return
            guildid = ctx.guild.id
            directory_channel_collection = self.bot.channel_ids.get_collection('directory_channel')
            channelid = await guildid_check(ctx, guildid, channel_type)
            channel = self.bot.get_channel(channelid)
            if channel is None:
                await ctx.reply(f"Channel ID couldn't be found")
                return
            if channel_type == "general":
                if directory_channel_collection.find_one({"_id": channelid, "directory_type": channel_type}):
                    await ctx.reply(f"There is already a matching directory message for that type.")
                    return
            else:
                await ctx.reply(f"{channel_type} isn't valid, try again")
                return
            await self.create_directory(self, ctx, channel, channel_type, False)
        except Exception as e:
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error within create_directory directory_thread -- {e}")
            return

    @commands.command()
    async def directory_update(self, ctx, thread_name=None, thread_link=None, action="add", channel_type="general"):
        """Mod and Up
        $directory_update thread_name thread_link action(OPTIONAL) channel_type(OPTIONAL)
        :ACTION:
        add (DEFAULT)
        remove
        :CHANNEL_TYPE:
        general (DEFAULT)"""
        try:
            usersperms = await perm_check(ctx, ctx.guild.id)
            if usersperms not in ("owner", "admin", "mod"):
                await ctx.reply(PermError)
                return
            guildid = ctx.guild.id
            directory_update_collection = self.bot.channel_ids.get_collection('directory_update')
            channelid = await guildid_check(ctx, guildid, channel_type)
            channel = self.bot.get_channel(channelid)
            if channel is None:
                return
            elif None in (thread_name, thread_link):
                await ctx.reply(f"Something wasn't filled out right. Check thee command structure again. Your input registered as:\n$directory_update {thread_name} {thread_link} {action} {channel_type}")
                return
            try:
                document = DirectoryChannel.objects.get(channel_id=channelid, directory_type=channel_type)
            except Exception as f:
                if FileNotFoundError:
                    await ctx.reply(f"Document Doesn't Exist Yet!!")
                    return
                else:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f))
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error loading document within directory_update directory_thread -- {f}")
                    return
            if action == "add":
                try:
                    formatted_time = await fortime()
                    thread_name = thread_name.replace("_", " ")
                    update_document = DirectoryUpdate(message_id=ctx.message.id, channel_id=channelid, guild_id=ctx.guild.id,
                                                      guild_name=ctx.guild.name, channel_name=channel.name, directory_type=channel_type,
                                                      thread_name=thread_name, thread_link=thread_link, author_name=ctx.author.name,
                                                      author_nick_name=ctx.author.display_name, date_updated=formatted_time)
                    update_document_dict = update_document.to_mongo()
                    directory_update_collection.insert_one(update_document_dict)

                    list_thread_link = document['thread_link']
                    list_thread_name = document['thread_name']
                    list_thread_link.append(thread_link)
                    list_thread_name.append(thread_name)
                    document.update(channel_name=channel.name, prev_author_name=ctx.author.name, prev_author_nick_name=ctx.author.display_name,
                                    last_updated=formatted_time, thread_name=list_thread_name, thread_link=list_thread_link)
                    document.save()
                    document = DirectoryChannel.objects.get(channel_id=channelid, directory_type=channel_type)
                except Exception as f:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f))
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error adding new update_document/updating document in directory_update directory_thread -- {f}")
                    return
            elif action == "remove":
                thread_name = thread_name.replace("_", " ")
                try:
                    directory_update_collection.delete_one({"thread_link": thread_link})
                except Exception as f:
                    if FileNotFoundError:
                        try:
                            directory_update_collection.delete_one({"thread_name": thread_name})
                        except Exception as g:
                            if FileNotFoundError:
                                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f"Update Document couldn't be found for {thread_name} and {thread_link}\n{g}"))
                                return
                            else:
                                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, g))
                                formatted_time = await fortime()
                                logger.error(f"{formatted_time}: Error removing update_document within directory_update directory_thread -- {g}")
                                return
                    else:
                        await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f))
                        formatted_time = await fortime()
                        logger.error(f"{formatted_time}: Error removing update_document within directory_update directory_thread -- {f}")
                        return
                try:
                    new_thread_name = document['thread_name']
                    new_thread_link = document['thread_link']
                    try:
                        thread_link_index = new_thread_link.index(thread_link)
                    except Exception as f:
                        await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f))
                        return
                    try:
                        new_thread_name.remove(thread_name)
                    except Exception as f:
                        if ValueError:
                            try:
                                new_thread_name.remove(thread_link_index)
                                pass
                            except Exception as g:
                                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, g))
                                return
                        else:
                            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f))
                            formatted_time = await fortime()
                            logger.error(f"{formatted_time}: Error updating document within directory_update directory_thread -- {f}")
                            return
                    try:
                        new_thread_link.remove(thread_link)
                    except Exception as f:
                        if ValueError:
                            try:
                                new_thread_link.remove(thread_link_index)
                                pass
                            except Exception as g:
                                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, g))
                                return
                        else:
                            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, f))
                            formatted_time = await fortime()
                            logger.error(f"{formatted_time}: Error updating document within directory_update directory_thread -- {f}")
                            return
                    formatted_time = await fortime()
                    document.update(channel_name=channel.name, prev_author_name=ctx.author.name, prev_author_nick_name=ctx.author.display_name,
                                    last_updated=formatted_time, thread_name=new_thread_name, thread_link=new_thread_link)
                    document.save()
                    document = DirectoryChannel.objects.get(channel_id=channelid, directory_type=channel_type)
                except Exception as e:
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Something went wrong within directory_update directory_thread -- {e}")
                    pass
            embed = await self.get_page(self, document, "None")
            if embed is None:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, "Check Logs/Terminal. Unknown issue"))
                return
            message_to_edit = await channel.fetch_message(document['message_id'])
            await message_to_edit.edit(embed=embed)
        except Exception as e:
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error within directory_update directory_thread -- {e}")
            return

    @commands.command()
    async def thread_update(self, ctx):
        """Mod and Up
        $thread_update"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin", "mod"):
            await ctx.reply(PermError)
            return
        channelid = ctx.channel.id
        channel_document = DirectoryChannel.objects.get(guild_id=ctx.guild.id)
        channel = self.bot.get_channel(channelid)
        user = await self.bot.fetch_user(ctx.author.id)
        await self.change_page(self, channel, channel_document, user, "none")

    @commands.command()
    async def get_threads(self, ctx, channel_type="general"):
        """Get thee thread directory
        $get_threads"""
        try:
            usersperms = await perm_check(ctx, ctx.guild.id)
            if usersperms is None:
                await ctx.reply(PermError)
                return
            if channel_type != "general":
                await ctx.reply(f"chanel_type wasn't registered correct, -- {channel_type}. Try again")
                return
            channelid = ctx.channel.id
            channel = self.bot.get_channel(channelid)
            if ctx.guild.id == guifo.pettysqad_id:
                if channelid != guifo.pettysqad_general_chat:
                    await ctx.reply(f"This command is restricted to 'general-chat'")
                    return
            directory_channel_collection = self.bot.channel_ids.get_collection('directory_channel')
            if directory_channel_collection.find_one({"channel_id": channelid}):
                directory_document = DirectoryChannel.objects.get(channel_id=channelid)
                message_to_delete = await channel.fetch_message(directory_document['message_id'])
                await message_to_delete.delete()
                directory_channel_collection.delete_one({"channel_id": channelid})
            await self.create_directory(self, ctx, channel, channel_type, True)
        except Exception as e:
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, "Error within thee backend, logged"))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error within get_threads -- {e}")
            return


async def setup(bot):
    await bot.add_cog(ThreadDirectory(bot))
