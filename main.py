# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord
import os
#from keep_alive import keep_alive


client = discord.Client()

global g_msg_id
g_msg_id = 0

global ctx 
ctx = {}

async def get_ctx_from_payload(pl):

    guild = await client.fetch_guild(pl.guild_id)

    # Check guild.
    if guild == None:
        print("on_raw_reaction_add() :: Could not find guild with ID #" + str(pl.guild_id))
        return

    chnl = client.get_channel(pl.channel_id)

    # Check channel.
    if chnl == None:
        print("on_raw_reaction_add() :: Could not find channel with ID #" + str(pl.channel_id))
        return
        
    msg = await chnl.fetch_message(pl.message_id)

    # Check message.
    if msg == None:
        print("on_raw_reaction_add() :: Could not find message with ID #" + str(pl.message_id))

        user = await guild.fetch_member(pl.user_id)

        # Check user.
        if user == None:
            print("on_raw_reaction_add() :: Could not find user with ID #" + str(pl.user_id))
            return
        ctx['user'] = user 
  
    ctx['guild'] = guild
    ctx['chnl'] = chnl
    ctx['msg'] = msg

    return

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$meo_add'):
        embed = discord.Embed(title="各種求", color=0x6610f2)
        embed.add_field(name="用以下方式求神明指示",
                        value="""
                        1. 求事業，請點:pray:\n
                        2. 求姻緣，請點:kissing_heart:\n
                        3. 求財富，請點:dollar:\n
                        4. 求健康，請點:muscle:
        """)
        ra_list = ['\U0001F64F', '\U0001F60D', '\U0001F4B5', '\U0001F4AA']


    if message.content.startswith('$npc_add'):
        embed = discord.Embed(title="路人甲", color=0x6610f2)
        embed.add_field(name="用以下方式與路人互動",
                        value="""
                        1. 閒聊得金幣, 請點:moneybag:\n
                        2. 知識換金幣, 請點:dollar:\n
                        3. 地圖尋寶，請點:footprints:\n 
                        4. 我有疑問，請點:question:
        """)        
        ra_list = ['\U0001F4B0', '\U0001F4B5', '\U0001F463', '\U00002753']
        #ra_list = ['pray', 'kissing_heart', 'dollar', 'muscle']
    
    if embed is not None:
        try:
            msg = await message.channel.send(embed=embed)
            g_msg_id = msg.id
            print({g_msg_id})
            
            #hide the command messages from user
            await message.delete()  
            
            for ra in ra_list:
                await msg.add_reaction(ra)
        except discord.HTTPException as e:
            print({e})


@client.event
async def on_raw_reaction_add(payload):
    print(f'{payload.message_id} == {g_msg_id}')   

    # await get_ctx_from_payload(payload)
    # if ctx != {}:
    #   print(ctx)
  
    #if payload.message_id == g_msg_id:
    if payload.member:
      member = payload.member
      if member.bot:
        return
      
      location = "白金攤位"  
      ra_msg_dict = {
        "meo" : 
            {
            '\U0001F64F': {'msg_t': 'guide_var', 'msg_q': f"Please go to {location} for high pay jobs !"},
            '\U0001F60D': {'msg_t': 'q_select', 'msg_q': 'Who is your favorite talker?', 'options': {1:"talker-a", 2:"talker-b"}},
            '\U0001F4B5': {'msg_t': 'guide_var', 'msg_q': 'Please go to XX for good luck !'},
            '\U0001F4AA': {'msg_t': 'guide_var', 'msg_q': 'Please go to XX and take a look at YY !'}
            },
        "npc" :
            {
            '\U0001F4B0': {'msg_t': 'q_select', 'msg_q': 'Where did you get the info about PyCon 2022 from ?', 'options': {1:"Facebook", 2:"YouTube", 3:"Others"}} , 
            '\U0001F4B5': {'msg_t': 'q_select', 'msg_q': 'The highest mountain in Taiwan ?'}, 
            '\U0001F463': {'msg_t': 'guide_var', 'msg_q': 'Please visit xx in Gather Town, you may find something interesting !'}, 
            '\U00002753': {'msg_t': 'guide_var', 'msg_q': 'http://tw.pycon.org'}
            }
      }

    # Level-1 Questions
    for chan in ra_msg_dict:
        for k in ra_msg_dict[chan]:
            if str(payload.emoji) == k: 
                await member.send(ra_msg_dict[chan][k]['msg_q'])
                
                
    

#keep_alive()

try:
    client.run(os.getenv("TOKEN"))
except discord.HTTPException as e:
    if e.status == 429:
        print(
            "The Discord servers denied the connection for making too many requests"
        )
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e
