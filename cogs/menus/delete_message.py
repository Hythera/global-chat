import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import time

from database.models import UserRole, GlobalMessage
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

class delete_message(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.delete_message_menu = app_commands.ContextMenu(name=discord.app_commands.locale_str("delete_message"), callback=self.delete_message_callback, )
        self.delete_message_menu.default_permissions=discord.Permissions(manage_messages=True)
        self.client.tree.add_command(self.delete_message_menu) 


    async def delete_message_callback(self, interaction: discord.Interaction, message: discord.Message):
        author = await UserRole(interaction.user.id).load()
        if author.stored and config["roles"][author.role]["permission_level"] >= 10:
            uuid = await GlobalMessage().get_uuid(message.id)
            if uuid:
                await interaction.response.defer(ephemeral=True)
                global_messages = await GlobalMessage().get(uuid)

                instance_count = 0
                start_time = time.time() * 1000
                for global_message in global_messages:
                    guild = self.client.get_guild(global_message["guild_id"])
                    if guild:
                        channel = guild.get_channel(global_message["channel_id"])
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
                    title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "menu.database_message.success_embed.title"),
                    description=translator.translate(interaction.locale.value, "menu.database_message.success_embed.description", count=instance_count, duration=duration),
                    color=0x57F287)
                await interaction.edit_original_response(embed=success_embed)
            else:
                database_error_embed = discord.Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "menu.database_message.permission_error_embed.title"),
                    description=translator.translate(interaction.locale.value, "menu.delete_message.database_error_embed.description"),
                    color=0xED4245)
                await interaction.response.send_message(embed=database_error_embed, ephemeral=True)
        else:
            permission_error_embed = discord.Embed(
                title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "menu.delete_message.permission_error_embed.title"),
                description=translator.translate(interaction.locale.value, "menu.delete_message.permission_error_embed.description"),
                color=0xED4245)
            await interaction.response.send_message(embed=permission_error_embed, ephemeral=True)
        

async def setup(client:commands.Bot) -> None:
    await client.add_cog(delete_message(client))