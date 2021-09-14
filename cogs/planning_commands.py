from discord.ext import commands
from discord_slash import SlashCommand , cog_ext, SlashContext ,ComponentContext
from discord_slash.utils.manage_components import create_select,create_button, create_select_option, create_actionrow,wait_for_component
from discord_slash.model import ButtonStyle
from class_file import *
from PIL import Image, ImageDraw,ImageFont

import json
import io
import discord

from datetime import datetime, timedelta, date
from time import time


datas = json.load(open("datas/colloscope.json", "r"))


DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]


def get_events_of_the_day(day:datetime.date,grp:int) -> list:
    """Return a list of events of the day `day`od group `grp`

    Args:
        day (datetime.date): The day
        grp (int): The group
    
    Returns:
        [list]: A list of events  
    """    
    monday = day - timedelta(days = day.weekday())
    column_index = datas["mondays"].index(monday.strftime("%d/%m/%Y")) 

    events = []
    for line in datas["planning"]:
        if line["grps"][column_index] == int(grp) and line["timedelta"]["days"] == day.weekday():
            events.append(line)

    events.sort(key= lambda line : timedelta(**line["timedelta"]))
    
    return events

def get_week_parity(day):
    monday = day - timedelta(days = day.weekday())
    column_index = datas["mondays"].index(monday.strftime("%d/%m/%Y"))

    return datas["weeknumber"][column_index] % 2

def informatique_parity(day):
    monday = day - timedelta(days = day.weekday())
    column_index = datas["mondays"].index(monday.strftime("%d/%m/%Y"))
    res = datas["informatique"][column_index]
    return 'pair'*(res == 'B') + 'impair'*(res == 'A') + 'entier'*(res == 'C')


def IsParite(parite:str,group_number:int,week_parite:int) ->bool:
    """this function compute if the group attend the course

    Args:
        parite (str): the parite string
        group_number (int): the group id
        week_parite (int): the week parity

    Returns:
        bool: wether the group attend or not
    """
    if parite == 'entier' : return True
    if parite == 'pair':
        return group_number%2 != week_parite
    elif parite == 'impair':
        return group_number%2 == week_parite
    else:
        return True

class PlanningCommands(commands.Cog):
    def __init__(self, client:RaspailAssistant):
        self.client = client

    @cog_ext.cog_slash(name="planning",description='T\'envoie ton planning de la semaine ou de la semaine prochaine si on est la weekend :)',guild_ids= [879451596247933039])
    async def send_planning(self,ctx:SlashContext):
        if not await self.client.database.user_in_database(ctx.author.id):
            await ctx.send('utilise /groupe avant tout ;)')
            return
        today = date.today()
        user_grp = (await self.client.database.get_user_info(ctx.author.id))["group"] + 1

        if today.weekday() < 5:
            monday = today - timedelta(days = today.weekday())
        else:
            monday = today - timedelta(days = today.weekday()) + timedelta(days = 7)

        column = datas["mondays"].index(monday.strftime("%d/%m/%Y")) 

        events = []
        for line in datas["planning"]:
            if line["grps"][column] == user_grp :
                events.append(line)
        
        events.sort(key= lambda line : timedelta(**line["timedelta"]))

        message = f'La semaine du lundi {monday.strftime("%d/%m/%Y")}:'
        for event in events:
            message += f"\n\t - Tu as {event['type']} {('de ' + event['subject'] + ' ') if event['type'] == 'colle' else ''}avec {event['teatcher']} le {DAYS[event['timedelta']['days']]} à {event['timedelta']['hours']}h {' dans la salle ' + event['room'] + '.' if event['room'] else '.'}".format(event = event)
        
        await ctx.send(content=message)
    @cog_ext.cog_slash(name="edt",description='T\'envoie l\'emploie du temp du jour choisis',guild_ids= [879451596247933039])
    async def edt_image(self,ctx:SlashContext):
        def check(context:ComponentContext):
            return ctx.author == context.author
        if not await self.client.database.user_in_database(ctx.author.id):
            await ctx.send('utilise /groupe avant tout ;)')
            return
        #get group
        groupe = (await self.client.database.get_user_info(ctx.author.id))["group"] + 1
        #compute week------------------#
        today = date.today()
        if today.weekday() < 5:
            monday = today - timedelta(days = today.weekday())
        else:
            monday = today - timedelta(days = today.weekday()) + timedelta(days = 7)
        #week parity
        week_parity = get_week_parity(monday)
        #-----------------------------#

        #-----------------------------#
        #declare constant
        X_LENGHT = 300
        Y_LENGHT = 100
        DX = 50

        with open('datas/edt.json','r') as item:
            edt = json.load(item)
            edt = edt['edt']
        
        select = create_select(
        options=[
            create_select_option(f"{jour}", value=f"{i}", emoji='📅')
            for i,jour in enumerate(DAYS)
        ],
        placeholder="Utilise ce menu déroulant pour séléctionner le jour ",
        min_values=1, # the minimum number of options a user must select
        max_values=1  # the maximum number of options a user can select
        )
        action_row = create_actionrow(select)
        embed= discord.Embed(title='Sélectione un jour')
        embed.set_image(url='https://media.gettyimages.com/photos/happy-student-in-class-picture-id539246041?s=612x612')
        #send the embed and selection
        await ctx.send(embed=embed,components=[action_row])

        #wait for selection
        select_ctx: ComponentContext = await wait_for_component(self.client, components=action_row,check=check)
        
        jour_index = int(select_ctx.selected_options[0])
        jour = edt[jour_index]
        
        #create the reponse button
        buttons = [
            create_button(
                style=ButtonStyle.green,
                label=f"Tu as Sélectioner un jour",
                disabled=True,
                emoji='📅'
            ),
        ]
        #respond to the orginal message
        await select_ctx.edit_origin(embed=embed,components=[create_actionrow(*buttons)])
        
        im =  Image.new('RGB', (X_LENGHT + DX, Y_LENGHT*10), color = 'white')
        fnt = ImageFont.truetype('datas/Roboto-Regular.ttf', 20)
        fnt_bold = ImageFont.truetype('datas/Roboto-Bold.ttf', 25)
        fnt_high = ImageFont.truetype('datas/Roboto-Bold.ttf', 25)
        #LIGNE VERTICAL
        Ldraw = ImageDraw.Draw(im)
        points = [
                (DX,0 ), 
                (DX,Y_LENGHT *10)
            ]
        Ldraw.line(points, fill ="black", width = 1)

        #heures
        draw = ImageDraw.Draw(im)
        for i in range(8,18):
            x_position = 0
            y_position = Y_LENGHT * (i - 8)
            draw.text((x_position,y_position), f'{i}h', font=fnt_high, fill=(0, 0, 0))

        #cours
        liste_cours = [cours for cours in jour['cours'] if IsParite(cours['parite'],groupe,week_parity) and cours['nom'] != 'Informatique']
        if IsParite(informatique_parity(monday),groupe,week_parity) and {"nom":"Informatique","salle":"INFO","heures":[10,11],"parite":"INFO"} in jour['cours']:
            if informatique_parity(monday) == 'entier': salle = 'B411'
            else : salle = 'B401'
            liste_cours.append({"nom":"Informatique","salle":salle,"heures":[10,11],"parite":"INFO"})
        liste_image = []
        for i,cours in enumerate(liste_cours):
            #block size
            size = len(cours['heures'])
            #bloc color
            if cours["nom"] == 'Physique':
                color = "purple"
            elif cours['nom'] == 'Math':
                color = "green"
            elif cours['nom'] == 'Anglais':
                color = 'blue'
            elif 'SII' in cours['nom']:
                color = 'yellow'
            elif cours['nom'] == 'Français':
                color = 'pink'
            elif cours['nom'] == 'Informatique':
                color = 'cyan'
            elif cours['nom'] == 'DS':
                color = 'red'
            #bloc text
            TOP_TEXT = cours['nom']
            BOTTOM_TEXT = cours['salle'] if 'salle' != None else "XXXX"
            #create bloc
            img = Image.new('RGB', (X_LENGHT,Y_LENGHT*size), color)
            draw = ImageDraw.Draw(img)
            #draw text
            x_position = X_LENGHT//3
            y_position = (Y_LENGHT)*size//3
            draw.text((x_position,y_position)   , TOP_TEXT   , font=fnt_bold, fill=(0, 0, 0))
            draw.text((x_position,y_position+25), BOTTOM_TEXT, font=fnt, fill=(0, 0, 0))
            liste_image.append(img)
        
                
                
        #lignes verticales
        for i in range(11):

            Ldraw = ImageDraw.Draw(im)
            
            points = [
                (0,Y_LENGHT * i), 
                (X_LENGHT+DX,Y_LENGHT *i)
            ]
            
            Ldraw.line(points, fill ="black", width = 1)

        #paste courses
        for i,image in enumerate(liste_cours):
            first_hour = liste_cours[i]['heures'][0] - 1
            im.paste(liste_image[i] ,(DX,Y_LENGHT*(first_hour-7)))

        #colles et TP
        jour = monday + timedelta(days=jour_index)
        events = get_events_of_the_day(jour,groupe)
        for event in events:
            room = event['room'] if event['room'] else '.'
            prof_name = event['teatcher']
            start_hour =event['timedelta']['hours']
            size = 1
            event_name = f"{event['subject']}"
            if event['type'] == 'colle':
                size = 1
                color = 'gray'
            elif event['type'] == 'TIPE':
                size = 2
                color = 'yellow'
            elif event['type'] == 'tp':
                size = 3
                color = 'yellow'
            #create bloc
            img = Image.new('RGB', (X_LENGHT,Y_LENGHT*size), color)
            draw = ImageDraw.Draw(img)
            #draw text
            TOP_TOP_TEXT = event['type']
            TOP_TEXT = event_name
            MIDDLE_TEXT = prof_name
            BOTTOM_TEXT = room
            
            x_position = X_LENGHT //3
            y_position = (Y_LENGHT)*size//3
            
            draw.text((x_position,y_position-25), TOP_TOP_TEXT,font=fnt_bold, fill=(0, 0, 0))
            draw.text((x_position,y_position)   , TOP_TEXT   , font=fnt_bold, fill=(0, 0, 0))
            draw.text((x_position,y_position+25), MIDDLE_TEXT, font=fnt, fill=(0, 0, 0))
            draw.text((x_position,y_position+45), BOTTOM_TEXT, font=fnt, fill=(0, 0, 0))
            #paste the image
            im.paste(img ,(DX,Y_LENGHT*(start_hour-8)))
        
        #add additional lines
        for i,cours in enumerate(liste_cours):
            Ldraw = ImageDraw.Draw(im)
            
            first_heure = liste_cours[i]['heures'][0] - 8
            last_heure = liste_cours[i]['heures'][-1] - 7

            points = [
                (0,Y_LENGHT * first_heure), 
                (X_LENGHT+DX,Y_LENGHT *first_heure)
            ]
            
            
            Ldraw.line(points, fill ="black", width = 1)
            

            points = [
                (0,Y_LENGHT *last_heure), 
                (X_LENGHT+DX,Y_LENGHT *last_heure)
            ]

            
            Ldraw.line(points, fill ="black", width = 1) 
        
        #send the planning
        buffer_output = io.BytesIO()
        im.save(buffer_output, format='PNG')
        buffer_output.seek(0)
        file = discord.File(buffer_output, 'edt.png')
        await ctx.send(file=file,content=f'Voici le planning du {DAYS[jour_index]} {jour.strftime("%d/%m/%Y")}')
        

def setup(bot:RaspailAssistant):
    bot.add_cog(PlanningCommands(bot))