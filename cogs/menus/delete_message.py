import discord
from discord.ext import commands
from discord import app_commands
from json import load
import asyncio
import time

from database.models import UserRole, GlobalMessage
from languages import Translator
translator = Translator()

with open("config.json", 'r', encoding='utf-8') as file:
    config = load(file)

class delete_message(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.delete_message_menu = app_commands.ContextMenu(name=discord.app_commands.locale_str("delete_message"), callback=self.delete_message_callback)
        self.delete_message_menu.default_permissions=discord.Permissions(manage_messages=True)
        self.client.tree.add_command(self.delete_message_menu) 


    async def delete_message_callback(self, interaction: discord.Interaction, message: discord.Message):
        author = await UserRole(interaction.user.id).load()
        if author.stored and config["roles"][author.role]["permission_level"] >= 5:
            uuid = await GlobalMessage().get_uuid(message.id)
            if uuid:
                await interaction.response.defer(ephemeral=True)
                message_infos = await GlobalMessage().get_infos(uuid)
                global_messages = await GlobalMessage().get(uuid)
                
                instance_count = 0
                start_time = time.time() * 1000
                for global_message in global_messages:
                    channel = self.client.get_channel(global_message["channel_id"])
                    if channel:
                        try:
                            loop_message = await channel.fetch_message(global_message["message_id"])
                            await loop_message.delete()
                            instance_count += 1
                            await asyncio.sleep(0.05)  
                        except:
                            pass    
                duration = f"{int((time.time() * 1000) - start_time)}ms"
                success_embed= discord.Embed(
                    title=f"{config["emojis"]["check_circle_green"]} "+translator.translate(interaction.locale.value, "menu.delete_message.success_embed.title"),
                    description=translator.translate(interaction.locale.value, "menu.delete_message.success_embed.description", count=instance_count, duration=duration),
                    color=0x57F287)
                await interaction.edit_original_response(embed=success_embed)

                message_author_id = message_infos[2]
                message_content = message.embeds[0].description.replace('⠀', '')
                staff_channel = self.client.get_channel(config["channels"]["actions"])

                line_image = discord.File("images/line.png")
                log_embed = discord.Embed(
                    title=f"{config["emojis"]["trash_red"]} "+translator.translate(staff_channel.guild.preferred_locale.value, "log.actions.delete_log_embed.title"),
                    description=translator.translate(staff_channel.guild.preferred_locale.value, "log.actions.delete_log_embed.description", deleted_by=interaction.user.id, message_author=message_author_id, instances=instance_count),
                    color=0xED4245)
                content_embed = discord.Embed(
                    title=f"{config["emojis"]["file_text_red"]} "+translator.translate(staff_channel.guild.preferred_locale.value, "log.actions.delete_log_content_embed.title"),
                    description=f"```\n{message_content}```",
                    color=0xED4245)
                content_embed.set_image(url="attachment://line.png")
                log_embed.set_image(url="attachment://line.png")

                await staff_channel.send(embeds=[log_embed, content_embed], files=[line_image])
            else:
                database_error_embed = discord.Embed(
                    title=f"{config["emojis"]["x_circle_red"]} "+translator.translate(interaction.locale.value, "menu.delete_message.database_error_embed.title"),
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