import discord
import aioredis
import os
import json
from typing import List
from discord.ext import commands

REDIS_URL = os.environ['REDIS_URL']

class database():
    """[Wrapper for redis database]
    """
    def __init__(self):
        #create a pool of connection
        #not nessesary but I don't want to read the doc again
        self.redis_pool = aioredis.ConnectionPool.from_url(url=REDIS_URL)
         
    async def add_user(self,user_id:int,group:int) -> None:
        """[Add user to the database]

        Args:
            user_id (int): [the unique discord ID]
            group (int): [The colle groupe ID]
        """
        redis_con = aioredis.Redis(connection_pool=self.redis_pool)
        #store the data
        key = str(user_id)
        
        #create the user_info dict
        user_info = {
            'group':group,
            'reminder_planning':None,
            'reminder_colle':None
        }
        
        user_info = json.dumps(user_info)
        
        await redis_con.execute_command('set',key,user_info)
        #set a time limit before the data is dumped
    async def user_in_database(self,user_id:int) -> bool:
        """[Check for the existence of user data]

        Args:
            user_id (int): [the unique discord ID]

        Returns:
            bool: [Whether information exists or not]
        """
        #get a connection 
        redis_con = aioredis.Redis(connection_pool=self.redis_pool)
        #return the bool
        key = str(user_id)
        return bool(await redis_con.exists(key))
    async def get_user_info(self,user_id:int) -> dict:
        """[summary]

        Args:
            user_id (int): [the unique discord ID]

        Returns:
            dict: [the user informations]
        """
        #get a connection 
        redis_con = aioredis.Redis(connection_pool=self.redis_pool)
        #return the group dict
        key = str(user_id)
        data = await redis_con.execute_command('get',key)
        return json.loads(data)

#client class overloaded with database features
class RaspailAssistant(commands.Bot):
    def __init__(self):
        # Setting help_command=False ensures that discord.py does not create a !help command.
        # Enabling self_bot ensures that the bot does not try and parse messages that start with "!".
        super().__init__(command_prefix="!",self_bot=True, intents= discord.Intents.default())
        #database object
        self.database:database = database()
        #list of server for slash command
        self.guild_ids:List[int] = [ 879451596247933039 ]
        