
import discord
from discord.ext import commands
import string
import random
import asyncio
from json import load
import time
import re

from database.models import GlobalChannel, GlobalMessage, UserRole, Mutes
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = load(file)

link_regex = re.compile(r'(?:https?://)[a-z0-9_\-\.]*[a-z0-9_\-]')

def generate_random_string():
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(20))
    return random_string

class message(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.global_chat_cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)
    
    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        global_channel = None
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

                    if message.type not in [discord.MessageType.default, discord.MessageType.reply]:
                        return

                    bucket = self.global_chat_cooldown.get_bucket(message)
                    retry_after = bucket.update_rate_limit()
                    if retry_after:
                        cooldown_error_embed = discord.Embed(
                            title=f"{config["emojis"]["clock_red"]} "+translator.translate(message.guild.preferred_locale.value, "global_chat.cooldown_error_embed.title"),
                            description=translator.translate(message.guild.preferred_locale.value, "global_chat.cooldown_error_embed.description",time=round(time.time()+retry_after)),
                            color=0xED4245)
                        try:
                            await message.author.send(embed=cooldown_error_embed)
                        except:
                            pass
                        return

                    user = await Mutes(message.author.id).load()
                    if user.stored:
                        if user.exipires_at == None:
                            time_str = translator.translate(message.guild.preferred_locale.value, "global_chat.translation.never")
                        else:
                            time_str = f"<t:{int(user.exipires_at.timestamp())}:R>"
                        mute_error_embed = discord.Embed(
                            title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(message.guild.preferred_locale.value, "global_chat.mute_error_embed.title"),
                            description=translator.translate(message.guild.preferred_locale.value, "global_chat.mute_error_embed.description", time=time_str, reason=user.reason),
                            color=0xED4245)
                        try:
                            await message.author.send(embed=mute_error_embed)
                        except:
                            pass
                        return
                    
                    if message.attachments:
                        attachment_error_embed = discord.Embed(
                            title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(message.guild.preferred_locale.value, "global_chat.attachment_error_embed.title"),
                            description=translator.translate(message.guild.preferred_locale.value, "global_chat.attachment_error_embed.description"),
                            color=0xED4245)
                        try:
                            await message.author.send(embed=attachment_error_embed)
                        except:
                            pass
                        return
                    
                    user_role = await UserRole(message.author.id).load()
                    if not user_role.stored or config["roles"][user_role.role]["permission_level"] < 10:      
                        if link_regex.search(message.content):
                            link_error_embed = discord.Embed(
                                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(message.guild.preferred_locale.value, "global_chat.link_error_embed.title"),
                                description=translator.translate(message.guild.preferred_locale.value, "global_chat.link_error_embed.description"),
                                color=0xED4245)
                            try:
                                await message.author.send(embed=link_error_embed)
                            except:
                                pass
                            return
                        
                    if message.reference:
                        reference_uuid = await GlobalMessage().get_uuid(message.reference.message_id)
                    else:
                        reference_uuid = None
                        
                    await self.loop_channels(message, global_channel, user_role, reference_uuid)

        except Exception as e:
            if global_channel:
                error_channel = self.client.get_channel(config["channels"]["errors"])
                line_image = discord.File("images/line.png")
                log_embed = discord.Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(error_channel.guild.preferred_locale.value, "log.errors.log_embed.title"),
                    description=translator.translate(error_channel.guild.preferred_locale.value, "log.errors.log_embed.description", type="on_message", command="None", user="`None`"),
                    color=0xED4245)
                log_embed.set_image(url="attachment://line.png")
                content_embed = discord.Embed(
                    title=f"{config["emojis"]["file_text_red"]} "+translator.translate(error_channel.guild.preferred_locale.value, "log.errors.content_embed.title"),
                    description=f"```{e}```",
                    color=0xED4245)
                content_embed.set_image(url="attachment://line.png")
                await error_channel.send(embeds=[log_embed, content_embed], files=[line_image])
        
            
    async def loop_channels(self, message: discord.Message, global_channel: GlobalChannel, user_role: UserRole, reference_uuid: str = None):
        channels = await global_channel.get_all_channels()

        if reference_uuid:
            data = await GlobalMessage().get(reference_uuid)
            referenced_messages = {item['channel_id']: item['message_id'] for item in data}
        else:
            referenced_messages = None

        uuid = generate_random_string()

        if user_role.stored == True:
            role = user_role.display_role
        else:
            role = "default"

        channel: discord.TextChannel = self.client.get_channel(message.channel.id)
        if global_channel.setting_invite == 0:
            sent_message = await self.send(channel, message.author, role, None, message.guild, message.content, referenced_messages)
        else:
            sent_message = await self.send(channel, message.author, role, global_channel.invite, message.guild, message.content, referenced_messages)
        messages = await GlobalMessage().add(uuid, sent_message.id, sent_message.channel.id)
        await messages.add_info(uuid, sent_message.id, sent_message.channel.id, message.author.id)

        for entry in channels:
            if entry["guild_id"] != message.guild.id:
                channel: discord.TextChannel = self.client.get_channel(entry["channel_id"])
                if channel:
                    try:
                        perms: discord.Permissions = channel.permissions_for(channel.guild.get_member(self.client.user.id))
                        if perms.send_messages:
                            if global_channel.setting_invite == 0:
                                sent_message = await self.send(channel, message.author, role, None, message.guild, message.content, referenced_messages)
                            else:
                                sent_message = await self.send(channel, message.author, role, global_channel.invite, message.guild, message.content, referenced_messages)
                            await messages.add(uuid, sent_message.id, sent_message.channel.id)
                            await asyncio.sleep(0.05)
                    except:
                        pass


    async def send(self, channel: discord.TextChannel, author: discord.Member, role: str, invite:str, guild: discord.Guild, content: str, referenced_messages: dict):
        embed=discord.Embed(
            description=f"{content}\n⠀",
            color=int(config["roles"][role]["color"], 16))
        try:
            icon = discord.File(f"images/icons/{role}.png",)
        except:
            icon = discord.File(f"images/icons/default.png", filename=f"{role}.png")
        embed.set_author(name=author.name, url=f"https://discordapp.com/users/{author.id}", icon_url=f"attachment://{role}.png")
        if author.avatar:
            embed.set_thumbnail(url=author.avatar.with_size(256).url)
        else:
            embed.set_thumbnail(url=author.default_avatar.with_size(256).url)
        if invite:
            embed.add_field(name=translator.translate(channel.guild.preferred_locale.value, "global_chat.message.embed.field.name"),value=translator.translate(channel.guild.preferred_locale.value, "global_chat.message.embed.field.value.invite", support_server=config["support_server_url"], invite=invite))
        else:
            embed.add_field(name=translator.translate(channel.guild.preferred_locale.value, "global_chat.message.embed.field.name"),value=translator.translate(channel.guild.preferred_locale.value, "global_chat.message.embed.field.value", support_server=config["support_server_url"]))
        if guild.icon:
            embed.set_footer(text=f"{guild.name}", icon_url=guild.icon.with_size(64).url)
        else:
            embed.set_footer(text=f"{guild.name}", icon_url=config["standard_server_icon_url"])
        try:
            if referenced_messages:
                try:
                    message: discord.Message = await channel.fetch_message(referenced_messages[channel.id])
                except:
                    message = None
                if message:
                    return await message.reply(embed=embed, file=icon)
                else:
                    return await channel.send(embed=embed, files=icon)

            else:
                return await channel.send(embed=embed, file=icon)
        except:
            return None


async def setup(client:commands.Bot) -> None:
    await client.add_cog(message(client))