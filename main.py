# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord
import os
from copy import copy, deepcopy
#from keyifylist import KeyifyList
import pqdict
# from pqdict import PQDict

#from pqdict import heapsorted_by_value


# billionaires = {'Bill Gates': 72.7, 'Warren Buffett': 60.0, ...}
# top10_richest = heapsorted_by_value(billionaires, maxheap=True)[:10]

# prio_queue = queue.PriorityQueue()
#from keep_alive import keep_alive


client = discord.Client()

# REF: https://stackoverflow.com/questions/66628327/discord-py-bot-reactions-in-dms
intents = discord.Intents.default()
intents.members = True

global g_msg_id
g_msg_id = 0

global ctx 
ctx = {}

global npc_msg 
npc_msg = None

# Restrict the Q&A max to 2 Levels  

# userid: {'rewards': (xp, gold, star),'selected_q': (channel_id, selected_emoji_ucode), 'expected_ans': None}
global user_track_table
user_track_table = {}

# use list to store rewards: [xp, gold, starts] to save the space
default_user_record = {'rewards': [0, 0, 0], 'selected_q': [0, ''], 'q_to_ask_id': 0, 'q_to_ask_ans': [], 'knowledge_q_id': 0, 'expected_ans': [0], 'expect_msg_id': 0, 'msg_tye': ""}

# Questions for users in order
pycon_questions_list = [

{'q':"Where did you know about PyCon 2022 from", 'opts': {1:"Facebook", 2:"YouTube", 3:"Twitter", 4:"Others"}},
{'q':"How many years of your Python experience", 'opts': {1:"<1", 2:"1-3", 3:">3", 4:">5"}}

]

knowledge_QnA_list = [

{'q':"The highest mountain in Taiwan", 'opts': {1:"玉山", 2:"合歡山", 3:"阿里山", 4:"陽明山"}, 'ans': 3},
{'q':"桃園大溪最有名的小吃是", 'opts': {1:"豆乾", 2:"豆花", 3:"豆漿", 3:"花生糖"}, 'ans': 1}

]

rank_list = []

rank_pq = pqdict.pqdict(reverse = True)

rank_dict = {}

def rank_update (user_id, gold):
    #import bisect
    #l_indx = bisect.bisect_left(KeyifyList(rank_list, lambda x: x[1]), gold)
    #rank_list.insert(l_indx, (user_id, gold))
    if user_id in rank_pq:
        rank_pq.updateitem(user_id, gold)
    else:
        rank_pq.additem(user_id, gold)     

    #rank_dict[user_id] = gold
    return



async def get_ctx_from_payload(pl):

    if pl.guild_id is None:
        return

    guild = await client.fetch_guild(pl.guild_id)

    # Check guild.
    if guild is None:
        print("on_raw_reaction_add() :: Could not find guild with ID #" + str(pl.guild_id))
        return

    chnl = client.get_channel(pl.channel_id)

    # Check channel.
    if chnl is None:
        print("on_raw_reaction_add() :: Could not find channel with ID #" + str(pl.channel_id))
        return
        
    msg = await chnl.fetch_message(pl.message_id)

    # Check message.
    if msg is None:
        print("on_raw_reaction_add() :: Could not find message with ID #" + str(pl.message_id))
        return 
    
    user = await guild.fetch_member(pl.user_id)

    # Check user.
    if user is None:
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
    # Load user data and init user track table


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    embed = None
    ra_list = []
    if message.content.startswith('$rank'):
        embed = discord.Embed(title="目前排名", color=0x6610f2)
        embed_field_name = "Rank by Gold"
        embed_field_value = "Rank:\n"
        # for user_id, gold in reversed(rank_list):
        _rank_pq_copy = rank_pq.copy()
        for user_id in _rank_pq_copy:
        # rank_sorted = pqdict.nlargest(len(rank_dict), rank_dict)
        #for user_id in rank_sorted:
            user = await client.fetch_user(user_id)
            embed_field_value += user.name + ":" + str(_rank_pq_copy[user_id]) + "\n"

        embed.add_field(name = embed_field_name, value = embed_field_value)

        # ra_list = []          


    if message.content.startswith('$meo_add'):
        embed = discord.Embed(title="有求必應", color=0x6610f2)
        embed.add_field(name="用以下方式求指示",
                        value=
                        "1. 求事業，請點🙏\n" +
                        "2. 求姻緣，請點😘\n" +
                        "3. 求財富，請點㊗️\n" +
                        "4. 求健康，請點💪"
        )
        ra_list = ['🙏', '😘', '㊗️', '💪']


    if message.content.startswith('$npc_add'):
        embed = discord.Embed(title="我是路人甲", color=0x6610f2)
        embed.add_field(name="用以下方式與我互動",
                        value=
                        "1. 閒聊得金幣, 請點💰\n" +
                        "2. 知識換金幣, 請點💵\n" +
                        "3. 地圖尋寶，請點👣\n" + 
                        "4. 有其它疑問，請點❓"
        )        
        ra_list = ['💰', '💵', '👣', '❓']
    
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

    #print(client.user)
    print(payload.user_id)
    
    #user = await client.fetch_user(payload.user_id)
    #print(user)

    # From Direct Messages: payload guild is None that member is None from bot
    if payload.member is None:
        if payload.user_id not in user_track_table:
            return

    #await get_ctx_from_payload(payload)
    #if ctx != {}:
    #   print(ctx['chnl'])
  
    #if payload.message_id == g_msg_id:
    if payload.member:
        member = payload.member
        if member.bot:
            return

    #print(payload.member)

    # init the question menu releated variables    
    location = "白金攤位"

    # init user related variables
    if payload.user_id not in user_track_table:
        user_track_table[payload.user_id] = deepcopy(default_user_record)
    
    user_record = user_track_table[payload.user_id]

    if user_record['q_to_ask_id'] < len(pycon_questions_list):
        pycon_q_to_ask = pycon_questions_list[user_record['q_to_ask_id']] 
    else:
        pycon_q_to_ask = {'q':"You had completed all Q&A, thank you !", 'opts': {}} 

    if user_record['knowledge_q_id'] < len(knowledge_QnA_list):
        knowledge_q_to_ask = knowledge_QnA_list[user_record['knowledge_q_id']]
    else:
        knowledge_q_to_ask = {'q':"You had completed all Q&A, thank you !", 'opts': {}, 'ans': 0}

    ra_msg_dict = {
        'meo' : 
            {
            '🙏': {'msg_t': 'guide_var', 'msg_q': f"Please go to {location} for high pay jobs !"},
            '😘': {'msg_t': 'q_select', 'msg_q': 'Who is your favorite talker?', 'options': {1:"talker-a", 2:"talker-b"}},
            '㊗️': {'msg_t': 'guide_var', 'msg_q': 'Please go to XX for good luck !'},
            '💪': {'msg_t': 'guide_var', 'msg_q': 'Please go to XX and take a look at YY !'}
            },
        'npc' :
            {
            '💰': {'msg_t': 'q_select', 'msg_q': f"{pycon_q_to_ask['q']} ?", 'options': pycon_q_to_ask['opts']} , 
            '💵': {'msg_t': 'q_select', 'msg_q': f"{knowledge_q_to_ask['q']} ?", 'options': knowledge_q_to_ask['opts']}, 
            '👣': {'msg_t': 'guide_var', 'msg_q': 'Please visit xx in Gather Town, you may find something interesting !'}, 
            '❓': {'msg_t': 'guide_var', 'msg_q': 'http://tw.pycon.org'}
            }
    }

    num_ra_list = {'1️⃣':1, '2️⃣':2, '3️⃣':3, '4️⃣':4}
    # Level-1 Selections (Entry questions)
    for chan in ra_msg_dict:
        for k in ra_msg_dict[chan]:
            if str(payload.emoji) == k:
                embed = discord.Embed(title='', color=0x6610f2) 
                embed_field_name = ra_msg_dict[chan][k]['msg_q']
                embed_field_value = "See you soon.."
                if ra_msg_dict[chan][k]['msg_t'] == 'q_select' :
                    if len(ra_msg_dict[chan][k]['options']) > 0:
                        embed_field_value = ""
                    for opt in ra_msg_dict[chan][k]['options']:
                        embed_field_value += [*num_ra_list][int(opt) - 1]
                        embed_field_value += ra_msg_dict[chan][k]['options'][opt]
                        embed_field_value += "\n"
                
                embed.add_field(name = embed_field_name, value = embed_field_value)

                msg = await member.send(embed=embed)

                if ra_msg_dict[chan][k]['msg_t'] == 'q_select' :
                    for ra in [*num_ra_list][:len(ra_msg_dict[chan][k]['options'])]:
                        await msg.add_reaction(ra)
                    # Record the user state for selected questions
                    user_record['selected_q'][0] = chan
                    user_record['selected_q'][1] = k
                
                # keep the msg.id for follow reaction 
                user_record['expect_msg_id'] = msg.id

                if k == '💰':
                    user_record['msg_tye'] = 'pycon_q'
                    user_record['expected_ans'][0] = 0
                if k == '💵':
                    user_record['msg_tye'] = 'knowledge_q'
                    user_record['expected_ans'][0] =  knowledge_q_to_ask['ans']   
                
                # update [xp, gold, stars]
                user_record['rewards'][0] += 1

                # clear the reaction from 'npc' channel that user can do it multiple times
                if payload.member and chan == 'npc':
                    global npc_msg
                    if npc_msg is None: 
                        await get_ctx_from_payload(payload)
                        npc_msg = ctx['msg']
                    
                    await npc_msg.remove_reaction(k, payload.member)

                # We can escape the loop
                break

    # Level-2 Selections (Answers)
    if user_record['expect_msg_id'] == payload.message_id :
        embed_field_name = "Rewards"
        if user_record['msg_tye'] == 'pycon_q':
            if str(payload.emoji) in num_ra_list:
                user_record['rewards'][1] += 1
                user_record['q_to_ask_ans'].append(num_ra_list[str(payload.emoji)])
                user_record['q_to_ask_id'] += 1
                # clear the msg.id answered
                user_record['expect_msg_id'] = 0
                embed_field_name = "Your got a gold!"           
        
        if user_record['expected_ans'][0] > 0:
            if str(payload.emoji) in num_ra_list:
                if num_ra_list[str(payload.emoji)] == user_record['expected_ans'][0]:
                    user_record['rewards'][1] += 1
                    user_record['knowledge_q_id'] += 1               
                    user_record['expected_ans'][0] = 0   
                    # clear the msg.id answered
                    user_record['expect_msg_id'] = 0
                    embed_field_name = "Your got a gold!"

        embed = discord.Embed(title='', color=0x6610f2) 
        embed_field_value = "You have: "
        embed_field_value += f"Gold: {str(user_record['rewards'][1])} "
        embed_field_value += f"Stars: {str(user_record['rewards'][2])}"
        embed.add_field(name = embed_field_name, value = embed_field_value)

        user = await client.fetch_user(payload.user_id)
        await user.send(embed=embed)               

    rank_update(payload.user_id, user_record['rewards'][1])
    # user_track_table[payload.user_id] = {}
    print(user_track_table)

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
