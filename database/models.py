from aiomysql import Pool
from database import get_pool

global_channels = "global_channels"
message_ids     = "message_ids"
message_infos   = "message_infos"
user_roles      = "user_roles"
mutes           = "mutes"

class GlobalChannel:
    def __init__(self, channel_id: int = None, guild_id: int = None):
        self.channel_id = channel_id
        self.guild_id = guild_id
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
                    self.setting_invite = result[3]
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

    async def update(self, setting_invite: int = None):
        if setting_invite is not None:
            self.setting_invite = setting_invite
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"UPDATE `{global_channels}` SET `setting_invite` =  %s WHERE `guild_id` = %s", (self.setting_invite, self.guild_id,))
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

    async def len(self) -> int:
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT COUNT(*) FROM `{global_channels}`")
                result = await cursor.fetchone()
                                   
        pool.close()
        await pool.wait_closed()
        return result[0]
    
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

    async def add_info(self, uuid:str, message_id: int, channel_id: int, author_id: int):
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"INSERT INTO `{message_infos}` (`uuid`, `original_message_id`, `original_channel_id`, `author_id`) VALUES (%s, %s, %s, %s)", (uuid, message_id, channel_id, author_id))
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

    async def get_infos(self, uuid:str) -> dict:
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT `original_message_id`, `original_channel_id`, `author_id` FROM `{message_infos}` WHERE uuid = %s", (uuid,))
                result = await cursor.fetchone()
                    
        pool.close()
        await pool.wait_closed()
        return result
    
    async def len(self) -> int:
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT COUNT(DISTINCT `uuid`) FROM `{message_ids}`")
                result = await cursor.fetchone()
                                   
        pool.close()
        await pool.wait_closed()
        return result[0]
    
class UserRole:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.role = None
        self.display_role = None
        self.stored = False

    async def load(self):
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM `{user_roles}` WHERE `user_id`= %s", self.user_id)
                result = await cursor.fetchone()
                if result:
                    self.display_role = result[2]
                    self.role = result[1]
                    self.stored = True
                else:
                    self.stored = False

        pool.close()
        await pool.wait_closed()
        return self
    
    async def change(self, role: str, display_role: str = None):
        self.role = role
        if display_role:
            self.display_role = display_role
        else:
           self.display_role = role
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                if self.stored == False:
                    await cursor.execute(f"INSERT INTO `{user_roles}` (`user_id`, `role`, `display_role`) VALUES (%s, %s, %s)", (self.user_id, self.role, self.display_role))
                else:
                    await cursor.execute(f"UPDATE `{user_roles}` SET `role` =  %s, `display_role` = %s WHERE `user_id` = %s", (self.role, self.display_role, self.user_id))

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
                await cursor.execute(f"SELECT `user_id`, `role`, `display_role` FROM `{user_roles}`")
                result = [{"user_id": row[0], "role": row[1], "display_role": row[2]} for row in await cursor.fetchall()]

        pool.close()
        await pool.wait_closed()
        return result

    async def len(self) -> int:
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT COUNT(*) FROM `{user_roles}`")
                result = await cursor.fetchone()
                                   
        pool.close()
        await pool.wait_closed()
        return result[0]

class Mutes:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.staff_id = 8
        self.reason = None
        self.exipires_at = None
        self.stored = False

    async def load(self):
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM `{mutes}` WHERE `user_id`= %s", self.user_id)
                result = await cursor.fetchone()
                if result:
                    self.staff_id = result[1]
                    self.reason = result[2]
                    self.exipires_at = result[3]
                    self.stored = True
                else:
                    self.stored = False

        pool.close()
        await pool.wait_closed()
        return self
    
    async def add(self, staff_id: int, reason: str, expires_at):
        self.staff_id = staff_id
        self.reason = reason
        self.exipires_at = expires_at
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"INSERT INTO `{mutes}` (`user_id`, `staff_id`, `reason`, `expires_at`) VALUES (%s, %s, %s, %s)", (self.user_id, self.staff_id, self.reason, self.exipires_at))


        pool.close()
        await pool.wait_closed()
        return self
    
    async def remove(self):
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"DELETE FROM `{mutes}` WHERE `user_id`= %s", (self.user_id))
                
        pool.close()
        await pool.wait_closed()
        return self    
    
    async def list(self) -> list:
        pool: Pool = await get_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT `user_id`, `expires_at` FROM `{mutes}` WHERE `expires_at` IS NOT NULL")
                result = [{"user_id": row[0], "expires_at": row[1]} for row in await cursor.fetchall()]

        pool.close()
        await pool.wait_closed()
        return result