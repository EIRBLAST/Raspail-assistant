import discord
from class_file import *
from discord.ext import commands
from discord_slash import SlashCommand , cog_ext, SlashContext ,ComponentContext
from discord_slash.utils.manage_components import create_select,create_button, create_select_option, create_actionrow,wait_for_component
from discord_slash.model import ButtonStyle

class GroupSelect(commands.Cog):
    def __init__(self, client:RaspailAssistant):
        self.client = client
        self.numbers =[   client.get_emoji(838150929261658183) #1
            ,client.get_emoji(838150930385600563) #2
            ,client.get_emoji(838150932466106378) #3
            ,client.get_emoji(838150934508732467) #4
            ,client.get_emoji(838150935267377234) #5
            ,client.get_emoji(838150936476123147) #6
            ,client.get_emoji(838150937582632971) #7
            ,client.get_emoji(838150939160477707) #8
            ,client.get_emoji(838150940284551218) #9
            ,client.get_emoji(838398109004333066) #10
            ,client.get_emoji(886502374376624138) #11
            ,client.get_emoji(886502374238208031) #12
            ,client.get_emoji(886502373944602655) #13
        ]
        self.groups = [
            886513013186777119, #group 1
            886513048456679445, #group 2
            886513073731547147, #group 3
            886513097949478933, #group 4
            886513129402548255, #group 5
            886513156300623924, #group 6
            886513180803751946, #group 7
            886513202706391071, #group 8
            886513229801590795, #group 9
            886513260285820978, #group 10
            886513292468715521, #group 11
            886513325083615252, #group 12
            886513351788728350, #group 13
        ]
    @cog_ext.cog_slash(name="groupe",description='te permet de selectionner ton groupe de colle',guild_ids= [879451596247933039])
    async def group_(self,ctx:SlashContext):
        role_list:List[discord.Role] = [ctx.guild.get_role(role) for role in self.groups]
        embed = discord.Embed(title="Selectionne le groupe dans lequel tu te trouve")
        embed.set_image(url='https://www.personal.psu.edu/afr3/blogs/siowfa13/stock-photo-small-group-of-smiling-business-people-standing-together-on-white-background-141633655.jpg')
        #create selection object
        select = create_select(
        options=[
            create_select_option(f"Groupe {group+1}", value=f"{group}", emoji=self.numbers[group])
            for group in range(12)
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
        groupe = int(select_ctx.selected_options[0])
        #add user to database
        await self.client.database.add_user(ctx.author.id,groupe)
        #give the role to the person
        Role:discord.Role = ctx.guild.get_role(self.groups[groupe])
        #get member
        member:discord.Member = ctx.guild.get_member(ctx.author.id)
        
        #remove old group if any
        for role in member.roles:
            if role in role_list:
                await member.remove_roles(role)
        
        #add the right role
        await member.add_roles(Role,reason='groupe command')
        
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
    @cog_ext.cog_slash(name="TEST",description='Groupe',guild_ids= [879451596247933039])
    @commands.has_role("Admins")
    async def groupid(self,ctx:SlashContext):
        """
        string = '['
        for role in ctx.guild.roles:
            string += f'{role.id},'
        string += ']'
        await ctx.send(content=string)
        """
        for role in ctx.guild.roles:
            await ctx.send(f'{role.name}|{role.id}')
def setup(bot:RaspailAssistant):
    bot.add_cog(GroupSelect(bot))