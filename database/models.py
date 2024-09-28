from aiomysql import Pool
from database import get_pool
from datetime import datetime, timedelta

global_channels = "global_channels"
message_ids = "message_ids"
user_roles = "user_roles"

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
                await cursor.execute(f"SELECT `channel_id`, `guild_id`, `invite` FROM `{global_channels}`")
                results = await cursor.fetchall()
                
                channels = []
                for result in results:
                    channel_id = result[0]
                    guild_id = result[1]
                    invite = result[2]
                    channels.append({
                        'channel_id': channel_id,
                        'guild_id': guild_id,
                        'invite': invite
                    })
                    
        pool.close()
        await pool.wait_closed()
        return channels
    
class GlobalMessage:
    def __init__(self):
        pass
  
    async def add(self, uuid:str, message_id: int, channel_id: int):
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"INSERT INTO `{message_ids}` (`uuid`, `message_id`, `channel_id`) VALUES (%s, %s, %s)", (uuid, message_id, channel_id))
        pool.close()
        await pool.wait_closed()
        return self
    
    async def get_uuid(self, message_id:int) -> str:
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT `uuid` FROM `{message_ids}` WHERE `message_id` = %s", (message_id))
                result = await cursor.fetchone()

        pool.close()
        await pool.wait_closed()
        if result:
            return result[0]
        else: 
            return None
    
    async def get(self, uuid:str) -> dict:
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT `message_id`, `channel_id` FROM `{message_ids}` WHERE uuid = %s", (uuid,))
                result = [{"message_id": row[0], "channel_id": row[1]} for row in await cursor.fetchall()]
                    
        pool.close()
        await pool.wait_closed()
        return result
    
class UserRole:
    def __init__(self, user_id):
        self.user_id = user_id
        self.role = None
        self.stored = False

    async def load(self):
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM `{user_roles}` WHERE `user_id`= %s", self.user_id)
                result = await cursor.fetchone()
                if result:
                    self.role = result[1]
                    self.stored = True
                else:
                    self.stored = False

        pool.close()
        await pool.wait_closed()
        return self
    
    async def change(self, role: str):
        self.role = role
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                if self.stored == False:
                    await cursor.execute(f"INSERT INTO `{user_roles}` (`user_id`, `role`) VALUES (%s, %s)", (self.user_id, self.role))
                else:
                    await cursor.execute(f"UPDATE `{user_roles}` SET `role` = %s WHERE `user_id` = %s", (self.role, self.user_id))

        pool.close()
        await pool.wait_closed()
        return self
    
    async def remove(self):
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"DELETE FROM `{user_roles}` WHERE `user_id`= %s", (self.user_id))
                
        pool.close()
        await pool.wait_closed()
        return self    
    
    async def list(self) -> list:
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT `user_id`, `role` FROM `{user_roles}`")
                result = [{"user_id": row[0], "role": row[1]} for row in await cursor.fetchall()]

        pool.close()
        await pool.wait_closed()
        return result