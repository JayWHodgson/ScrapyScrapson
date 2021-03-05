# ScrapyHTMLMake.py
# A bot by Jaye :)
# 27/02/2021 - Last Update: 28/02/2021
import discord
import os
import re
import shlex
import requests
import shutil
import sys
from discord.ext import commands

#setup discord
intents = discord.Intents.default()
intents.members = True
TOKEN = ''
with open('Token.txt', 'r') as f:
    TOKEN = f.readline()
ISTXCID = 816008780911214618
client = discord.Client(intents=intents)

def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok

async def image_get(url):
    image_server = client.get_channel(816008780911214618)
    filename = url.split("/")[-1] #make a file name
    
    r = None
    i = 0
    while i < 3 and r == None:
        try:#this will in most cases work, but discord can be weird sometimes
            r = requests.get(url, stream=True) #attempt to retrieve image
        except:
            r = None
            i += 1 #don't so more than three times
    if r == None:
        return None
        
    if r.status_code == 200: #check if image was retrieved
        r.raw.decode_content = True #if not set image size will be zero
        with open(filename, 'wb') as f: #write raw data to a file in binary
            shutil.copyfileobj(r.raw, f)
        if os.stat(filename).st_size >= 8388608: #check if file is over 8MB
            os.remove(filename) 
            return None #attachments larger than 8MB will unfortunately be lost on channel deletion
        
        message = None
        while message == None: #attempt upload 
            try: #we already checked size, there's no reason the file can't be sent
                message = await image_server.send(file=discord.File(filename)) #send attachment to image server
            except:
                message = None
        
        os.remove(filename) #remove file once uploaded
        return message.attachments[0].url #there will only ever be one attachment
    else:
        return None

async def make_filename(src_name, export_mode):
    ext = ''
    if export_mode == 0:
        ext = 'txt'
    else:
        ext = 'html'
        
    filename = f'{src_name}_Log.{ext}'
    #on the chance of multiple servers using bot that happen to have the same channel name
    iNum = 0
    while os.path.exists(filename):
        filename = f'{src_name}_Log{iNum}.{ext}'
        iNum+=1
    
    return filename

async def log_make(scrape_target, post_target, export_mode):
    filename = await make_filename(scrape_target.name, export_mode)
    
    history = await scrape_target.history(limit=sys.maxsize, oldest_first=True).flatten()
    with open(filename,'w+', encoding='utf8') as f:
        if export_mode == 0:
            await make_txt(history, f)
        else:
            await make_html(history, f, scrape_target)
    
    #post to channel of choice
    try:
        await post_target.send(file=discord.File(filename))
        os.remove(filename) #remove file once uploaded
    finally:
        return

async def HTMLPreamble(src_channel):
    guild_name = src_channel.guild.name
    category_name = src_channel.category.name
    channel_name = src_channel.name
    channel_topic = src_channel.topic
    icon_url = str(src_channel.guild.icon_url)
    preamble = f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <title>{guild_name} - {channel_name}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">

    <style>
        /* General */

@font-face {{
    font-family: Whitney;
    src: url(https://cdn.jsdelivr.net/gh/Tyrrrz/DiscordFonts@master/whitney-300.woff);
    font-weight: 300;
}}

@font-face {{
    font-family: Whitney;
    src: url(https://cdn.jsdelivr.net/gh/Tyrrrz/DiscordFonts@master/whitney-400.woff);
    font-weight: 400;
}}

@font-face {{
    font-family: Whitney;
    src: url(https://cdn.jsdelivr.net/gh/Tyrrrz/DiscordFonts@master/whitney-500.woff);
    font-weight: 500;
}}

@font-face {{
    font-family: Whitney;
    src: url(https://cdn.jsdelivr.net/gh/Tyrrrz/DiscordFonts@master/whitney-600.woff);
    font-weight: 600;
}}

@font-face {{
    font-family: Whitney;
    src: url(https://cdn.jsdelivr.net/gh/Tyrrrz/DiscordFonts@master/whitney-700.woff);
    font-weight: 700;
}}

body {{
    font-family: "Whitney", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 17px;
}}

a {{
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

img {{
    object-fit: contain;
}}

.markdown {{
    max-width: 100%;
    line-height: 1.3;
    overflow-wrap: break-word;
}}

.preserve-whitespace {{
    white-space: pre-wrap;
}}

.spoiler {{
    /* width: fit-content; */
    display: inline-block;
    /* This is more consistent across browsers, the old attribute worked well under Chrome but not FireFox. */
}}

.spoiler--hidden {{
    cursor: pointer;
}}

.spoiler-text {{
    border-radius: 3px;
}}

.spoiler--hidden .spoiler-text {{
    color: rgba(0, 0, 0, 0);
}}

.spoiler--hidden .spoiler-text::selection {{
    color: rgba(0, 0, 0, 0);
}}

.spoiler-image {{
    position: relative;
    overflow: hidden;
    border-radius: 3px;
}}

.spoiler--hidden .spoiler-image {{
    box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.1);
}}

.spoiler--hidden .spoiler-image * {{
    filter: blur(44px);
}}

.spoiler--hidden .spoiler-image:after {{
    content: "SPOILER";
    color: #dcddde;
    background-color: rgba(0, 0, 0, 0.6);
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    font-weight: 600;
    padding: 100%;
    border-radius: 20px;
    letter-spacing: 0.05em;
    font-size: 0.9em;
}}

.spoiler--hidden:hover .spoiler-image:after {{
    color: #fff;
    background-color: rgba(0, 0, 0, 0.9);
}}

.quote {{
    margin: 0.1em 0;
    padding-left: 0.6em;
    border-left: 4px solid;
    border-radius: 3px;
}}

.pre {{
    font-family: "Consolas", "Courier New", Courier, monospace;
}}

.pre--multiline {{
    margin-top: 0.25em;
    padding: 0.5em;
    border: 2px solid;
    border-radius: 5px;
}}

.pre--inline {{
    padding: 2px;
    border-radius: 3px;
    font-size: 0.85em;
}}

.mention {{
    border-radius: 3px;
    padding: 0 2px;
    color: #7289da;
    background: rgba(114, 137, 218, .1);
    font-weight: 500;
}}

.emoji {{
    width: 1.25em;
    height: 1.25em;
    margin: 0 0.06em;
    vertical-align: -0.4em;
}}

.emoji--small {{
    width: 1em;
    height: 1em;
}}

.emoji--large {{
    width: 2.8em;
    height: 2.8em;
}}

/* Preamble */

.preamble {{
    display: grid;
    margin: 0 0.3em 0.6em 0.3em;
    max-width: 100%;
    grid-template-columns: auto 1fr;
}}

.preamble__guild-icon-container {{
    grid-column: 1;
}}

.preamble__guild-icon {{
    max-width: 88px;
    max-height: 88px;
}}

.preamble__entries-container {{
    grid-column: 2;
    margin-left: 0.6em;
}}

.preamble__entry {{
    font-size: 1.4em;
}}

.preamble__entry--small {{
    font-size: 1em;
}}

/* Chatlog */

.chatlog {{
    max-width: 100%;
}}

.chatlog__message-group {{
    display: grid;
    margin: 0 0.6em;
    padding: 0.9em 0;
    border-top: 1px solid;
    grid-template-columns: auto 1fr;
}}

.chatlog__reference-symbol {{
    grid-column: 1;
    border-style: solid;
    border-width: 2px 0 0 2px;
    border-radius: 8px 0 0 0;
    margin-left: 16px;
    margin-top: 8px;
}}

.chatlog__reference {{
    display: flex;
    grid-column: 2;
    margin-left: 1.2em;
    margin-bottom: 0.25em;
    font-size: 0.875em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    align-items: center;
}}

.chatlog__reference-avatar {{
    border-radius: 50%;
    height: 16px;
    width: 16px;
    margin-right: 0.25em;
}}

.chatlog__reference-name {{
    margin-right: 0.25em;
    font-weight: 600;
}}

.chatlog__reference-link {{
    flex-grow: 1;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.chatlog__reference-link:hover {{
    text-decoration: none;
}}

.chatlog__reference-content > * {{
    display: inline;
}}

.chatlog__reference-edited-timestamp {{
    margin-left: 0.25em;
    font-size: 0.8em;
}}

.chatlog__author-avatar-container {{
    grid-column: 1;
    width: 40px;
    height: 40px;
}}

.chatlog__author-avatar {{
    border-radius: 50%;
    height: 40px;
    width: 40px;
}}

.chatlog__messages {{
    grid-column: 2;
    margin-left: 1.2em;
    min-width: 50%;
}}

.chatlog__author-name {{
    font-weight: 500;
}}

.chatlog__timestamp {{
    margin-left: 0.3em;
    font-size: 0.75em;
}}

.chatlog__message {{
    padding: 0.1em 0.3em;
    margin: 0 -0.3em;
    background-color: transparent;
    transition: background-color 1s ease;
}}

.chatlog__content {{
    font-size: 0.95em;
    word-wrap: break-word;
}}

.chatlog__edited-timestamp {{
    margin-left: 0.15em;
    font-size: 0.8em;
}}

.chatlog__attachment {{
    margin-top: 0.3em;
}}

.chatlog__attachment-thumbnail {{
    vertical-align: top;
    max-width: 45vw;
    max-height: 500px;
    border-radius: 3px;
}}

.chatlog__attachment-container {{
    height: 40px;
    width: 100%;
    max-width: 520px;
    padding: 10px;
    border: 1px solid;
    border-radius: 3px;
    overflow: hidden;
}}

.chatlog__attachment-icon {{
    float: left;
    height: 100%;
    margin-right: 10px;
}}

.chatlog__attachment-icon > .a {{
    fill: #f4f5fb;
    d: path("M50,935a25,25,0,0,1-25-25V50A25,25,0,0,1,50,25H519.6L695,201.32V910a25,25,0,0,1-25,25Z");
}}

.chatlog__attachment-icon > .b {{
    fill: #7789c4;
    d: path("M509.21,50,670,211.63V910H50V50H509.21M530,0H50A50,50,0,0,0,0,50V910a50,50,0,0,0,50,50H670a50,50,0,0,0,50-50h0V191Z");
}}

.chatlog__attachment-icon > .c {{
    fill: #f4f5fb;
    d: path("M530,215a25,25,0,0,1-25-25V50a25,25,0,0,1,16.23-23.41L693.41,198.77A25,25,0,0,1,670,215Z");
}}

.chatlog__attachment-icon > .d {{
    fill: #7789c4;
    d: path("M530,70.71,649.29,190H530V70.71M530,0a50,50,0,0,0-50,50V190a50,50,0,0,0,50,50H670a50,50,0,0,0,50-50Z");
}}

.chatlog__attachment-filesize {{
    color: #72767d;
    font-size: 12px;
}}

.chatlog__attachment-filename {{
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}}

.chatlog__embed {{
    display: flex;
    margin-top: 0.3em;
    max-width: 520px;
}}

.chatlog__embed-color-pill {{
    flex-shrink: 0;
    width: 0.25em;
    border-top-left-radius: 3px;
    border-bottom-left-radius: 3px;
}}

.chatlog__embed-content-container {{
    display: flex;
    flex-direction: column;
    padding: 0.5em 0.6em;
    border: 1px solid;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
}}

.chatlog__embed-content {{
    display: flex;
    width: 100%;
}}

.chatlog__embed-text {{
    flex: 1;
}}

.chatlog__embed-author {{
    display: flex;
    margin-bottom: 0.3em;
    align-items: center;
}}

.chatlog__embed-author-icon {{
    margin-right: 0.5em;
    width: 20px;
    height: 20px;
    border-radius: 50%;
}}

.chatlog__embed-author-name {{
    font-size: 0.875em;
    font-weight: 600;
}}

.chatlog__embed-title {{
    margin-bottom: 0.2em;
    font-size: 0.875em;
    font-weight: 600;
}}

.chatlog__embed-description {{
    font-weight: 500;
    font-size: 0.85em;
}}

.chatlog__embed-fields {{
    display: flex;
    flex-wrap: wrap;
}}

.chatlog__embed-field {{
    flex: 0;
    min-width: 100%;
    max-width: 506px;
    padding-top: 0.6em;
    font-size: 0.875em;
}}

.chatlog__embed-field--inline {{
    flex: 1;
    flex-basis: auto;
    min-width: 150px;
}}

.chatlog__embed-field-name {{
    margin-bottom: 0.2em;
    font-weight: 600;
}}

.chatlog__embed-field-value {{
    font-weight: 500;
}}

.chatlog__embed-thumbnail {{
    flex: 0;
    margin-left: 1.2em;
    max-width: 80px;
    max-height: 80px;
    border-radius: 3px;
}}

.chatlog__embed-image-container {{
    margin-top: 0.6em;
}}

.chatlog__embed-image {{
    max-width: 500px;
    max-height: 400px;
    border-radius: 3px;
}}

.chatlog__embed-footer {{
    margin-top: 0.6em;
}}

.chatlog__embed-footer-icon {{
    margin-right: 0.2em;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    vertical-align: middle;
}}

.chatlog__embed-footer-text {{
    font-size: 0.75em;
    font-weight: 500;
}}

.chatlog__reactions {{
    display: flex;
}}

.chatlog__reaction {{
    display: flex;
    align-items: center;
    margin: 0.35em 0.1em 0.1em 0.1em;
    padding: 0.2em 0.35em;
    border-radius: 3px;
}}

.chatlog__reaction-count {{
    min-width: 9px;
    margin-left: 0.35em;
    font-size: 0.875em;
}}

.chatlog__bot-tag {{
    position: relative;
    top: -.2em;
    margin-left: 0.3em;
    padding: 0.05em 0.3em;
    border-radius: 3px;
    vertical-align: middle;
    line-height: 1.3;
    background: #7289da;
    color: #ffffff;
    font-size: 0.625em;
    font-weight: 500;
}}

/* Postamble */

.postamble {{
    margin: 1.4em 0.3em 0.6em 0.3em;
    padding: 1em;
    border-top: 1px solid;
}}
    </style>
    <style>
        /* General */

body {{
    background-color: #36393e;
    color: #dcddde;
}}

a {{
    color: #0096cf;
}}

.spoiler-text {{
    background-color: rgba(255, 255, 255, 0.1);
}}

.spoiler--hidden .spoiler-text {{
    background-color: #202225;
}}

.spoiler--hidden:hover .spoiler-text {{
    background-color: rgba(32, 34, 37, 0.8);
}}

.quote {{
    border-color: #4f545c;
}}

.pre {{
    background-color: #2f3136 !important;
}}

.pre--multiline {{
    border-color: #282b30 !important;
    color: #b9bbbe !important;
}}

/* === Preamble === */

.preamble__entry {{
    color: #ffffff;
}}

/* Chatlog */

.chatlog__message-group {{
    border-color: rgba(255, 255, 255, 0.1);
}}

.chatlog__reference-symbol {{
    border-color: #4f545c;
}}

.chatlog__reference {{
    color: #b5b6b8;
}}

.chatlog__reference-link {{
    color: #b5b6b8;
}}

.chatlog__reference-link:hover {{
    color: #ffffff;
}}

.chatlog__reference-edited-timestamp {{
    color: rgba(255, 255, 255, 0.2);
}}

.chatlog__author-name {{
    color: #ffffff;
}}

.chatlog__timestamp {{
    color: rgba(255, 255, 255, 0.2);
}}

.chatlog__message--highlighted {{
    background-color: rgba(114, 137, 218, 0.2) !important;
}}

.chatlog__message--pinned {{
    background-color: rgba(249, 168, 37, 0.05);
}}

.chatlog__attachment-container {{
    background-color: #2f3136;
    border-color: #292b2f;
}}

.chatlog__edited-timestamp {{
    color: rgba(255, 255, 255, 0.2);
}}

.chatlog__embed-color-pill--default {{
    background-color: rgba(79, 84, 92, 1);
}}

.chatlog__embed-content-container {{
    background-color: rgba(46, 48, 54, 0.3);
    border-color: rgba(46, 48, 54, 0.6);
}}

.chatlog__embed-author-name {{
    color: #ffffff;
}}

.chatlog__embed-author-name-link {{
    color: #ffffff;
}}

.chatlog__embed-title {{
    color: #ffffff;
}}

.chatlog__embed-description {{
    color: rgba(255, 255, 255, 0.6);
}}

.chatlog__embed-field-name {{
    color: #ffffff;
}}

.chatlog__embed-field-value {{
    color: rgba(255, 255, 255, 0.6);
}}

.chatlog__embed-footer {{
    color: rgba(255, 255, 255, 0.6);
}}

.chatlog__reaction {{
    background-color: rgba(255, 255, 255, 0.05);
}}

.chatlog__reaction-count {{
    color: rgba(255, 255, 255, 0.3);
}}

/* Postamble */

.postamble {{
    border-color: rgba(255, 255, 255, 0.1);
}}

.postamble__entry {{
    color: #ffffff;
}}
    </style>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/solarized-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/highlight.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            document.querySelectorAll('.pre--multiline').forEach(block => hljs.highlightBlock(block));
        }});
    </script>

    <script>
        function scrollToMessage(event, id) {{
            var element = document.getElementById('message-' + id);

            if (element) {{
                event.preventDefault();

                element.classList.add('chatlog__message--highlighted');

                window.scrollTo({{
                    top: element.getBoundingClientRect().top - document.body.getBoundingClientRect().top - (window.innerHeight / 2),
                    behavior: 'smooth'
                }});

                window.setTimeout(function() {{
                    element.classList.remove('chatlog__message--highlighted');
                }}, 2000);
            }}
        }}

        function showSpoiler(event, element) {{
            if (element && element.classList.contains('spoiler--hidden')) {{
                event.preventDefault();
                element.classList.remove('spoiler--hidden');
            }}
        }}
    </script>
</head>
<body>

<div class="preamble">
    <div class="preamble__guild-icon-container">
        <img class="preamble__guild-icon" src="{icon_url}" alt="Guild icon">
    </div>
    <div class="preamble__entries-container">
        <div class="preamble__entry">{guild_name}</div>
        <div class="preamble__entry">{category_name} / {channel_name}</div>

            <div class="preamble__entry preamble__entry--small">{channel_topic}</div>

    </div>
</div>

"""
    return preamble

async def HTMLPostamble():
    postamble = f"""
</div>

<div class="postamble">
    <div class="postamble__entry"></div>
</div>

</body>

</html>
"""
    return postamble

async def HTMLchat_group_open(message):
    try:
        mem = message.guild.get_member(message.author.id)
        rgb = mem.colour.to_rgb()
    except:
        rgb = (255,255,255)
    
    openner = f"""
<div class="chatlog__message-group">
    <div class="chatlog__author-avatar-container">
        <img class="chatlog__author-avatar" src="{str(message.author.avatar_url)}" alt="Avatar">
    </div>
    <div class="chatlog__messages">
        <span class="chatlog__author-name" title="{message.author.name}#{message.author.discriminator}" data-user-id="{message.author.id}" style="color: rgb({rgb[0]},{rgb[1]},{rgb[2]})">{message.author.display_name}</span>
        <span class="chatlog__timestamp">{message.created_at.strftime("%d-%m-%Y %H:%M ")}</span>
    """
    return openner
    
async def HTMLchat_group_close(message):
    closer = f"""
    </div>
</div>
    """
    return closer
    
async def HTMLmessage_make(message):
    msgcontent = message.clean_content
    links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msgcontent)
    for i in links:
        msgcontent = msgcontent.replace(i, f'<a href="{i}">{i}</a>')
    emoji = re.findall('<:(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+:(?:[0-9])+>', msgcontent)
    
    for i in emoji:
        emjL = []
        try:
            emj = i.replace('<', '')
            emj = emj.replace('>', '')
            emjL = emj.split(':')
            emjL.pop(0)
            #print(emjL)
            emjO = await message.guild.fetch_emoji(emjL[1])
            if emjO == None:
                emjO = await client.get_emoji(emjL[1])
            msgcontent = msgcontent.replace(i, f'<img class="emoji emoji--large" alt=":{emjO.name}:" title=":{emjO.name}:" src="{str(emjO.url)}"></span>')
        except:
            try: #if emoji can't be found try to find it on the discord server
                if exists(f'https://cdn.discordapp.com/emojis/{emjL[1]}.gif'):
                    msgcontent = msgcontent.replace(i, f'<img class="emoji emoji--large" alt=":{emjL[0]}:" title=":{emjL[0]}:" src="https://cdn.discordapp.com/emojis/{emjL[1]}.gif"></span>')
                else:
                    msgcontent = msgcontent.replace(i, f'<img class="emoji emoji--large" alt=":{emjL[0]}:" title=":{emjL[0]}:" src="https://cdn.discordapp.com/emojis/{emjL[1]}.png"></span>')
            except:
                i = None
        
    
    msg = f"""
            <div class="chatlog__message " data-message-id="{message.id}" id="message-{message.id}">
                <div class="chatlog__content">
                    <div class="markdown">
                        <span class="preserve-whitespace">{msgcontent}</span>
                    </div>
                </div>
    """
    for q in message.attachments:
        atturl = await image_get(q.url)
        if atturl: #if image was successfully retrieved
            msg = msg + f"""
                <div class="chatlog__attachment">
                    <div class="" onclick="">
                        <div class="">
                            <a href="{atturl}">
                                <img class="chatlog__attachment-thumbnail" src="{atturl}" alt="Image attachment">
                            </a>
                        </div>
                    </div>
                </div>
            """
    for q in message.embeds:
        msg = msg + f"""
                <div class="chatlog__embed">
                    <div class="chatlog__embed-color-pill chatlog__embed-color-pill--default"></div>

                    <div class="chatlog__embed-content-container">
                        <div class="chatlog__embed-content">
                            <div class="chatlog__embed-text">
        """
        if q.title:
            msg = msg +f"""
                                <div class="chatlog__embed-title">
                                    <a class="chatlog__embed-title-link" href="{q.url}">
                                        <div class="markdown preserve-whitespace">{q.title}</div>
                                    </a>
                                </div>
            """
        msg = msg + f"""
                            </div>
                            <div class="chatlog__embed-thumbnail-container">
                                <a class="chatlog__embed-thumbnail-link" href="{q.url}">
                                    <img class="chatlog__embed-thumbnail" src="{q.thumbnail.url}" alt="Thumbnail">
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
        """
    msg = msg + f"""
            </div>
    """
    return msg

async def make_txt(history, f):
    last_auth = -1 #declare id to compare to
    for i in history:
        #don't include messages by the bot and the command to activate it
        if (i.author != client.user) and (re.search('!Scrape*', i.content) == None):
            #if the message has a different author than the last message write their name to file
            if((i.author.id != last_auth)):
                f.write(f'{i.author.display_name}: \n')
                last_auth = i.author.id
            #write message to file
            f.write(f'{i.created_at.strftime("%m/%d/%Y-%H:%M:%S: ")}{i.clean_content}')

            #write attachment urls to file if they exists
            for q in i.attachments:
                atturl = await image_get(q.url)
                if atturl: #if image was successfully retrieved
                    f.write(atturl)
                    #seperate urls
                    if q != i.attachments[len(i.attachments) - 1]:  
                        f.write(' / ')
            f.write('\n')

async def make_html(history, f, src_channel):
    f.write(await HTMLPreamble(src_channel))
    f.write('<div class="chatlog">')#open chatlogs
    last_message = history[0] #sets the first message's author
    f.write(await HTMLchat_group_open(last_message))
    for i in history:
        #don't include messages by the bot and the command to activate it
        if (i.author != client.user) and (re.search('!Scrape*', i.content) == None):
            if((i.author.id != last_message.author.id)):
                f.write(await HTMLchat_group_close(last_message))
                f.write(await HTMLchat_group_open(i))
            f.write(await HTMLmessage_make(i))
            last_message = i
    f.write(await HTMLchat_group_close(last_message))
    f.write(await HTMLPostamble())
    
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
                
            if(args[3] == 'txt'):
                oType = 0
            elif(args[3] == 'html'):
                oType = 1
            else:
                await message.channel.send(content='Last argument must be "txt" or "html"')
                return
            
            #get source and destination channels
            scrape_target = discord.utils.get(message.guild.channels, name=args[1])
            post_target = discord.utils.get(message.guild.channels, name=args[2])

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
            await log_make(scrape_target, post_target, oType)
        else:
            for c in scrape_target.channels:
                if type(c) is discord.channel.TextChannel: #skip voice channels
                    await log_make(c, post_target, oType)
        
        #attach log to message
        await message.channel.send(content='Scrape Finished')

client.run(TOKEN)