import discord
from class_file import *
from discord.ext import commands
from discord_slash import SlashCommand , cog_ext, SlashContext , utils

class GroupSelect(commands.Cog):
    def __init__(self, client:RaspailAssistant):
        self.client = client

    @cog_ext.cog_slash(name="groupe",description='te permet de selectionner ton groupe de colle')
    async def group_(self,ctx:SlashContext):
        embed = discord.Embed(title="Selectionne le groupe dans lequel tu te trouve")
        
        await ctx.send(embed=embed)

        
def setup(bot:RaspailAssistant):
    bot.add_cog(GroupSelect(bot))