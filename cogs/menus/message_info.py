import discord
from discord.ext import commands
from discord import app_commands
import json

from database.models import UserRole, GlobalMessage, GlobalChannel
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

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

                found_message = None
                for message in global_messages:
                    if message.get("original_message") == 1:
                        found_message = message
                        break
                if found_message:
                    global_channel = await GlobalChannel(channel_id=found_message["channel_id"]).load()
                    try:
                        channel = self.client.get_channel(global_channel.channel_id)
                        original_messge = await channel.fetch_message(found_message["message_id"])
                    except:
                        original_messge = None
                    if original_messge:
                        response_embed = discord.Embed(
                            title=f"{config["emojis"]["file_text"]} "+translator.translate(interaction.locale.value, "menu.message_info.response_embed.title"),
                            description=translator.translate(interaction.locale.value, "menu.message_info.response_embed.description", user_id=int(original_messge.embeds[0].author.url.split("/")[-1]), message_id=original_messge.id, message_uuid=uuid, guild_id=channel.guild.id, guild_name=channel.guild.name, channel_id=channel.id, channel_name=channel.name),
                            color=0x4e5058)
                        await interaction.edit_original_response(embed=response_embed, view=EmbedButtons(interaction, global_channel))
                        return
                    
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