from datetime import date, datetime, timedelta

import humanize
import discord
from discord.ext import commands
from discord_slash import ComponentContext, SlashCommand, SlashContext, cog_ext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import (create_actionrow,
                                                   create_button,
                                                   create_select,
                                                   create_select_option,
                                                   wait_for_component)

from tools import data_io


dates = {
        "CESI" : [datetime.strptime("06/04/2022", "%d/%m/%Y"), datetime.strptime("06/04/2022", "%d/%m/%Y")],
        "EPITA / IPSA / ESME" : [datetime.strptime("09/04/2022", "%d/%m/%Y"), datetime.strptime("09/04/2022", "%d/%m/%Y")],
        "Centrale-Supélec": [datetime.strptime("03/05/2022", "%d/%m/%Y"), datetime.strptime("06/05/2022", "%d/%m/%Y")],
        "CCINP": [datetime.strptime("09/05/2022", "%d/%m/%Y"), datetime.strptime("13/05/2022", "%d/%m/%Y")]
}


humanize.i18n.activate('fr')


def generate_progress_bar(perecent):
    full = "⬛"
    blanck = "⬜"

    full_count = round(perecent)// 10
    print(full_count)
    blanck_count = 10 - full_count

    return full * full_count + blanck * blanck_count

class MotivationCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="motivation",description='Te motive (parceque on en a tous besoin)', guild_ids= [879451596247933039])
    async def send_motivation(self,ctx:SlashContext):
        m = "Voici le contdown jusqu'aux différents concours"
        for concours in dates.keys():
            if datetime.now() < dates[concours][1]:
                m += "\n\t- " + concours + ": "  +  humanize.precisedelta(dates[concours][1] - datetime.now(), minimum_unit="minutes")
        
        p = (datetime.strptime("02/09/2021", "%d/%m/%Y") - datetime.now()).total_seconds() / (datetime.strptime("02/09/2021", "%d/%m/%Y") - dates["CCINP"][1]).total_seconds()
        m += f"\nGlobalement l'avancement de l'année est de {generate_progress_bar(p*100)} {p*100:.2f}%"

        await ctx.send(content=m)

def setup(bot):
    bot.add_cog(MotivationCommands(bot))