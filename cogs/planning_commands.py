import io
from time import time
import datetime

from discord.ext import commands
from discord_slash import ComponentContext, SlashCommand, SlashContext, cog_ext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import (create_actionrow,
                                                   create_button,
                                                   create_select,
                                                   create_select_option,
                                                   wait_for_component)

from class_file import *
from tools import data_io
from tools import timetable
import tools

class PlanningCommands(commands.Cog):
    def __init__(self, client:RaspailAssistant):
        self.client = client

    @cog_ext.cog_slash(name="planning",description='T\'envoie ton planning de la semaine ou de la semaine prochaine si on est la weekend :)',guild_ids= [879451596247933039])
    async def send_planning(self,ctx:SlashContext):

        if not await self.client.database.user_in_database(ctx.author.id):
            await ctx.send('Utilise /groupe avant tout ;)')
            return
        today = datetime.date.today()
        user_grp = (await self.client.database.get_user_info(ctx.author.id))["group"] + 1
        user_role_mentionner = filter(lambda r: r.name == "Groupe "+ str(user_grp), ctx.channel.guild.roles )[0].mention

        if today.weekday() < 5:
            monday = today - datetime.timedelta(days = today.weekday())
        else:
            monday = today - datetime.timedelta(days = today.weekday()) + datetime.timedelta(days = 7)


        # Start the creation of a timetable

        timetable_I = timetable.timtable_imager(timetable_dimention_width = 6)

        colums = []
        for day in range(0, 6):
            events = data_io.get_events_of_the_day(monday + datetime.timedelta(days=day), user_grp)
            blocks = []
            for event in events:
                if event.get("type", "") == "colle":
                    color =  "grey"
                else:
                    color =  timetable.get_color(event.get("nom", event.get("subject", "")).split(" - ")[0].lower())

                lines = [
                    {
                        "content": event.get("subject", "").upper(),
                        "font": "bold",
                        "align": ""
                    },
                    {
                        "content": event.get("room","") or "salle inconue",
                        "font": "regular",
                        "align": ""
                    }
                ]

                if event.get("teatcher", ""):
                    lines.append({
                        "content": event.get("teatcher", ""),
                        "font": "regular",
                        "align": ""
                    })
                
                height =  event["duration"]["hours"]
                
                blocks.append(timetable_I.generate_block(lines, height, color))
            colums.append(timetable_I.generate_column(blocks, [event["timedelta"]["hours"] - 8 for event in events], header = data_io.DAYS[day]))


        # Generate the image
        image = timetable_I.generate_timetable(colums)

        #send the planning
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)
        file = discord.File(buffer_output, 'edt.png')
        #send the file
        await ctx.send(content=f"Voila pour toi l'edt du {user_role_mentionner} :) !",file=file)

    @cog_ext.cog_slash(name="now",description='T\'envoie le planning de chaque groupe ',guild_ids= [879451596247933039])
    async def send_planning_now(self,ctx:SlashContext):
        nb_of_groups = 12
        today = datetime.date.today()

        if today.weekday() > 4:
            await ctx.send(content="Tu es en weekend, tu ne peux pas faire ça :).")
            return 


        events_of_grp = lambda i: data_io.get_events_of_the_day(today, i)
        timetable_I = timetable.timtable_imager(timetable_dimention_width = nb_of_groups)

        columns = []
        for grp in range(1,nb_of_groups+1):
            events = events_of_grp(grp)
            blocks = []
            for event in events:

                if event.get("type", "") == "colle":
                    color =  "grey"
                else:
                    color =  timetable.get_color(event.get("nom", event.get("subject", "")).split(" - ")[0].lower())

                lines = [
                    {
                        "content": event.get("subject", "").upper(),
                        "font": "bold",
                        "align": ""
                    },
                    {
                        "content": event.get("room","") or "salle inconue",
                        "font": "regular",
                        "align": ""
                    }
                ]

                if event.get("teatcher", ""):
                    lines.append({
                        "content": event.get("teatcher", ""),
                        "font": "regular",
                        "align": ""
                    })
                
                height =  event["duration"]["hours"]
                
                blocks.append(timetable_I.generate_block(lines, height, color))
            
            columns.append(timetable_I.generate_column(blocks, [event["timedelta"]["hours"] - 8 for event in events], "Groupe: " + str(grp)))


        img = timetable_I.generate_timetable(columns)
        #send the planning
        buffer_output = io.BytesIO()
        img.save(buffer_output, format='PNG')
        buffer_output.seek(0)
        file = discord.File(buffer_output, 'edt.png')
        #send the file
        await ctx.send(content=f"Voila pour toi voici le planning d'aujourd'hui ({today.strftime('%d/%m/%Y')}) :) !",file=file)
    

    @cog_ext.cog_slash(name="papier",description='T\'envoie l\'emploi du temps et coloscope en version papier.',guild_ids= [879451596247933039])
    async def papier(self,ctx:SlashContext):
        edt = discord.File(open("datas/edt.jpg", "rb"), 'edt.png')
        colloscope = discord.File(open("datas/colloscope.jpg", "rb"), 'colloscope.png')
        await ctx.send(files=[edt, colloscope],content='Voici pour toi :) !')
        
def setup(bot:RaspailAssistant):
    bot.add_cog(PlanningCommands(bot))
