from class_file import *

from discord_slash import SlashCommand


REDIS_URL = os.environ['REDIS_URL']
TOKEN     = os.environ['TOKEN']

client = RaspailAssistant()
slash = SlashCommand(client)

#called when the bot starts
@client.event
async def on_ready():
    
    
    client.load_extension("cog")
    print('Loaded extensions')

if __name__ == '__main__':
    client.run()