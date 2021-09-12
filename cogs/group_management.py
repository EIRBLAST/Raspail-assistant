import discord
from class_file import *
from discord.ext import commands
from discord_slash import SlashCommand , cog_ext, SlashContext ,ComponentContext
from discord_slash.utils.manage_components import create_select,create_button, create_select_option, create_actionrow,wait_for_component
from discord_slash.model import ButtonStyle

class GroupSelect(commands.Cog):
    def __init__(self, client:RaspailAssistant):
        self.client = client
        self.numbers =[   client.get_emoji(838150929261658183)
            ,client.get_emoji(838150930385600563)
            ,client.get_emoji(838150932466106378)
            ,client.get_emoji(838150934508732467)
            ,client.get_emoji(838150935267377234)
            ,client.get_emoji(838150936476123147)
            ,client.get_emoji(838150937582632971)
            ,client.get_emoji(838150939160477707)
            ,client.get_emoji(838150940284551218)
            ,client.get_emoji(838398109004333066)
            ,client.get_emoji(886502374376624138)
            ,client.get_emoji(886502374238208031)
            ,client.get_emoji(886502373944602655)
        ]
    @cog_ext.cog_slash(name="groupe",description='te permet de selectionner ton groupe de colle')
    async def group_(self,ctx:SlashContext):
        embed = discord.Embed(title="Selectionne le groupe dans lequel tu te trouve")
        embed.set_image(url='https://www.personal.psu.edu/afr3/blogs/siowfa13/stock-photo-small-group-of-smiling-business-people-standing-together-on-white-background-141633655.jpg')
        #create selection object
        select = create_select(
        options=[
            create_select_option(f"Groupe {group+1}", value=f"{group}", emoji=f"{self.numbers[group]}")
            for group in range(13)
        ],
        placeholder="Utilise ce menu déroulant pour séléctionner ton groupe ",
        min_values=1, # the minimum number of options a user must select
        max_values=1  # the maximum number of options a user can select
        )
        action_row = create_actionrow(select)
        
        #send the embed and selection
        await ctx.send(embed=embed,components=[action_row])

        #wait for selection
        select_ctx: ComponentContext = await wait_for_component(self.client, components=action_row)
        
        #retrive selected group
        groupe = int(select_ctx.selected_options)
        #add user to database
        await self.client.database.add_user(ctx.author.id,groupe)
        #give the role to the person
        #/////////////////////////
        #create the reponse button
        buttons = [
            create_button(
                style=ButtonStyle.green,
                label=f"Tu es dans le groupe {groupe+1}",
                disabled=True,
                emoji=self.numbers[groupe]
            ),
        ]
        #respond to the orginal message
        await select_ctx.edit_origin(embed=embed,components=[create_actionrow(*buttons)])
    @cog_ext.cog_slash(name="TEST",description='Groupe')
    async def groupid(self,ctx:commands.Context):
        string = '['
        for role in ctx.guild.roles:
            string += f'{role.id},'
        string += ']'
        await ctx.send(content=string)
    
def setup(bot:RaspailAssistant):
    bot.add_cog(GroupSelect(bot))