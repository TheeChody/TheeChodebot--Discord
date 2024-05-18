import discord
from discord.ext import commands
from cogs.mondocs import EconomyData
from chodebot import logger, fortime, perm_check, PermError, ErrorMsgOwner, OWNERTAG


async def add_points(self, ctx, authorid: int, value: int, gambling: bool):
    try:
        document = EconomyData.objects.get(author_id=authorid)
    except Exception as e:
        if FileNotFoundError:
            economy_data_collection = self.bot.channel_ids.get_collection('economy_data')
            new_user = self.bot.get_user(authorid)
            new_document = EconomyData(author_id=authorid, author_name=new_user.name, guild_name=ctx.guild.name)
            new_document_dict = new_document.to_mongo()
            economy_data_collection.insert_one(new_document_dict)
            document = EconomyData.objects.get(author_id=authorid)
        else:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: add_points errored out: {e}")
            return
    new_points_value = document['points_value'] + value
    if gambling:
        if value > document['highest_gambling_won']:
            document.update(highest_gambling_won=value)
            document.save()
        new_total_won = document['total_gambling_won'] + value
        document.update(points_value=new_points_value, total_gambling_won=new_total_won)
        document.save()
    else:
        if value > document['highest_gained_value']:
            document.update(highest_gained_value=value)
            document.save()
        if value >= 2:
            document.update(points_value=new_points_value, last_gained_value=value)
            document.save()
        else:
            document.update(points_value=new_points_value)
            document.save()
    if value > 75 and not gambling:
        author = await self.bot.fetch_user(authorid)
        await ctx.channel.send(f"{author.mention} you gained {value} points", silent=True, delete_after=10)


async def remove_points(self, ctx, authorid: int, value: int, gambling: bool):
    try:
        document = EconomyData.objects.get(author_id=authorid)
    except Exception as e:
        if FileNotFoundError:
            economy_data_collection = self.bot.channel_ids.get_collection('economy_data')
            new_user = self.bot.get_user(authorid)
            new_document = EconomyData(author_id=authorid, author_name=new_user.name, guild_name=ctx.guild.name)
            new_document_dict = new_document.to_mongo()
            economy_data_collection.insert_one(new_document_dict)
            document = EconomyData.objects.get(author_id=authorid)
        else:
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: add_points errored out: {e}")
            return
    new_points_value = document['points_value'] - value
    if new_points_value < 0:
        new_points_value = 0
    if gambling:
        if value > document['highest_gambling_lost']:
            document.update(highest_gambling_lost=value)
            document.save()
        new_total_lost = document['total_gambling_lost'] + value
        document.update(points_value=new_points_value, total_gambling_lost=new_total_lost)
        document.save()
    else:
        if value > document['highest_lost_value']:
            document.update(highest_lost_value=value)
            document.save()
        if value >= 2:
            document.update(points_value=new_points_value, last_lost_value=value)
            document.save()
        else:
            document.update(points_value=new_points_value)
            document.save()
    if value > 75 and not gambling:
        author = await self.bot.fetch_user(authorid)
        await ctx.reply(f"{author.mention} you lost {value} points", silent=True, delete_after=10)


class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def createpoints(self, ctx):
        """Creates a document to store your points in."""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            return
        economy_data = self.bot.channel_ids.get_collection('economy_data')
        try:
            new_document = EconomyData(author_id=int(ctx.author.id), author_name=ctx.author.name, guild_name=ctx.guild.name)
            new_document_dict = new_document.to_mongo()
            economy_data.insert_one(new_document_dict)
            await ctx.reply(f"A document has been created for ya, you are ready to start collecting points!")
        except Exception as e:
            if FileExistsError:
                await ctx.reply(f"You already have a doc for ya")
            else:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error creating a document for {ctx.author.name} in {ctx.guild.name}'s {ctx.channel.name}\n{e}")

    @commands.command()
    async def deletepoints(self, ctx):
        """This deletes your history, careful non-reversible!!"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            return
        economy_data = self.bot.channel_ids.get_collection('economy_data')
        try:
            if economy_data.find_one({"_id": ctx.author.id}):
                economy_data.delete_one({"_id": ctx.author.id})
                await ctx.reply(f"Your Points Document Has Been Deleted")
                return
            elif FileNotFoundError:
                await ctx.reply(f"You don't have a document for points yet")
                return
        except Exception as e:
            # if FileNotFoundError:
            #     await ctx.reply(f"You don't have a document for points yet")
            #     return
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Error deleting document for {ctx.author.name} in {ctx.guild.name}'s {ctx.channel.name}\n{e}")
            return

    @commands.command()
    async def pointscheck(self, ctx):
        """To check your individual point count"""
        userspersm = await perm_check(ctx, ctx.guild.id)
        if userspersm is None:
            return
        economy_data = self.bot.channel_ids.get_collection('economy_data')
        try:
            document = EconomyData.objects.get(author_id=ctx.author.id)
        except Exception as e:
            if FileNotFoundError:
                new_document = EconomyData(author_id=ctx.author.id, author_name=ctx.author.name, guild_name=ctx.guild.name)
                new_document_dict = new_document.to_mongo()
                economy_data.insert_one(new_document_dict)
                document = EconomyData.objects.get(author_id=ctx.author.id)
            else:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error checking {ctx.author.name} data in {ctx.guild.name}'s {ctx.channel.name}\n{e}")
                return
        channel = self.bot.get_channel(ctx.channel.id)
        embed = discord.Embed(title=f"Your current point value is: {document['points_value']}", description="", color=0x006900)
        embed.add_field(name=f"Last Gain/loss: {document['last_gained_value']}/{document['last_lost_value']}", value=f"", inline=False)
        embed.add_field(name=f"Highest Gain/Loss: {document['highest_gained_value']}/{document['highest_lost_value']}", value=f"", inline=False)
        embed.add_field(name=f"Highest Gamble Win/Loss: {document['highest_gambling_won']}/{document['highest_gambling_lost']}", value=f"", inline=False)
        embed.add_field(name=f"Total Gamble Won/Lost: {document['total_gambling_won']}/{document['total_gambling_lost']}", value=f"", inline=False)
        await channel.send(channel, embed=embed)

    @commands.command()
    async def pointsleader(self, ctx):
        """Displays user points leaderboard"""
        userspersm = await perm_check(ctx, ctx.guild.id)
        if userspersm is None:
            return
        try:
            economy_data = self.bot.channel_ids.get_collection('economy_data')
            economydocuments = economy_data.find({})
            # Sort the economy documents by points_value in descending order
            economydocuments = sorted(economydocuments, key=lambda document: document['points_value'], reverse=True)  # also this lambda document throws a shadows outterscope variable
            # Get the top ten economy documents
            top_ten_economydocuments = economydocuments[:10]
            embed = discord.Embed(title=f"Top 10 Point Leaders:", description="", color=0x006900)
            for n, document in enumerate(top_ten_economydocuments):
                embed.add_field(name=f"{n+1}: {document['points_value']:,}: {document['author_name']}", value=document['guild_name'], inline=False)
            channel = self.bot.get_channel(ctx.channel.id)
            await channel.send(channel, embed=embed)
        except Exception as e:
            if FileNotFoundError:
                await ctx.reply(f"There either hasn't been any documents created yet or something else happened. Check this:\n{e}")
            else:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error pointsleader -- {e}")

    @commands.command()
    async def pointsleaderguild(self, ctx):
        """Displays the Guild points leaderboard"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms is None:
            return
        try:
            # Get the collection of economy data
            economy_data = self.bot.channel_ids.get_collection("economy_data")
            # Execute the aggregation pipeline
            guild_pipeline = [
                {
                    "$group": {
                        "_id": "$guild_name",
                        "total_points": {
                            "$sum": "$points_value"
                        }
                    }
                },
                {
                    "$sort": {
                        "total_points": -1
                    }
                }
            ]
            results = economy_data.aggregate(guild_pipeline)
            # Display the guild leaderboard
            channel = self.bot.get_channel(ctx.channel.id)
            embed = discord.Embed(title=f"Top 10 Guild Leaders:", description="", color=0x006900)
            for n, result in enumerate(results):
                embed.add_field(name=f"{n+1}: {result['_id']}: {result['total_points']:,}", value="", inline=False)
            await channel.send(channel, embed=embed)
        except Exception as e:
            await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
            formatted_time = await fortime()
            logger.error(f"{formatted_time}: Guild Leaderboard Errored out: {e}")

    @commands.command()
    async def addpoints(self, ctx, username: str, value: int):
        """Give points to a certain user, must be the username not custom nickname
        $addpoints theechodebot#8289 100"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin"):
            await ctx.reply(PermError)
            return
        try:
            document = EconomyData.objects.get(author_name=username)
        except Exception as e:
            if FileNotFoundError:
                await ctx.reply(f"The user has no document yet, try again later")
                return
            else:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error adding {value} to {username} in {ctx.guild.name}'s {ctx.channel.name}\n{e}")
                return
        new_points_value = document['points_value'] + value
        document.update(points_value=new_points_value)
        document.save()
        await ctx.reply(f"You have awarded {value} to {username}. New current is {new_points_value}")
        formatted_time = await fortime()
        logger.info(f"{formatted_time}: {ctx.author.name} gave {username} {value} points in {ctx.channel.name} -- {ctx.guild.name}")
        return

    @commands.command()
    async def rempoints(self, ctx, username: str, value: int):
        """Remove points from a certain user, must be the username not custom nickname
        $rempoints theechodebot#8289 100"""
        usersperms = await perm_check(ctx, ctx.guild.id)
        if usersperms not in ("owner", "admin"):
            await ctx.reply(PermError)
            return
        try:
            document = EconomyData.objects.get(author_name=username)
        except Exception as e:
            if FileNotFoundError:
                await ctx.reply(f"The user has no document yet, try again later")
                return
            else:
                await ctx.reply(ErrorMsgOwner.format(OWNERTAG, e))
                formatted_time = await fortime()
                logger.error(f"{formatted_time}: Error removing {value} from {username} in {ctx.guild.name}'s {ctx.channel.name}\n{e}")
                return
        new_points_value = document['points_value'] - value
        document.update(points_value=new_points_value)
        document.save()
        await ctx.reply(f"You have taken away {value} from {username}. New current is {new_points_value}")
        formatted_time = await fortime()
        logger.info(f"{formatted_time}: {ctx.author.name} took {value} points from {username} in {ctx.channel.name} -- {ctx.guild.name}")
        return


async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
