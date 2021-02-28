# ScrapyMain.py
# A bot by Jaye :)
# 27/02/2021 - Last Update: 28/02/2021

import discord
import os
import re
import shlex

#setup discord
TOKEN = ''
with open('Token.txt', 'r') as f:
    TOKEN = f.readline()
client = discord.Client()

#make a text log of scrape_target and post it in post_target
async def log_make(scrape_target, post_target):
    filename = f'{scrape_target.name}_Log.txt'
        #on the chance of multiple servers using bot that happen to have the same channel name
    iNum = 0
    while os.path.exists(filename):
        filename = f'{scrape_target.name}_Log{iNum}.txt'
        iNum+=1
    
    last_auth = -1 #declare id to compare to
    async for i in scrape_target.history(oldest_first=True):
        with open(filename,'a', encoding='utf8') as f:
            #don't include messages by the bot and the command to activate it
            if (i.author != client.user) and (re.search('!Scrape*', i.content) == None):
                #if the message has a different author than the last message write their name to file
                if(i.author.id != last_auth):
                    f.write(f'{i.author.display_name}: \n')
                    last_auth = i.author.id
                #write message to file
                f.write(f'{i.created_at.strftime("%m/%d/%Y-%H:%M:%S: ")}{i.content}')
                
                #write attachment urls to file if they exists
                for q in i.attachments:
                    f.write(q.url)
                    #seperate urls
                    if q != i.attachments[len(i.attachments) - 1]:  
                        f.write(' / ')
                f.write('\n')
    #post to channel of choice
    await post_target.send(file=discord.File(filename))
    os.remove(filename) #remove file once uploaded
    return

#find a channel in a server with a name string
async def channel_find(name, guild):
    found = False
    for j in guild.channels:
        if name == j.name:
            found = True
            mChnl = j
            return j
    return None

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    
@client.event
async def on_message(message):
    #don't react to own messages
    if message.author == client.user:
        return
    #command is either "!Scrape" or "!Scrape [Channel or Category] [Source] [Destination]"
    if re.search('!Scrape*', message.content):
        if len(message.content) >= 9: #if arguments are passed            
            args = shlex.split(message.content[8:])
            #check type of Scrape, 0 = Channel, 1 = Category
            if(args[0] == 'Channel'):
                cType = 0
            elif(args[0] == 'Category'):
                cType = 1
            else:
                await message.channel.send(content='First argument must be "Channel" or "Category"')
                return
            
            #get source and destination channels
            scrape_target = await channel_find(args[1], message.guild)
            post_target =  await channel_find(args[2], message.guild)
            
            #check to see if the channels exist
            if (scrape_target == None) or (post_target == None):
                await message.channel.send(content='Channel not found')
                return
            
            #make sure channels are of right type
            if (cType == 1) and (type(scrape_target) is not discord.channel.CategoryChannel):
                await message.channel.send(content='Source is not a Category')
                return
            elif(type(post_target) is not discord.channel.TextChannel):
                await message.channel.send(content='Destination is not a Text Channel')
                return

        else: #if just "!Scrape"
            post_target = message.channel
            scrape_target = message.channel
            cType = 0
    
        await message.channel.send('Beginning Scrape')
        
        if cType == 0:
            await log_make(scrape_target, post_target)
        else:
            for c in scrape_target.channels:
                if type(c) is discord.channel.TextChannel: #skip voice channels
                    await log_make(c, post_target)
        
        #attach log to message
        await message.channel.send(content='Scrape Finished')

client.run(TOKEN)