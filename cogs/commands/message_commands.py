import discord
from discord.ext import commands
from discord import User, app_commands
import json
import time
import asyncio

from database.models import UserRole, GlobalMessage
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

class message_commands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    message_command = app_commands.Group(name=discord.app_commands.locale_str("message"), description=discord.app_commands.locale_str("message_description"), default_permissions=discord.Permissions(manage_messages=True), guild_only=True, guild_ids=[config["admin_guild_id"]])

    @message_command.command(name=discord.app_commands.locale_str("delete"), description=discord.app_commands.locale_str("message_delete_description"))
    @app_commands.describe(uuid=discord.app_commands.locale_str("message_delete_describe_uuid"))
    async def rmessage_delete(self, interaction: discord.Interaction, uuid: str):
        author = await UserRole(interaction.user.id).load()
        if author.stored and config["roles"][author.role]["permission_level"] >= 5:
            await interaction.response.defer(ephemeral=True)
            global_messages = await GlobalMessage().get(uuid)
            if global_messages != []:
                instance_count = 0
                start_time = time.time() * 1000
                for global_message in global_messages:
                    channel = self.client.get_channel(global_message["channel_id"])
                    if channel:
                        try:
                            message = await channel.fetch_message(global_message["message_id"])
                            await message.delete()
                            instance_count += 1
                            await asyncio.sleep(0.05)  
                        except:
                            pass    
                duration = f"{int((time.time() * 1000) - start_time)}ms"
                success_embed= discord.Embed(
                    title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "command.message_delete.success_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.message_delete.success_embed.description", count=instance_count, duration=duration),
                    color=0x57F287)
                await interaction.edit_original_response(embed=success_embed)
            else:
                database_error_embed = discord.Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.message_delete.database_error_embed.title"),
                    description=translator.translate(interaction.locale.value, "command.message_delete.database_error_embed.description"),
                    color=0xED4245)
                await interaction.edit_original_response(embed=database_error_embed)
        else:
            permission_error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "command.role.set.permission_error_embed.title"),
                description=translator.translate(interaction.locale.value, "command.role.set.permission_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=permission_error_embed, ephemeral=True)
      

async def setup(client:commands.Bot) -> None:
    await client.add_cog(message_commands(client))