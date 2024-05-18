import discord
import random
from discord.ext import commands
from cogs.mondocs import WarningsLoggerChannel, WarningsLoggerIndividual, WarningsLoggerMessage
from chodebot import fortime, logger, guifo, perm_check, owner_check, OWNERID, OWNERTAG, ErrorMsgOwner, PermError


class WarningSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        try:
            try:
                document = WarningsLoggerChannel.objects.get(message_id=payload.message_id)
                channel = self.bot.get_channel(document['channel_id'])
                user = await self.bot.fetch_user(payload.member.id)
            except Exception as f:
                if FileNotFoundError:
                    return
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error in on_raw_reaction_add in directory_threads -- {f}")
                    return
            print(f"wareallistener -- {payload.member.name} -- {payload.message_id} -- {payload.emoji.name}")
            await self.change_page(self, channel, document, user, payload.emoji.name, payload.guild_id)
        except Exception as e:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error in on_raw_reaction_add in directory_threads -- {e}")
            return

    @staticmethod
    async def get_page(self, document, emoji, guildid):
        skip = 10
        embed = None
        try:
            current_page = document['page']
            next_page = current_page
            start_index = document['index']
            max_page = 0
            remainder = document['users_written_up']
            while remainder > 0:
                remainder -= skip
                max_page += 1
            warnings_logger_individual = self.bot.channel_ids.get_collection('warnings_logger_individual')
            warnings_logger_individual_list = warnings_logger_individual.find({"guild_id": guildid})
            warnings_logger_individual_list_sorted = sorted(warnings_logger_individual_list, key=lambda document: document['author_nick_name'].lower(), reverse=False)
            if emoji == "⬅️" and current_page > 1:
                next_page = current_page - 1
                start_index -= skip
            elif emoji == "➡️" and current_page < max_page:
                next_page = current_page + 1
                start_index += skip
            warnings_logger_individual_list_sorted_current = warnings_logger_individual_list_sorted[start_index:]
            embed = discord.Embed(title=f"Action/Warning Levels", description=f"Last Updated:\n{document['last_updated']} MST", color=0xFF0000)
            m = 0
            for n, individual_document in enumerate(warnings_logger_individual_list_sorted_current, start=start_index):
                m += 1
                embed.add_field(name=f"{n+1}: {individual_document['author_nick_name']}/{individual_document['author_name']}\n{individual_document['author_id']}\nActions: {individual_document['action_level']}\nWarnings: {individual_document['warning_level']}", value=f"Last offense: {individual_document['date_last_offense']} MST", inline=False)
                if m == skip or n >= document['users_written_up']:
                    break
            embed.add_field(name=f"Page {next_page}/{max_page}", value="", inline=False)
            try:
                document.update(page=next_page, index=start_index)
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
    async def change_page(self, channel, document, user, emoji, guildid):
        message_to_edit = await channel.fetch_message(document['message_id'])
        embed = await self.get_page(self, document, emoji, guildid)
        if embed is None:
            await channel.send(f"{user.mention} something wen't wrong changing pages, alerting {OWNERTAG} to thee issue")
        else:
            await message_to_edit.edit(embed=embed)
        if emoji != "none":
            await message_to_edit.remove_reaction(emoji, user)

    @commands.command()
    async def update_action(self, ctx, userid, action_level, link=None, extra=None, warning_level=0):
        """Mod and Higher Use Only
        $update_action userid action_level link extra(optional) warning_level(optional)"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin", "mod"):
            await ctx.reply(PermError)
            return
        if ctx.channel.id in guifo.spc_automod_group:
            action_level = int(action_level)
            warning_level = int(warning_level)
            warnings_logger_individual = self.bot.channel_ids.get_collection('warnings_logger_individual')
            warnings_logger_message = self.bot.channel_ids.get_collection('warnings_logger_message')
            userid = int(userid)
            messageid = ctx.message.id
            channelid = ctx.channel.id
            guildid = ctx.guild.id
            channel_document = WarningsLoggerChannel.objects.get(guild_id=guildid)
            channel = self.bot.get_channel(channelid)
            user = await self.bot.fetch_user(userid)
            try:
                individual_document = WarningsLoggerIndividual.objects.get(author_id=userid, guild_id=guildid)
            except Exception as e:
                if FileNotFoundError:
                    new_document_id = str(userid)[:5] + str(guildid)[:5] + str(random.randint(1, 99))
                    new_document_id = int(new_document_id)
                    new_document = WarningsLoggerIndividual(document_id=new_document_id, guild_name=ctx.guild.name, guild_id=guildid, channel_id=channelid,
                                                            author_id=user.id, author_name=user.name, author_nick_name=user.display_name)
                    new_document_dict = new_document.to_mongo()
                    warnings_logger_individual.insert_one(new_document_dict)
                    individual_document = WarningsLoggerIndividual.objects.get(author_id=userid, guild_id=guildid)
                    new_users_written_up = channel_document['users_written_up'] + 1
                    channel_document.update(users_written_up=new_users_written_up)
                    channel_document.save()
                    channel_document = WarningsLoggerChannel.objects.get(guild_id=guildid)
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error selecting/creating individual doc :: {e}")
                    await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                    return
            if link is None:
                server_owner_id = await owner_check(ctx, ctx.guild.id)
                if server_owner_id is None:
                    server_owner_id = OWNERID
                link = f"<@{server_owner_id}> get with me in a chat to explain"
            if warning_level == 0:
                warning_level = individual_document['warning_level']
            formatted_time = await fortime()
            message_content = f"{formatted_time} MST: {ctx.author.name} wrote up\nUser:{user.id, user.display_name, user.name}\nNew Action Level: {action_level}. New Warning Level: {warning_level}.\nLink: {link}.\nExtra: {extra}"
            new_document_message = WarningsLoggerMessage(message_id=messageid, message_date_time=formatted_time, guild_name=ctx.guild.name, guild_id=guildid, channel_name=ctx.channel.name,
                                                         channel_id=channelid, mod_author=ctx.author.name, offender_id=userid, offender_name=user.name, offender_nick_name=user.display_name,
                                                         message_content=message_content, raw_message_content=ctx.message.content)
            new_document_message_dict = new_document_message.to_mongo()
            warnings_logger_message.insert_one(new_document_message_dict)
            await ctx.reply(f"Your update has been logged as follows:\n{message_content}")

            new_dates_written_up = f"{individual_document['dates_written_up']}|{formatted_time}"
            individual_document.update(message_id=messageid, author_name=user.name, author_nick_name=user.display_name, warning_level=warning_level,
                                       action_level=action_level, date_last_offense=formatted_time, dates_written_up=new_dates_written_up)
            individual_document.save()
            await self.change_page(self, channel, channel_document, user, "none", guildid)
        else:
            await ctx.reply(f"This command is restricted to warnings channel only")
            return

    @commands.command()
    async def create_warn_list(self, ctx):
        """Admin and Higher Use Only
        $create_warn_list"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin"):
            await ctx.reply(PermError)
            return
        warnings_logger_channel = self.bot.channel_ids.get_collection('warnings_logger_channel')
        for channelid in guifo.spc_automod_group:
            try:
                if warnings_logger_channel.find_one({"channel_id": channelid}):
                    pass
                else:
                    formatted_time = await fortime()
                    channel = self.bot.get_channel(channelid)
                    embed = discord.Embed(title=f"Action/Warning Levels", description=f"Last Updated: {formatted_time} MST", color=0xFF0000)
                    message_to_create = await channel.send(embed=embed)
                    await message_to_create.add_reaction("⬅️")
                    await message_to_create.add_reaction("➡️")
                    new_document = WarningsLoggerChannel(message_id=message_to_create.id, guild_name=channel.guild.name, guild_id=channel.guild.id, channel_name=channel.name,
                                                         channel_id=channelid, mod_author=ctx.author.name)
                    new_document_dict = new_document.to_mongo()
                    warnings_logger_channel.insert_one(new_document_dict)
            except Exception as e:
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error happened creating_warning_list :: {e}")

    @commands.command()
    async def get_warn_message(self, ctx, userid: int):
        """Mod and Higher Use Only
        $get_warn_message userid"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin", "mod"):
            await ctx.reply(PermError)
            return
        try:
            warnings_logger_channel_collection = self.bot.channel_ids.get_collection('warnings_logger_channel')
            if warnings_logger_channel_collection.find_one({"channel_id": ctx.channel.id}):
                pass
            else:
                prev_author = ctx.author
                await ctx.message.delete()
                await ctx.channel.send(f"{prev_author.mention} that command is restricted to certain channels. Get with TheeChody if you're unsure where", delete_after=30)
                return
        except Exception as e:
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error fetching channel document for warning system in g({ctx.guild.id}) c({ctx.channel.id}) -- {e}")
            return
        user = await self.bot.fetch_user(userid)
        try:
            warnings_logger_message = self.bot.channel_ids.get_collection('warnings_logger_message')
            warnings_individual_messages = warnings_logger_message.find({"offender_id": userid})
        except Exception as e:
            print(e)
            return
        embed = discord.Embed(title=f"{user.display_name}'s warning messages", description="", colour=0xFF0000)
        n = 1
        for document in warnings_individual_messages:
            try:
                if document['guild_id'] == ctx.guild.id:
                    embed.add_field(name=f"Write Up #{n}", value=f"{document['message_content']}", inline=False)
                    n += 1
            except Exception as e:
                print(e)
                continue
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def warnsys_update(self, ctx):
        """Mod and Up
        $warnsys_update"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin", "mod"):
            await ctx.reply(PermError)
            return
        channelid = ctx.channel.id
        guildid = ctx.guild.id
        channel_document = WarningsLoggerChannel.objects.get(guild_id=guildid)
        channel = self.bot.get_channel(channelid)
        user = await self.bot.fetch_user(ctx.author.id)
        await self.change_page(self, channel, channel_document, user, "none", guildid)

    @commands.command()
    async def warnsys_add_emojis(self, ctx):
        """Admin and Up
        DO NOT USE IF EMOJIS ALREADY ASSIGNED
        $warnsys_add_emojis"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin"):
            await ctx.reply(PermError)
            return
        channel = self.bot.get_channel(ctx.channel.id)
        document = WarningsLoggerChannel.objects.get(guild_id=ctx.guild.id)
        message_to_edit = await channel.fetch_message(document['message_id'])
        await message_to_edit.add_reaction("⬅️")
        await message_to_edit.add_reaction("➡️")


async def setup(bot):
    await bot.add_cog(WarningSystem(bot))
