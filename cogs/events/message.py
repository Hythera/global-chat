
import discord
from discord.ext import commands
import string
import random
import asyncio
import json

from database.models import GlobalChannel, GlobalMessage, UserRole
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

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
                         await message.delete()
                    except:
                        pass

                    await self.loop_channels(message, global_channel)

        except Exception as e:
            print("on_message: ", e)
        
            
    async def loop_channels(self, message: discord.Message, global_channel: GlobalChannel):
        channels = await global_channel.get_all_channels()

        uuid = generate_random_string()
        user_role = await UserRole(message.author.id).load()

        guilds = self.client.guilds
        for guild in guilds:
            if guild.id == message.guild.id:
                member_count = guild.member_count
        if user_role.stored == True:
            role = user_role.role
        else:
            role = "default"

        channel: discord.TextChannel = self.client.get_channel(message.channel.id)
        sent_message = await self.send(channel, message.author, role, member_count, global_channel.invite, message.guild, message.content)
        messages = await GlobalMessage().add(uuid, sent_message.id, sent_message.channel.id)

        for entry in channels:
            if entry["guild_id"] != message.guild.id:
                channel: discord.TextChannel = self.client.get_channel(entry["channel_id"])
                if channel:
                    try:
                        perms: discord.Permissions = channel.permissions_for(channel.guild.get_member(self.client.user.id))
                        if perms.send_messages:
                            sent_message = await self.send(channel, message.author, role, member_count, global_channel.invite, message.guild, message.content)
                            await messages.add(uuid, sent_message.id, sent_message.channel.id)
                            await asyncio.sleep(0.05)
                    except:
                        pass


    async def send(self, channel: discord.TextChannel, author: discord.Member, role: str, member_count:int, invite:str, guild: discord.Guild, content: str):
        embed=discord.Embed(
            description=content+"\n",
            color=int(config["roles"][role]["color"], 16))
        if role != "default":
            embed.title = config["roles"][role]["display_name"]
        embed.set_author(name=author.name, icon_url=author.display_avatar, url=f"https://discordapp.com/users/{author.id}")
        embed.add_field(name=translator.translate(guild.preferred_locale.value, "global_chat.message.embed.field.name"),value=translator.translate(guild.preferred_locale.value, "global_chat.message.embed.field.value", support_server=config["support_server_url"], invite=invite))
        if guild.icon:
            embed.set_footer(text=f"{guild.name} - {member_count}", icon_url=guild.icon.url)
        else:
            embed.set_footer(text=f"{guild.name} - {member_count}", icon_url=config["standard_server_icon_url"])
        return await channel.send(embed=embed)
    
async def setup(client:commands.Bot) -> None:
    await client.add_cog(message(client))