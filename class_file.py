import discord
import aioredis
import os
from discord.ext import commands

class database():
    def __init__(self):
        #create a pool of connection
        #not nessesary but I don't want to read the doc again
        self.redis_pool = aioredis.ConnectionPool.from_url(url=REDIS_URL)
         
    async def add_user(self,user_id:int,group:int) -> None:
        redis_con = aioredis.Redis(connection_pool=self.redis_pool)
        #store the data
        key = str(user_id)
        await redis_con.execute_command('set',key,group)
        #set a time limit before the data is dumped
    async def user_in_database(self,user_id:int) -> bool:
        #get a connection 
        redis_con = aioredis.Redis(connection_pool=self.redis_pool)
        #return the bool
        key = str(user_id)
        return bool(await redis_con.exists(key))
    async def get_group(self,user_id:int) -> int:
        #get a connection 
        redis_con = aioredis.Redis(connection_pool=self.redis_pool)
        #return the group dict
        key = str(user_id)
        data = await redis_con.execute_command('get',key)
        return data

#client class overloaded with database features
class RaspailAssistant(commands.Bot):
    def __init__(self):
        # Setting help_command=False ensures that discord.py does not create a !help command.
        # Enabling self_bot ensures that the bot does not try and parse messages that start with "!".
        super().__init__(command_prefix="!", self_bot=True, help_command=False, intents= discord.Intents.default())
        #database object
        self.database = database()
        