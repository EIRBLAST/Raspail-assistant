import discord
from discord.ext import commands
from discord_slash import SlashCommand , cog_ext, SlashContext ,ComponentContext
from class_file import *

import json

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

    return datas["informatique"][column_index]



class PlanningCommands(commands.Cog):
    def __init__(self, client:RaspailAssistant):
        self.client = client

    @cog_ext.cog_slash(name="planning",description='T\'envoie ton planning de la semaine ou de la semaine prochaine si on est la weekend :)',guild_ids= [879451596247933039])
    async def send_planning(self,ctx:SlashContext):
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

def setup(bot:RaspailAssistant):
    bot.add_cog(PlanningCommands(bot))