from class_file import *

from discord_slash import SlashCommand

TOKEN     = os.environ['TOKEN']

client = RaspailAssistant()
slash = SlashCommand(client)

main_extension = [
    'cogs.group_management'    
]


#called when the bot starts
@client.event
async def on_ready():
    #load the bot cogs
    for file in main_extension:
            client.load_extension(file)
            print(f'loaded {file}')
    print('Loaded extensions')

if __name__ == '__main__':
    client.run()