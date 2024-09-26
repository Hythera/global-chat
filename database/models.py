from aiomysql import Pool
from database import get_pool
from datetime import datetime, timedelta

global_channels = "global_channels"

class GlobalChannel:
    def __init__(self, channel_id: int = None, guild_id: int = None, invite: str = None):
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.invite = invite
        self.stored = False

    async def load(self):
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                if self.channel_id:
                    await cursor.execute(f"SELECT * FROM `{global_channels}` WHERE `channel_id`= %s", self.channel_id)
                else:
                    await cursor.execute(f"SELECT * FROM `{global_channels}` WHERE `guild_id`= %s", self.guild_id)
                result = await cursor.fetchone()
                if result:
                    self.channel_id = result[0]
                    self.guild_id = result[1]
                    self.invite = result[2]
                    self.stored = True
                else:
                    self.stored = False

        pool.close()
        await pool.wait_closed()
        return self
    
    async def add(self, invite: str = None):
        self.invite = invite
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"INSERT INTO `{global_channels}` (`channel_id`, `guild_id`, `invite`) VALUES (%s, %s, %s)", (self.channel_id, self.guild_id, self.invite))
        pool.close()
        await pool.wait_closed()
        return self
    
    async def remove(self):
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"DELETE FROM `{global_channels}` WHERE `channel_id`= %s", (self.channel_id,))
        pool.close()
        await pool.wait_closed()
        return self
    
    async def get_all_channels(self) -> dict:
        pool: Pool = await get_pool()
        channels = {}
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT `channel_id`, `model` FROM `{ai_channels_table}` WHERE `guild_id` = %s", (self.guild_id,))
                results = await cursor.fetchall()
                
                for result in results:
                    channel_id = result[0]
                    model = result[1]
                    channels[channel_id] = {
                        'model': model
                    }
                    
        pool.close()
        await pool.wait_closed()
        return channels