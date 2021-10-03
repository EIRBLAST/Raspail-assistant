import discord
from discord.ext import commands, tasks
import random 
import json

class Presence(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.sentenses = json.load(open("datas/presence_sentenses.json", "r"))
        self.update_presence.start()
        print("Presence updater inir")
    
    
    @tasks.loop(seconds=10)
    async def update_presence(self):
        activity_=random.choice(self.sentenses)
        await self.client.change_presence(activity=discord.Game(name=activity_))
    
    @update_presence.before_loop
    async def before_update(self):
        print('waiting for client to load ...')
        await self.client.wait_until_ready()

    def cog_unload(self):
        self.update_presence.cancel()

def setup(bot):
    bot.add_cog(Presence(bot))
    