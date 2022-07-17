# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord
import os
from copy import copy, deepcopy
#from keep_alive import keep_alive


client = discord.Client()

# REF: https://stackoverflow.com/questions/66628327/discord-py-bot-reactions-in-dms
intents = discord.Intents.default()
intents.members = True

global g_msg_id
g_msg_id = 0

global ctx 
ctx = {}

# Restrict the Q&A max to 2 Levels  

# userid: {'rewards': (xp, gold, star),'selected_q': (channel_id, selected_emoji_ucode), 'expected_ans': None}
global user_track_table
user_track_table = {}

# use list to store rewards: [xp, gold, starts] to save the space
default_user_record = {'rewards': [0, 0, 0], 'selected_q': [0, ''], 'q_to_ask_id': 0, 'q_to_ask_ans': [], 'knowledge_q_id': 0, 'expected_ans': [], 'expect_msg_id': 0, 'msg_tye': ""}

# Questions for users in order
pycon_questions_list = [

{'q':"Where did you know about PyCon 2022 from", 'opts': {1:"Facebook", 2:"YouTube", 3:"Twitter", 4:"Others"}},
{'q':"How many years of your Python experience", 'opts': {1:"<1", 2:"1-5", 3:">5", 4:">10"}}

]

knowledge_QnA_list = [

{'q':"The highest mountain in Taiwan", 'opts': {1:"玉山", 2:"合歡山", 3:"阿里山"}, 'ans': 3}

]


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
                        1. 求事業，請點🙏\n
                        2. 求姻緣，請點😘\n
                        3. 求財富，請點💵\n
                        4. 求健康，請點💪
        """)
        ra_list = ['🙏', '😘', '💵', '💪']


    if message.content.startswith('$npc_add'):
        embed = discord.Embed(title="路人甲", color=0x6610f2)
        embed.add_field(name="用以下方式與路人互動",
                        value="""
                        1. 閒聊得金幣, 請點💰\n
                        2. 知識換金幣, 請點💵\n
                        3. 地圖尋寶，請點👣\n 
                        4. 我有疑問，請點❓
        """)        
        ra_list = ['💰', '💵', '👣', '❓']
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

    # init the question menu releated variables    
    location = "白金攤位"

    # init user related variables
    if payload.user_id not in user_track_table:
        user_track_table[payload.user_id] = deepcopy(default_user_record)
    
    pycon_q_to_ask = pycon_questions_list[user_track_table[payload.user_id]['q_to_ask_id']]  
    knowledge_q_to_ask = knowledge_QnA_list[user_track_table[payload.user_id]['knowledge_q_id']]

    ra_msg_dict = {
        "meo" : 
            {
            '🙏': {'msg_t': 'guide_var', 'msg_q': f"Please go to {location} for high pay jobs !"},
            '😘': {'msg_t': 'q_select', 'msg_q': 'Who is your favorite talker?', 'options': {1:"talker-a", 2:"talker-b"}},
            '💵': {'msg_t': 'guide_var', 'msg_q': 'Please go to XX for good luck !'},
            '💪': {'msg_t': 'guide_var', 'msg_q': 'Please go to XX and take a look at YY !'}
            },
        "npc" :
            {
            '💰': {'msg_t': 'q_select', 'msg_q': f"{pycon_q_to_ask['q']} ?", 'options': f"{pycon_q_to_ask['opts']}"} , 
            '💵': {'msg_t': 'q_select', 'msg_q': f"{knowledge_q_to_ask['q']} ?", 'options': f"{knowledge_q_to_ask['opts']}"}, 
            '👣': {'msg_t': 'guide_var', 'msg_q': 'Please visit xx in Gather Town, you may find something interesting !'}, 
            '❓': {'msg_t': 'guide_var', 'msg_q': 'http://tw.pycon.org'}
            }
    }

    num_ra_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
    # Level-1 Selections (Entry questions)
    for chan in ra_msg_dict:
        for k in ra_msg_dict[chan]:
            if str(payload.emoji) == k:
                embed = discord.Embed(title='', color=0x6610f2) 
                embed_field_name = ra_msg_dict[chan][k]['msg_q']
                embed_field_value = "See you soon.."
                if ra_msg_dict[chan][k]['msg_t'] == 'q_select' :
                    embed_field_value = ""
                    for opt in ra_msg_dict[chan][k]['options']:
                        embed_field_value += num_ra_list[int(opt) - 1]
                        embed_field_value += ra_msg_dict[chan][k]['options'][opt]
                        embed_field_value += "\n"
                
                embed.add_field(name = embed_field_name, value = embed_field_value)

                msg = await member.send(embed=embed)

                if ra_msg_dict[chan][k]['msg_t'] == 'q_select' :
                    for ra in num_ra_list[:len(ra_msg_dict[chan][k]['options'])]:
                        await msg.add_reaction(ra)
                    # Record the user state for selected questions
                    user_track_table[payload.user_id]['selected_q'][0] = chan
                    user_track_table[payload.user_id]['selected_q'][1] = k
                
                # keep the msg.id for follow reaction 
                user_track_table[payload.user_id]['expect_msg_id'] = msg.id

                if k == '💰':
                    user_track_table[payload.user_id]['msg_tye'] = 'pycon_q'
                if k == '💵':
                    user_track_table[payload.user_id]['msg_tye'] = 'knowledge_q'
                    user_track_table[payload.user_id]['expected_ans'][0] =  knowledge_q_to_ask['ans']   
                
                # update [xp, gold, stars]
                user_track_table[payload.user_id]['rewards'][0] += 1

                # We can escape the loop
                break

    # Level-2 Selections (Answers)
    if user_track_table[payload.user_id]['expect_msg_id'] == payload.message_id :
        if str(payload.emoji) == num_ra_list[user_track_table[payload.user_id]['expected_ans'][0] - 1]:
            user_track_table[payload.user_id]['rewards'][1] += 1
            # clear the msg.id answered
            user_track_table[payload.user_id]['expect_msg_id'] = 0
    
    # user_track_table[payload.user_id] = {}
    print({user_track_table})

    # Write user_track_table['rewards'] and ['q_to_ask_ans'] to database 

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
