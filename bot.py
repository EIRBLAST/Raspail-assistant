from class_file import *

from discord_slash import SlashCommand

TOKEN     = os.environ['TOKEN']

#bot client
client = RaspailAssistant()
#slash command client
slash = SlashCommand(client,sync_commands = True, sync_on_cog_reload = True,)

#main extensions
main_extension = [
    'cogs.group_management'
]


guild_ids = [879451596247933039] # Put your server ID in this array.

for file in main_extension:
    client.load_extension(file)
    print(f'loaded {file}')

@slash.slash(name="ping", guild_ids=guild_ids)
async def _ping(ctx): # Defines a new "context" (ctx) command called "ping."
    await ctx.send(f"Pong! ({client.latency*1000}ms)")

#called when the bot starts
@client.event
async def on_ready():
    #load the bot cogs
    print('Loaded extensions')



if __name__ == '__main__':
    
    client.run(TOKEN)