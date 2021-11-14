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

                lines = [
                    {
                        "content": event.get("nom", "") or event.get("subject", ""),
                        "font": "bold",
                        "align": ""
                    },
                    {
                        "content": event.get("salle","") or event.get("salle","") or "salle inconue",
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
                color =  timetable.get_color(event.get("nom", event.get("subject", "")).split(" - ")[0].lower())
                blocks.append(timetable_I.generate_block(lines, height, color))
            
            colums.append(timetable_I.generate_column(blocks, [event["timedelta"]["hours"] - 8 for event in events]))


        # Generate the image
        image = timetable_I.generate_timetable(colums)

        #send the planning
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)
        file = discord.File(buffer_output, 'edt.png')
        #send the file
        await ctx.send(content=f"Voila pour toi l'edt du groupe {user_grp} :) !",file=file)
    

    @cog_ext.cog_slash(name="papier",description='T\'envoie l\'emploie du temps et coloscope en version papier.',guild_ids= [879451596247933039])
    async def papier(self,ctx:SlashContext):
        edt = discord.File(open("datas/edt.jpg", "rb"), 'edt.png')
        colloscope = discord.File(open("datas/colloscope.jpg", "rb"), 'colloscope.png')
        await ctx.send(files=[edt, colloscope],content='Voici pour toi :) !')
        
def setup(bot:RaspailAssistant):
    bot.add_cog(PlanningCommands(bot))
    
    

"""
TODOLIST:

TODO: /now Renvoie pour chaque grp le cours actuel
TODO: /today Renvoie le planning du jour
TODO: /dashboard -> envoie un lien vers une app heroku qui donne l'edt en fontion d'une date choisie + planning de colle maths & physique.
TODO: Presence <-- 
"""
