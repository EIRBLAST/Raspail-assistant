from class_file import *

from discord_slash import SlashCommand

TOKEN     = os.environ['TOKEN']

#bot client
client = RaspailAssistant()
#slash command client
slash = SlashCommand(client, sync_commands=True)

#main extensions
main_extension = [
    'cogs.group_management'    
]

#remove the help command
client.remove_command('help')

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