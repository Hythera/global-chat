
import discord
from discord.ext import commands
import string
import random
import asyncio

from database.models import GlobalChannel, Message

def generate_random_string():
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(20))
    return random_string

class message(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        try:
            if message.author.bot:
                return
            if not message.guild:
                return
            if isinstance(message.channel, discord.TextChannel):
                global_channel = await GlobalChannel(channel_id=message.channel.id).load()
                if global_channel.stored == True:
                    try:
                        perms: discord.Permissions = message.channel.permissions_for(message.guild.get_member(self.client.user.id))
                        if perms.manage_messages:
                            await message.delete()
                    except:
                        pass

                    await self.loop_channels(message)

        except Exception as e:
            print("on_message: ", e)
            
    async def loop_channels(self, message: discord.Message):
        global_channel = await GlobalChannel(channel_id=message.channel.id).load()
        channels = await global_channel.get_all_channels()

        uuid = generate_random_string()
        

        channel: discord.TextChannel = self.client.get_channel(message.channel.id)
        sent_message = await self.send(channel, message.author, message.guild, message.content)
        messages = await Message().add(uuid, sent_message.id, sent_message.guild.id)

        for entry in channels:
            if entry["guild_id"] != message.guild.id:
                guild: discord.Guild = self.client.get_guild(entry["guild_id"])
                if guild:
                    channel: discord.TextChannel = self.client.get_channel(entry["channel_id"])
                    if channel:
                        try:
                            perms: discord.Permissions = channel.permissions_for(guild.get_member(self.client.user.id))
                            if perms.send_messages:
                                sent_message = await self.send(channel, message.author, message.guild, message.content)
                                await messages.add(uuid, sent_message.id, sent_message.guild.id)
                                await asyncio.sleep(0.054)
                        except:
                            pass

    async def send(self, channel: discord.TextChannel, author: discord.User, guild: discord.Guild, content: str):
        embed=discord.Embed(
            description=content,
            color=0x4e5058)
        embed.set_author(name=author.name, icon_url=author.avatar.url)
        if guild.icon:
            embed.set_footer(text=f"{guild.name} - 0", icon_url=guild.icon.url)
        else:
            embed.set_footer(text=f"{guild.name} - 0") #TODO
        return await channel.send(embed=embed)
    
async def setup(client:commands.Bot) -> None:
    await client.add_cog(message(client))