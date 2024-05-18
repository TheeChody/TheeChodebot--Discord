import time
import random
import asyncio
from discord.ext import commands
from refs.cya.refsheet import *
from chodebot import logger, fortime, perm_check
from cogs.mondocs import CyaAdventure, CyaMob, CyaPlayer, CyaPlayerAdventure


class CYA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def create_player_document(self, user_id, channel_id):
        cya_player_collection = self.bot.channel_ids.get_collection('cya_player')
        user = await self.bot.fetch_user(user_id)
        new_player_document = CyaPlayer(user_id=user.id, user_name=user.name, channel_playing_id=channel_id)
        new_player_document_dict = new_player_document.to_mongo()
        cya_player_collection.insert_one(new_player_document_dict)
        player_document = CyaPlayer.objects.get_queryset(user_id=user.id)
        return player_document

    @staticmethod
    async def create_player_adventure_document(self, user_id, adventure_id):
        cya_player_adventure_collection = self.bot.channel_ids.get_collection('cya_player_adventure')
        user = await self.bot.fetch_user(user_id)
        new_player_adventure_document = CyaPlayerAdventure(adventure_player_id=user.id, user_name=user.name, adventure_id=adventure_id)
        new_player_adventure_document_dict = new_player_adventure_document.to_mongo()
        cya_player_adventure_collection.insert_one(new_player_adventure_document_dict)
        player_adventure_document = CyaPlayerAdventure.objects.get(adventure_player_id=user.id)
        return player_adventure_document

    @staticmethod  # DO I NEED THIS????????????????
    async def phase_change(player_document, new_phase):
        userid = player_document['user_id']
        player_document.update(player_state=new_phase)
        player_document.save()
        player_document = CyaPlayer.objects.get(user_id=userid)
        return player_document

    @staticmethod  # Thinking this'll do good for a function to figure out what stage of quest we're at, then shuffle around to other functions and return back when needed to change
    async def phase_detection(player_document, player_adventure_document):
        pass

    @staticmethod  # Thinking doing missions/specials alike this
    async def intro_sequence(self, player_document, player_adventure_document):
        channel = self.bot.get_channel(player_document['channel_playing_id'])
        for line in player_adventure_document['adventure_intro_text']:
            channel.send(line)
            await asyncio.sleep(1)

    @commands.Cog.listener()  # Thinking this will be used to look for "reasonable" responses based on which 'sequence' player is in
    async def on_message(self, message):
        try:
            try:
                player_document = CyaPlayer.objects.get(user_id=message.author.id)
            except Exception as f:
                if FileNotFoundError:
                    return
                else:
                    formatted_time = await fortime()
                    logger.error(f"{formatted_time}: Error in CYA-- on_message :: {f}")
                    return
            usersperms = await perm_check(message, message.guild.id)
            if usersperms is None:
                await message.reply(f"You don't have thee right perms to play CYA.")
                return

        except Exception as e:
            print(e)

    @commands.command()
    async def startgame(self, ctx):
        try:
            try:
                player_document = CyaPlayer.objects.get(user_id=ctx.author.id)
            except Exception as f:
                if FileNotFoundError:
                    player_document = self.create_player_document(self, ctx.author.id, ctx.channel.id)
                else:
                    print(f)
                    return
            try:
                player_adventure_document = CyaPlayerAdventure.objects.get(adventure_player_id=ctx.author.id)
            except Exception as f:
                if FileNotFoundError:
                    player_adventure_document = None
                else:
                    print(f)
                    return
            if player_document['player_state'] == "First_Journey":
                if player_adventure_document is None:
                    player_adventure_document = self.create_player_adventure_document(self, ctx.author.id, 1)
                    player_document.update(player_state="In_Adventure")
                    player_document.save()
                else:
                    print("Error, first journey adventure document exists!!!")
            elif player_document['player_state'] == "At_Trader":
                pass
            elif player_document['player_state'] == "In_Adventure":
                pass
            return
        except Exception as e:
            print(e)
            return

    @commands.command()
    async def resumegame(self, ctx):
        pass

    @commands.command()
    async def newadventure(self, ctx):
        pass

    @commands.command()
    async def trader(self, ctx):
        pass


async def setup(bot):
    await bot.add_cog(CYA(bot))
