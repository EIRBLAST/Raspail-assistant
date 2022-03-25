import io
import time
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
from tools import daygrade

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
        user_role_mentionner = list(filter(lambda r: r.name == "Groupe "+ str(user_grp), ctx.channel.guild.roles ))[0].mention

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
        """
            Envoie le planning de chaque groupe
        """
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
        """
            T'envoie l'emploi du temps et coloscope en version papier.
        """
        edt = discord.File(open("datas/edt.jpg", "rb"), 'edt.png')
        colloscope = discord.File(open("datas/colloscope.jpg", "rb"), 'colloscope.png')
        await ctx.send(files=[edt, colloscope],content='Voici pour toi :) !')
    
    # Permet de voir le planning d'un groupe jusquà 6 semaines à l'avance
    @cog_ext.cog_slash(name="oracle",description='T\'envoie le planning d\'un groupe jusqu\'à 6 semaines à l\'avance.',guild_ids= [879451596247933039])
    async def oracle(self,ctx:SlashContext):
        """
            T'envoie le planning d'un groupe jusqu'à 6 semaines à l'avance.
        """

        print("Bon je commence")

        today = datetime.date.today()
        next_mondays = [today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(days=i*7) for i in range(1,7)]

        print("Heooo ?")
        if not await self.client.database.user_in_database(ctx.author.id):
            await ctx.send('Utilise /groupe avant tout ;)')
            return
        user_grp = (await self.client.database.get_user_info(ctx.author.id))["group"] + 1
        # user_role_mentionner = list(filter(lambda r: r.name == "Groupe "+ str(user_grp), ctx.channel.guild.roles ))[0].mention

        print("Heooo2 ?")
        # Selection par l'utilisateur de la semaine à afficher

        embed = discord.Embed(title="Selectionne la semaine", description="", color=0x00ff00)
        embed.set_image(url="https://image.shutterstock.com/image-photo/male-fortune-teller-crystal-ball-600w-2023087094.jpg")
        selection = create_select(
            options = [create_select_option("Semaine du lundi " + d.strftime("%d/%m/%Y"), value=d.strftime("%d/%m/%Y")) for d in next_mondays],
            placeholder = "Utilise ce menu déroulant pour séléctionner les semaines à afficher",
            min_values= 1,
            max_values = 6
        )
        
        action_row = create_actionrow(selection)
        await ctx.send(embed=embed, components=[action_row])

        print('hey')
        select_ctx: ComponentContext = await wait_for_component(self.client, components=action_row,check=lambda c: ctx.author == c.author)
        
        slected_weeks = select_ctx.selected_options
        print("Selected weeks:", slected_weeks)

        #create the reponse button
        buttons = [
            create_button(
                style=ButtonStyle.green,
                label=f"C'est noté maxi bg!",
                disabled=True,
            ),
        ]
        #respond to the orginal message
        await select_ctx.edit_origin(embed=embed,components=[create_actionrow(*buttons)])

        # Send plannings

        for week in slected_weeks:
            # Start the creation of a timetable
            monday = datetime.datetime.strptime(week, "%d/%m/%Y")
            print("monday:",monday)

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
                colums.append(timetable_I.generate_column(blocks, [event["timedelta"]["hours"] - 8 for event in events], header = data_io.DAYS[day] + " \n" + (monday + datetime.timedelta(days=day)).strftime("%d/%m/%Y")))


            # Generate the image
            image = timetable_I.generate_timetable(colums)

            #send the planning
            buffer_output = io.BytesIO()
            image.save(buffer_output, format='PNG')
            buffer_output.seek(0)
            file = discord.File(buffer_output, 'edt.png')
            #send the file
            await ctx.send(content=f"Voila pour toi l'edt de la semaine du {week} :) !",file=file)
            time.sleep(0.2)
    
    # Send the score of the current day:
    @cog_ext.cog_slash(name="score",description='T\'envoie le score de la journée en cours.',guild_ids= [879451596247933039])
    async def score(self,ctx:SlashContext):
        score = daygrade.score(datetime.date.today(), (await self.client.database.get_user_info(ctx.author.id))["group"] + 1)

        # Send the score
        await ctx.send(f"Le score de ta journée est de  {score[0]*20}/20")        

def setup(bot:RaspailAssistant):
    bot.add_cog(PlanningCommands(bot))
