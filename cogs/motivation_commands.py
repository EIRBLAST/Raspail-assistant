from datetime import date, datetime, timedelta

import humanize
from discord.ext import commands
from discord_slash import ComponentContext, SlashCommand, SlashContext, cog_ext

from tools import data_io


dates = [
        "cesi" : [datetime.strptime("06/04/2022", "%d/%m/%Y"), datetime.strptime("06/04/2022")],
        "EPITA / IPSA / ESME" : [datetime.strptime("09/04/2022"), datetime.strptime("09/04/2022")],
        "Centrale-Supélec": [datetime.strptime("03/05/2022"), datetime.strptime("06/05/2022")],
        "CCINP": [datetime.strptime("09/05/2022"), datetime.strptime("13/05/2022")]
]


def generate_progress_bar(perecent):
    full = "⬛"
    blanck = "⬜"

    full_count = int(perecent * 10)
    blanck_count = 10 - full_count

    return full * full_count + blanck * blanck_count

class PlanningCommands(commands.Cog):
    def __init__(self, client:RaspailAssistant):
        self.client = client

    @cog_ext.cog_slash(name="motivation",description='Te motive (parceque on en a tous besoin', guild_ids= [879451596247933039])
    async def send_planning(self,ctx:SlashContext):
        m = "Voici le contdown jusqu'aux différents concours"
        for concours in dates.keys():
            if date.today() < dates[concours][1]:
                m += "\n\t- " + concours + ": "  +  humanize.naturaltime(dates[concours][1] - datetime.now())
        
        p = (datetime.strptime("02/09/2021") - datetime.now()).days / (dates["CCINP"][1] - datetime.strptime("02/09/2021"))
        m += f"\nGlobalement l'avancement de l'année est de {generate_progress_bar(p*100)} {p*100}%"

        await ctx.send(content=m)