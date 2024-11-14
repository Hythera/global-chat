import discord
from discord.ext import commands
from discord import app_commands
import json

from database.models import UserRole, GlobalMessage, GlobalChannel
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

def format_number(number: int) -> str:
    if number >= 10_000_000:
        return f"{number // 1_000_000}M" 
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 10_000:
        return f"{number // 1_000}k" 
    elif number >= 1000:
        return f"{number / 1000:.1f}k"
    else:
        return number

class message_info(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.message_info_menu = app_commands.ContextMenu(name=discord.app_commands.locale_str("message_info"), callback=self.message_info_callback)
        self.message_info_menu.default_permissions=discord.Permissions(manage_messages=True)
        self.client.tree.add_command(self.message_info_menu) 


    async def message_info_callback(self, interaction: discord.Interaction, message: discord.Message):
        author = await UserRole(interaction.user.id).load()
        if author.stored and config["roles"][author.role]["permission_level"] >= 5:
            uuid = await GlobalMessage().get_uuid(message.id)
            if uuid:
                await interaction.response.defer(ephemeral=True)
                global_messages = await GlobalMessage().get(uuid)
                message_infos = await GlobalMessage().get_infos(uuid)

                try:
                    global_channel = await GlobalChannel(channel_id=message_infos[1]).load()
                    channel = self.client.get_channel(message_infos[1])
                except:
                    channel = None

                if channel:
                    response_embed = discord.Embed(
                        title=f"{config["emojis"]["file_text"]} "+translator.translate(interaction.locale.value, "menu.message_info.response_embed.title"),
                        description=translator.translate(interaction.locale.value, "menu.message_info.response_embed.description", user_id=message_infos[2], message_id=message_infos[0], message_uuid=uuid, instances=len(global_messages), guild_id=channel.guild.id, guild_name=channel.guild.name, guild_member_count=format_number(channel.guild.member_count), channel_id=channel.id, channel_name=channel.name),
                        color=0x4e5058)
                    await interaction.edit_original_response(embed=response_embed, view=EmbedButtons(interaction, global_channel))
                else:
                    message_error_embed = discord.Embed(
                        title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "menu.message_info.message_error_embed.title"),
                        description=translator.translate(interaction.locale.value, "menu.message_info.message_error_embed.description"),
                        color=0xED4245)
                    await interaction.edit_original_response(embed=message_error_embed)
            else:
                database_error_embed = discord.Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "menu.message_info.database_error_embed.title"),
                    description=translator.translate(interaction.locale.value, "menu.message_info.database_error_embed.description"),
                    color=0xED4245)
                await interaction.response.send_message(embed=database_error_embed, ephemeral=True)
        else:
            permission_error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "menu.message_info.permission_error_embed.title"),
                description=translator.translate(interaction.locale.value, "menu.message_info.permission_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=permission_error_embed, ephemeral=True)

class EmbedButtons(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, global_channel):
        super().__init__(timeout=None)
        server_invite = discord.ui.Button(label=translator.translate(interaction.locale.value, "menu.message_info.response_embed.button.server_invite"), style=discord.ButtonStyle.url, url=global_channel.invite)
        self.add_item(server_invite)
        
async def setup(client:commands.Bot) -> None:
    await client.add_cog(message_info(client))