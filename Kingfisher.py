from __future__ import print_function

import asyncio
import datetime
import json
import logging
import math
import operator
import os
import platform
import random
import re
import time
import traceback

import aiohttp
import discord
import gspread
import pytz
from discord.ext import commands
from discord.ext.commands import Bot
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image, ImageDraw
from pytz import timezone

version="0.08 Vials"
###useful resources
#for colours
#www.htmlcsscolor.com/hex


#keys for the map updating function
factions = { "horrorshow":(188, 0, 0), "faceless":(155, 89, 182), "forerunners":(231, 76, 60), "authority":(109, 130, 187),"leeches":(137, 90, 0),"eclipse":(0, 126, 133), "neutral":(255,255,255), "independent":(136, 0, 21), "sharks":(82, 95, 157), "hearth":(255, 215, 0) }
areas = [(57,98 ),(157,106 ),(229,105),(322,103),(416,103),(526,63),(604,46),(695,48),(781,81),(886,67),(971,68),(1044,62),(66,211),(163,206),(247,203),(322,198),(396,198),(492,154),(636,132),(681,145),(781,129),(885,129),(955,163),(1015,163),(1065,140),(69,293),(153,293),(261,293),(355,293),(433,293),(544,243),(807,222),(895,215),(998,238),(1060,222),(1139,179),(165,368),(258,383),(347,401),(403,364),(500,341),(557,325),(604,293),(668,285),(759,322),(817,269),(933,293),(1018,313),(155,450),(268,477),(478,445),(538,413),(589,401),(658,346),(695,323),(814,334),(861,322 ),(971,373 ),(1061,371 ),(444,495 ),(557,502 ),(637,477 ),(669,417 ),(724,383 ),(736,483 ),(757,453 ),(818,439 ),(882,415 ),(500,622 ),(595,592 ),(674,570 ),(718,540 ),(795,484 ),(843,464 ),(431,706 ),(510,682 ),(567,648 ),(444,780)]
#gh stuff
gh_factions={"deplorables":(241, 196, 15),"avalon":(173, 20, 87),"children":(155, 89, 182),"court":(101, 111, 255),"dominion":(192, 49, 53),   "uplift":(26, 151, 73), "neutral":(255,255,255), "independent":(163, 145, 108)}
#old factions: "division":(76, 140, 255), "prestige":(179, 86, 243), "daybreak":(236,42,18), "elite":(241, 196, 15),
gh_areas=[(100,122),(132.67,120),(192,118.6666667),(234.6666667,140.6666667),(268.6666667,165.3333333),(313.3333333,129.3333333),(372.6666667,126),(429.3333333,60),(473.3333333,20),(458.6666667,81.33333333),(498.6666667,53.33333333),(477.3333333,130),(482,162.6666667),(492,217.3333333),(415.3333333,207.3333333),(369.3333333,192),(293.3333333,194.6666667),(226.6666667,203.3333333),(166.6666667,184),(150.6666667,229.3333333),(113.3333333,224.6666667),(114,283.3333333),(181.3333333,234),(215.3333333,228.6666667),(262.6666667,238),(223.3333333,286),(379.3333333,230.6666667),(440.6666667,272.6666667),(464.6666667,241.3333333),(498,291.3333333),(490,320),(410,308),(351.3333333,278),(357.3333333,318),(250.6666667,322),(214.6666667,338),(134.6666667,309.3333333),(170.6666667,344.6666667),(166.6666667,378),(166,428),(239.3333333,392),(244.6666667,428),(278,376.6666667),(318,387.3333333),(316.6666667,433.3333333),(393.3333333,352.6666667),(359.3333333,412.6666667),(422.6666667,387.3333333),(458.6666667,378),(490.6666667,394.6666667),(494,458.6666667),(430.6666667,420.6666667),(439.3333333,459.3333333),(350.6666667,475.3333333),(271.3333333,494),(229.3333333,499.3333333),(190,484.6666667),(148,460),(174.6666667,509.3333333),(190.6666667,545.3333333),(278,546.6666667),(331.3333333,524),(380,553.3333333),(422.6666667,525.3333333),(455.3333333,512.6666667),(498,525.3333333)]
typ_colours={"Bash":0x0137f6,"Pierce":0xffa500,"Cut":0xb22649,"Freeze":0x00ecff,"Shock":0xd6ff00,"Rend":0x9937a5,"Burn":0x0fe754, "Poison":0x334403}
muted_usr=[]

asyncio.set_event_loop(asyncio.new_event_loop())
owner = ["138340069311381505"] #hyper#4131

logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger('discord')
#logger.setLevel(logging.DEBUG)
#handler = logging.FileHandler(filename=f'discord.log', encoding='utf-8', mode='a')
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#logger.addHandler(handler)

#pylint suppressions
# pylint: disable=E0102, W1401


# Setup the Sheets API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/spreadsheets.readonly']
credentials = ServiceAccountCredentials.from_json_keyfile_name('gspread.json', scope)
gc = gspread.authorize(credentials)

#kingfisher reference doc
RefSheet = gc.open_by_key('1LOZkywwxIWR41e8h-xIMFGNGMe7Ro2cOYBez_xWm6iU')
sheet = RefSheet.worksheet("Wounds")
feed = sheet.get_all_values()
tagsSheet = RefSheet.worksheet("Tags")
tags = tagsSheet.get_all_values()
perksSheet = RefSheet.worksheet("Perks")
perksfeed = perksSheet.get_all_values()
augSheet = RefSheet.worksheet("Augments")
augfeed = augSheet.get_all_values()
triggerSheet = RefSheet.worksheet("Triggers")
triggerfeed = triggerSheet.get_all_values()

#vials
VialDoc = gc.open_by_key("1yksmYY7q1GKx4tXVpb7oSxffgEh--hOvXkDwLVgCdlg")
sheet = VialDoc.worksheet("Full Vials")
vialfeed = sheet.get_all_values()


# Here you can modify the bot's prefix and description and whether it sends help in direct messages or not.
client = Bot(description=f"Thinkerbot version {version}", command_prefix=">", pm_help = False, case_insensitive=True)

# This is what happens everytime the bot launches. In this case, it prints information like server count, user count the bot is connected to, and the bot id in the console.
# Do not mess with it because the bot can break, if you wish to do so, please consult me or someone trusted.
@client.event
async def on_ready():
    print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print('running...')
    await client.change_presence(game=discord.Game(name='>help'))
    global b_task
    global b_task2
    b_task=client.loop.create_task(account_decay())
    b_task2=client.loop.create_task(rank_decay())
    return 


###Functions
#to add new factions
#add new faction colour
#add faction to legend via gimp
async def mapUpdate(faction,square,sid):

    #detroitmap = Image.open('borders_white.png')
    detroitmap = Image.open(f"map_{sid}/factionmap.png")
    legend = Image.open(f"map_{sid}/Legend_alpha.png")
    bg = Image.open(f"map_{sid}/background.png")
    if sid=="d":
        ImageDraw.floodfill(detroitmap, areas[square-1], (255,255,255))
        ImageDraw.floodfill(detroitmap, areas[square-1], factions[faction])
    elif (sid=="gh") or (sid=="test"):
        ImageDraw.floodfill(detroitmap, gh_areas[square-1], (255,255,255))
        ImageDraw.floodfill(detroitmap, gh_areas[square-1], gh_factions[faction])
    detroitmap.save(f"map_{sid}/factionmap.png")
    detroitmap =Image.alpha_composite(detroitmap,legend)
    detroitmap = Image.composite(detroitmap, bg, detroitmap)
    detroitmap.save(f"map_{sid}/map.png") #output
    
async def int_to_roman(input):
   if type(input) != type(1):
      raise TypeError(f"expected integer, got {type(input)}")
   if not 0 < input < 4000:
      raise ValueError("Argument must be between 1 and 3999")   
   ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
   nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
   result = ""
   for i in range(len(ints)):
      count = int(input / ints[i])
      result += nums[i] * count
      input -= ints[i] * count
   return result

#figure out which server this command runs on. Remind me to actually write server configs one day. One day. xd.
async def sid(loc):
    if loc=="283841245975937034":
        sid="detroit"
    elif loc=="465651565089259521":
        sid="gh"
    elif loc=="406587085278150656":
        sid="segovia"
    elif loc=="434729592352276480":
        sid="test"
    else:
        sid="undefined"
    return sid

#Deals with special wounds that require more interaction. Most common used to roll the effects chains for critical wounds.
specWounds=("Demolished","Cremated","Disintegrated (shock)","Iced Over","Whited Out","Devastated","Annihilated","Spreading","Infused")
async def specialWounds(client,ctx,case):
    ctx.invoked_with="wound"
    if case=="Demolished":
        bashes=[]
        limb=random.choice(["Arm","Legs","Head"])
        for i in feed:
            if i[0]=="Bash":
                if i[1]=="Moderate":
                    if i[2]==limb:
                        bashes.append(i)
            embed = discord.Embed(colour=discord.Colour(typ_colours["Bash"]))
            embed.set_footer(text=f"Rolled for {ctx.message.author.name} | {case}",icon_url=ctx.message.author.avatar_url)
            for i in bashes:
                embed.add_field(name=i[3], value=f"{i[4]}\n*Location: {i[2]}, Stage: {i[1]}*")
        await client.send_message(ctx.message.channel,embed=embed)
    elif (case=="Cremated") or (case=="Whited Out") or (case=="Disintegrated (shock)"):
        if case=="Cremated":
            typ="Burn"
        elif case=="Disintegrated (shock)":
            typ="Shock"
        elif case=="Whited Out":
            typ="Freeze"
        await ctx.invoke(wound,typus=typ,tag=case,title="__**Effect**__")
        while random.randint(0,1) < 1:
            await asyncio.sleep(0.2)
            await ctx.invoke(wound,typus=typ,tag=case)
        await client.send_message(ctx.message.channel,"Tails.")
    elif (case=="Iced Over"):
        await asyncio.sleep(0.2)
        await ctx.invoke(wound,typus="Freeze",tag=case,title="__**Effect**__")
    elif (case=="Spreading"):
        await asyncio.sleep(0.2)
        await ctx.invoke(wound,typus="Poison",severity="Lesser",tag=case,title="__**Effect**__")
    elif (case=="Infused"):
        await asyncio.sleep(0.2)
        await ctx.invoke(wound,typus="Poison",severity="Lesser",tag=case,title="__**Effect**__")
    elif (case=="Devastated"):
        typ=random.choice(["Cut","Bash","Pierce"])
        await asyncio.sleep(0.1)
        await ctx.invoke(wound,severity="Lesser",typus=typ,tag=case)
    elif (case=="Annihilated"):
        await ctx.invoke(roll,"3D7+0")

#Translates wound severity from our shorthands back to the longer explicit version.
async def severity_short(arg):
    if (arg=="lesser") or (arg=="les") or (arg=="l"):
        return "lesser"
    elif (arg=="moderate") or (arg=="mod") or (arg=="m"):
        return "moderate"
    elif (arg=="critical") or (arg=="crit") or (arg=="c"):
        return "critical"
    else:
        print("Comprehension Error in severity_short")

#check if a user is the bot itself
def is_me(m):
    return m.author == client.user


#global check to make sure blocked people can't mess around
@client.check
def mute_user(ctx):
    return ctx.message.author.id not in muted_usr

#local check used in some functions only
#Makes sure some functions cannot be used in pms
def no_pm(ctx):
    return not ctx.message.server is None

@client.event
async def on_member_join(member):
    if (member.server.id == "283841245975937034"): #or (member.server.id == "434729592352276480"):
        #await client.send_message(member,"**Welcome to V&V!**\nDon't hesitate to say hi in chat! Check out our New Player Guide at https://vanwiki.org/oc/new_player_guide")
        await client.send_message(discord.User(id=owner[0]),f"New player joined {member.server.name}: {member.name}")
    elif (member.server.id == "465651565089259521"):    
        await client.send_message(discord.User(id=owner[0]),f"New player joined {member.server.name}: {member.name}")
        
#@client.event
#async def on_command_error(error,ctx):
#    print(error)
#    logger.warning(f"{error} {traceback.format_exc()}") #logs the error traceback.format_exc()
#    #await client.send_message(ctx.message.channel,content="You fucked up.") #send the message to the channel
    
@client.command(pass_context=True, description="Makes the bot leave the server.",hidden=True)
async def order66(ctx):
    if ctx.message.author.id not in owner:
        await client.say("😰")
        return
    await client.say("Extermination in progress...")
    await asyncio.sleep(60*3)
    await client.say("Macht’s gut, und danke für den Fisch.")
    await client.leave_server(ctx.message.server)

@client.command(pass_context=True, description="Deletes all channels.",hidden=True)
async def order67(ctx):
    if ctx.message.author.id not in owner:
        await client.say("😰")
        return
    await client.say("Oh. You're actually serious about this?")
    #TODO: add confirmation
    chans=ctx.message.server.channels
    for i in chans:
        await client.delete_channel(i)

@client.command(pass_context=True, description="Need help? Want to ask for new features? Visit the Nest, the central server for all your Kingfisher needs.",hidden=True)
async def nest(ctx):
    await client.say("https://discord.gg/gxQVAbA")

#TODO: Conserve over restarts
#TODO: ping all people who reacted the the reminder     
@client.command(pass_context=True, description="Reminds you of shit. Time should be specified as 13s37m42h12d leaving away time steps as desired.", aliases=["rem"])
async def remind(ctx,time,*message):
    timer=0
    chunk=re.compile("\d+[shmd]*")
    chunks=chunk.findall(time)
    #print(chunks)
    for i in chunks:    
        if "s" in i:
            time=int(i[:-1])
            timer=timer+time
        if "m" in i:
            time=int(i[:-1])*60
            timer=timer+time
        if "h" in i:
            time=int(i[:-1])*60*60
            timer=timer+time
        if "d" in i:
            time=int(i[:-1])*60*60*24
            timer=timer+time
    await client.add_reaction(ctx.message,'\N{Timer Clock}')
    await asyncio.sleep(timer)
    await client.say(f"{ctx.message.author.mention}: {' '.join(message)}")

@client.command(pass_context=True, description="Shuts the bot down. Owner only.",hidden=True)
async def die(ctx):
    if ctx.message.author.id not in owner:
        await client.say("No. Fuck off.") 
        return
    global b_task
    global b_task2
    b_task.cancel()
    b_task2.cancel()
    await client.close()

#TODO: fix    
@client.command(pass_context=True, description="Used to send messages via Kingfisher to all servers.",hidden=True)
async def announce(ctx,*message:str):
    if ctx.message.author.id not in owner:
        return
    servs=client.servers
    print(servs)
    targets=[]
    for i in servs:
        print(i.name)
        for j in i.channels:
            if j.name=="general" or j.name=="chat":
                print(j.name)
                targets.append(j)
    print(targets)
    for i in targets:
        #await client.send_message(i,content=" ".join(message))
        return
            
    
@client.command(pass_context=True, description="Used to send messages via Kingfisher to a specific channel.",hidden=True)
async def tell(ctx,channel,*message:str):
    if ctx.message.author.id not in owner:
        return  
    target=client.get_channel(channel)
    await client.send_message(target,content=" ".join(message))
 
@client.command(pass_context=True,name='eval')
async def _eval(ctx, *, code):
    if ctx.message.author.id not in owner:
        return  
    """A bad example of an eval command"""
    await client.say(eval(code))
    

@client.command(pass_context=True, description="Refreshes the data from the reference docs. Owner only.",hidden=True)
async def updateFeed(ctx):
    if ctx.message.author.id not in owner:
        await client.say("You weren't even a challenge.")
        return
    global feed
    global tags
    global vialfeed
    global perksfeed
    global augfeed
    global triggerfeed
    credentials = ServiceAccountCredentials.from_json_keyfile_name('gspread.json', scope)
    gc = gspread.authorize(credentials)
    RefSheet = gc.open_by_key('1LOZkywwxIWR41e8h-xIMFGNGMe7Ro2cOYBez_xWm6iU')
    sheet = RefSheet.worksheet("Wounds")
    feed = sheet.get_all_values()
    tagsSheet = RefSheet.worksheet("Tags")
    tags = tagsSheet.get_all_values()
    VialDoc = gc.open_by_key("1yksmYY7q1GKx4tXVpb7oSxffgEh--hOvXkDwLVgCdlg")
    sheet = VialDoc.worksheet("Full Vials")
    vialfeed = sheet.get_all_values()
    perksSheet = RefSheet.worksheet("Perks")
    perksfeed = perksSheet.get_all_values()
    augSheet = RefSheet.worksheet("Augments")
    augfeed = augSheet.get_all_values()
    triggerSheet = RefSheet.worksheet("Triggers")
    triggerfeed = triggerSheet.get_all_values()
    await client.add_reaction(ctx.message,"\U00002714")

#fetch vials from the google sheet earlier for performance reasons. Then just format the stuff we're given. Easy. Has to account for some missing data.
@client.command(pass_context=True, description="Fetches vials from our vial sheet. Use *>vial* to roll a random vial, or *>vial Name* to look up a specific one.")
async def vial(ctx, avial=None):
    global vialfeed
    n=0
    vials=[[None]]*int((len(vialfeed)/4))
    output=None
    for i in range(1,len(vialfeed)):
        if vialfeed[i][0]!='':
            vials[n]=vialfeed[i]
            vials[n].extend(vialfeed[i+1])
            vials[n].extend(vialfeed[i+2])
            n=n+1

    if avial!=None:
        for i in range(0,len(vials)):
            if vials[i][0][:-1].casefold()==avial.casefold():
                output=vials[i]
    else:
        out=random.randint(0,len(vials)-1)
        output=vials[out]
    
    if output==None:
        await client.say(f"Vial {avial} not found.")
        return
    
    vialcolour=discord.Colour(0x00ffc4)
    embed = discord.Embed(title=f"__{output[0][:-1]}__", colour=vialcolour,url="https://docs.google.com/spreadsheets/d/1yksmYY7q1GKx4tXVpb7oSxffgEh--hOvXkDwLVgCdlg")
    embed.add_field(name="O [Desirability]",value=output[1][3:],inline=False)
    embed.add_field(name="P [Power]",value=output[5][3:],inline=False)
    if len(output[9][3:])>0:
        embed.add_field(name="R [Reliability]",value=output[9][3:],inline=False)
    embed.add_field(name=f"Case #1", value=output[3],inline=False)
    embed.add_field(name=f"Case #2", value=output[7],inline=False)
    if len(output[11])>0:
        embed.add_field(name=f"Case #3", value=output[11],inline=False)
    await client.say(embed=embed)

@client.command(pass_context=True, description="Perks and flaws. Use *>perk* to roll perks, *>flaw* to roll flaws. *>perk life* and *>flaw life* for life perks. Can also look up perks and flaws (*>perk profundum*). Can also use WD's *>luck*.",aliases=["flaw","luck","Flaw","Perk","Luck"])
async def perk(ctx, category=None):
    global perksfeed
    typus=0
    #2 perk life
    #3 perk power
    #4 flaw life
    #5 flaw power
    typus_name=[None,None,"Perk Life","Perk Power","Flaw Life","Flaw Power"]
    typus_colour=[None,None,discord.Colour(0xB6D7A8),discord.Colour(0x93C47D),discord.Colour(0xEA9999),discord.Colour(0xE06666)]
    if ctx.invoked_with.casefold()=="perk".casefold():
        #perk is column 2 and 3
        typus=typus+3
    elif ctx.invoked_with.casefold()=="flaw".casefold():
        #flaw is column 4 and 5
        typus=typus+5
    elif ctx.invoked_with.casefold()=="luck".casefold():
        category="luck"
    if (category==None) or (category=="power"):
        category="power" #we default to power perks
    elif category=="luck":
        luck=[None, None]
        luck[0]=random.randint(0,3)
        luck[1]=random.randint(0,3)
        typus=luck[0]+2
        if luck[1]==0:
            ctx.invoked_with="perk"
            await ctx.invoke(perk,category="power")
        elif luck[1]==1:
            ctx.invoked_with="perk"
            await ctx.invoke(perk,category="life")
        elif luck[1]==2:
            ctx.invoked_with="flaw"
            await ctx.invoke(perk,category="power")
        elif luck[1]==3:
            ctx.invoked_with="flaw"
            await ctx.invoke(perk,category="life")
    elif category=="life":
        typus=typus-1
    else:
        perkname=category
        for typus in range(2,6):
            for i in range(1,len(perksfeed)-2):
                p_pattern=re.compile("(\w*\,?\s?\-?\/?\'?)+\.")
                p_match=p_pattern.search(perksfeed[i][typus])
                if p_match: #required because there are some empty fields, and those don't return a p_match object at all, sadly
                    if (p_match.group()[:-1].casefold()==perkname.casefold()) or (p_match.group()[:-1].casefold().replace(" ","")==perkname.casefold()):
                        embed = discord.Embed(title=p_match.group()[:-1],description=perksfeed[i][typus][p_match.end():],colour=typus_colour[typus])
                        embed.set_footer(text=f"{typus_name[typus]}")
                        try:
                            await client.say(embed=embed)
                        except discord.HTTPException:
                            await client.say(perksfeed[i][typus])
        return
    out=random.randint(1,len(perksfeed)-3)
    while perksfeed[out][typus]=="":
        out=random.randint(1,len(perksfeed)-3)
    
    p_pattern=re.compile("(\w*\,?\s?\-?\/?\'?)+\.")
    p_match=p_pattern.search(perksfeed[out][typus])
    
    #dealing with banned perks
    bannedperks=["alumnor", "excessus", "champion", "carnificina", "swellingpower", "evolution","Powersuffers,rawpowerisdecreased","counter","hardceiling","deadshard","finemmane"]
    while p_match.group()[:-1].casefold().replace(" ","") in bannedperks:
        print("banned perk rolled")
        out=random.randint(1,len(perksfeed)-3)
        while perksfeed[out][typus]=="":
            out=random.randint(1,len(perksfeed)-3)
        p_pattern=re.compile("(\w*\,?\s?\-?\/?\'?)+\.")
        p_match=p_pattern.search(perksfeed[out][typus])
    #print(perksfeed[out][typus])
    embed = discord.Embed(title=p_match.group()[:-1],description=perksfeed[out][typus][p_match.end():],colour=typus_colour[typus])
    embed.set_footer(text=f"{typus_name[typus]}")
    try: #sadly there are some perks that are too long for the embed field.
        await client.say(embed=embed)
    except discord.HTTPException:
        await client.say(perksfeed[out][typus])
    

@client.command(pass_context=True, description="Roll augments. *>aug tinker*, or look up augs with *>aug tinker world*. You can see the short interpretation of the tarot card with *>aug world*",aliases=["aug","Aug"])
async def augment(ctx, classification=None, card=None):
    global augfeed
    if classification==None:
        await client.say("Need to know the classification. Blaster, Breaker, etc.")
        return
    augcolour=discord.Colour(0xBF9000)
    classifications=["blaster","breaker","brute","changer","master","mover","shaker","stranger","striker","tinker","thinker","trump"]
    cards=["fool","magi","nun","lady","lord","pope","lovers","chariot","strength","hermit","wheel","justice","hanged","death","temperance","devil","tower","star","moon","sun","judgement","world"]
    if classification in cards:
        await client.say(augfeed[cards.index(classification)+1][1])
        return
    augindex=classifications.index(classification.casefold())+2
    if card==None:
        out=random.randint(1,len(augfeed)-1)
        if augfeed[out][augindex]!="":
            embed = discord.Embed(title=f"{classification.title()} Augment",description=augfeed[out][augindex],colour=augcolour)
            await client.say(embed=embed)
            #await client.say(augfeed[out][augindex])
        else:
            embed = discord.Embed(title=f"{classification.title()} Augment - General",description=f"**{augfeed[out][0].title()}**: {augfeed[out][1]}",colour=augcolour)
            await client.say(embed=embed)
            #await client.say(f"**{augfeed[out][0].title()}**: {augfeed[out][1]}")
    else:
        augs=[i[augindex] for i in augfeed]
        p_pattern=re.compile("\w*\.")
        for i in range(0,len(augs)):
            p_match=p_pattern.search(augs[i])
            if p_match:
                if p_match.group()[:-1].casefold()==card.casefold(): 
                    await client.say(embed=discord.Embed(title=f"{classification.title()} Augment",description=augs[i],colour=augcolour))
                    return
                    #await client.say(augs[i])
        await client.say(f"No {card.title()} augment defined.")

@client.command(pass_context=True, description="Trigger warning.",aliases=["Trigger"])
async def trigger(ctx, id=None):
    global triggerfeed
    if id==None:
        out=random.randint(0,len(triggerfeed))
        while triggerfeed[out][0]=="":
            out=random.randint(0,len(triggerfeed))
        await client.say(f"Trigger #{out+1}: {triggerfeed[out][0]}")
    else:
        id=int(id)
        await client.say(f"Trigger #{id} by {triggerfeed[id-1][1]}: {triggerfeed[id-1][0]}")


@client.command(pass_context=True, description="Posts the google sheet document we use for our battle maps.", name="map", aliases=["maps"])
async def _map(ctx):
    playmap="https://docs.google.com/spreadsheets/d/1sqorjpTOAHHON_jPipwyGDHYPEEfGR2hPTbpETSUfys/edit"
    playmap_gh="https://docs.google.com/spreadsheets/d/1lPJuANN3ZX2PPSHWHGlPVUkQqexP7YUtkBvLm1YlBPo/edit#gid=0"
    if ctx.message.server.id=="465651565089259521":
        await client.say(playmap_gh)
    else:
        await client.say(playmap)

@client.command(pass_context=True, description="Use this command to claim squares on the map. Faction name needs to be spelled right. Use >claim to see the current map. Use >claim factions to see available factions")
async def claim(ctx,faction = None,square:int = None):
    loc=ctx.message.server.id #283841245975937034 detroit, 465651565089259521 GH
    if loc=="283841245975937034":
        sid="d"
    elif loc=="465651565089259521":
        sid="gh"
    else:
        sid="test"
    if (ctx.message.channel.id != "358409511838547979") and (ctx.message.channel.id != "435874236297379861") and (ctx.message.channel.id != "478240151987027978"):
        #await client.send_message(discord.User(id=owner[0]),f"Claiming in {ctx.message.channel}: {ctx.message.author.name}")
        await client.send_message(f"Can only claim in #faction-actions!")
        return
    cacher=random.randint(1, 100000000000)
    if faction=="factions":
        if sid=="d":
            await client.say(", ".join(list(factions.keys())))
            return
        elif sid=="gh":
            await client.say(", ".join(list(gh_factions.keys())))
            return
    if faction == None and square == None:
        await client.say(f"https://vanwiki.org/kingfisher/map_{sid}/map.png?nocaching={cacher}")
        return
    if faction != None and square == None:
        await client.say("Correct format: >claim Faction Square")
    try:
        await mapUpdate(faction.casefold(),square,sid)
    except (KeyError,IndexError):
        await client.add_reaction(ctx.message,"❌")
        return
    await client.say(f"Map updated. https://vanwiki.org/kingfisher/map_{sid}/map.png?nocaching={cacher}")
    #await client.send_file(ctx.message.channel,'Detroit_map.png')

@client.command(description="Bullying.",hidden=True)
async def worm(*args):
    await client.say("Take that, you 🐛")
	
@client.command(pass_context=True,description="Repeats famous catchphrases.", aliases=["Lysa"])
async def lysa(ctx):
    sweat_emoji = discord.utils.get(client.get_all_emojis(), name='sweats')
    phraselist = ["oof", "Uh", "Wew", "Weary", "sweats", "Rip", "nice", "Unfortunate", sweat_emoji, "listen\nit's fine"]
	
    await client.say(random.choice(phraselist))


# unsure if right 
# '>eve' command variables inits 
eve_max1 = 6
eve_max2 = 5
eve_f1 = []
eve_f2 = []
Eve_v = "v0.5 Eve"
# Rolls 6d5 and 6d6 in two columns	
@client.command(pass_context=True, description="Everyone's personal rolls",hidden=True)
async def eve(ctx, args = 0):
    global eve_f1
    global eve_f2
    var = ""
    if args == 1:
        eve_f1 = []
        for _ in range(6):
            eve_f1.append(random.randint(1, eve_max1))
        eve_f1.sort()
        var ="1"
    elif args == 2:
        eve_f2 = []
        for _ in range(6):
            eve_f2.append(random.randint(1, eve_max2))
        eve_f2.sort()
        var ="2"	
    elif args == 0:
        eve_f1 = []
        eve_f2 = []
        for _ in range(6):
            eve_f1.append(random.randint(1, eve_max1))
        eve_f1.sort()
        for _ in range(6):
            eve_f2.append(random.randint(1, eve_max2))
        eve_f2.sort()
        var ="r"
    elif args == 3:
        var ="s"
    
    await client.say( f"**{var}**\n|{eve_f1[0]} {eve_f1[1]} |  {eve_f2[0]} {eve_f2[1]}|\n|{eve_f1[2]} {eve_f1[3]} |  {eve_f2[2]} {eve_f2[3]}|\n|{eve_f1[4]} {eve_f1[5]} |  {eve_f2[4]} {eve_f2[5]}|")

@client.command(description="Forgot a simple URL? I got you.")
async def wiki(*args):
    await client.say("https://vanwiki.org/start")

@client.command(pass_context=True,description="Link a cape's vanwiki article.")
async def cape(ctx,*cape):
    cape=str(cape).replace(" ", "_")
    cape="".join(cape)
    cape=re.sub('\'|\,|\(|\)', '',cape)
    loc=ctx.message.server.id
    server=await sid(loc)
    if loc=="undefined":
        await client.add_reaction(ctx.message,"❌")
    domain=f"https://vanwiki.org/{server}/cape/{cape}"
    async with aiohttp.get(domain, allow_redirects=False) as r:
        #print(r.text)
        status="Status"
        if status in await r.text():
            await client.say(domain)
        else:
            await client.say("No such article. Create it at "+domain)


@client.command(pass_context=True,description="Fetch a user's avatar. Follow your Jadmin dreams.\nFormatting is tricky, check that you're matching case. Copy the discriminator too.")
async def avatar(ctx, user):
    if user==None:
        await client.say(">avatar [name]")
    user=ctx.message.server.get_member_named(user)
    if user==None:
        await client.add_reaction(ctx.message,"❌")
    await client.say(user.avatar_url)

@client.command(pass_context=True,description="No more %vial 5.",hidden=True)
async def stopspam(ctx, i:int):
    if ctx.message.author.id not in owner:
        await client.say("Need something deleted? <@&310528314412630027>.")
        return
    try:
        await client.purge_from(ctx.message.channel,limit=i,check=is_me)
    except discord.Forbidden:
        await client.say("Insufficient priviliges.")

#TODO: fix id
@client.command(pass_context=True,description="Fuck you.",hidden=True)
async def mute(ctx,usr): 
    if ctx.message.author.id not in owner:
        await client.say("This would be a fun game. But you already lost.")
        return
    global muted_usr
    muted_usr.append(ctx.message.server.get_member_named(usr).id)
    await client.say("I told them. Warned them.")
    print(f"{usr} has been muted.")

@client.command(pass_context=True,description="un-Fuck you.",hidden=True)
async def unmute(ctx,usr):
    if ctx.message.author.id not in owner:
        await client.say("No Release.")
        return
    global muted_usr
    muted_usr.remove(ctx.message.server.get_member_named(usr).id)
    await client.say("Finally free.")
    print(f"{usr} has been unmuted.")

@client.command(pass_context=True,description="Wer ist der Bürgermeister von Wesel?",hidden=True)
async def echo(ctx,*echo):
    if ctx.message.author.id not in owner:
        await client.say("Esel, Esel!")
        return
    print(" ".join(echo))
    print(ctx.message.channel)
    print(ctx.message.channel.id)
    await client.say(" ".join(echo))

@client.command(pass_context=True, name="time",description="Stuck in bubble hell? Wonder when giao will be back?")
async def _time(ctx,):
    utc=datetime.datetime.now(tz=pytz.utc)
    hyper = pytz.timezone('Europe/Berlin')
    zan= pytz.timezone('Europe/London')
    giao= pytz.timezone('Asia/Manila')
    kiwis = pytz.timezone('Pacific/Auckland')
    aussies = pytz.timezone('Australia/Canberra')
    pacific=pytz.timezone("America/Los_Angeles")
    mountain=pytz.timezone('America/Denver')
    central=pytz.timezone('America/Chicago')
    eastern=pytz.timezone('America/New_York')
    jakarta=pytz.timezone("Asia/Jakarta")

    hyper_dt=utc.astimezone(hyper)
    zan_dt=utc.astimezone(zan)
    giao_dt=utc.astimezone(giao)
    kiwis_dt=utc.astimezone(kiwis)
    pacific_dt=utc.astimezone(pacific)
    mountain_dt=utc.astimezone(mountain)
    central_dt=utc.astimezone(central)
    eastern_dt=utc.astimezone(eastern)
    aussies_dt=utc.astimezone(aussies)
    jakarta_dt=utc.astimezone(jakarta)

    fmt = '%H:%M:%S'
    utcfmt = '%H:%M:%S %a %d %b'
    fmt_offset = "(%Z %z)"

    embed = discord.Embed(title="Kingfisher World Clock", colour=discord.Colour(0xffffff))
    #embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Clock_simple.svg/1024px-Clock_simple.svg.png")
    embed.set_footer(text=f"Sponsored by Insomniacs Anonymous",icon_url=ctx.message.author.avatar_url)
    embed.add_field(name=f"UTC", value=utc.strftime(utcfmt),inline=False)
    embed.add_field(name=f"Auckland {kiwis_dt.strftime(fmt_offset)}", value=kiwis_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Manila {giao_dt.strftime(fmt_offset)}", value=giao_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Jakarta {jakarta_dt.strftime(fmt_offset)}", value=jakarta_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Berlin {hyper_dt.strftime(fmt_offset)}", value=hyper_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"London {zan_dt.strftime(fmt_offset)}", value=zan_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"New York {eastern_dt.strftime(fmt_offset)}", value=eastern_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Chicago {central_dt.strftime(fmt_offset)}", value=central_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Denver {mountain_dt.strftime(fmt_offset)}", value=mountain_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Seattle {pacific_dt.strftime(fmt_offset)}", value=pacific_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Canberra {aussies_dt.strftime(fmt_offset)}", value=aussies_dt.strftime(fmt), inline=True)
    
    await client.say(embed=embed)

#TODO: Better QoL, list options, better configuration
@client.command(pass_context=True, description="Gives (or removes) self-serve roles.")
async def toggle(ctx, req_role="Active"):
    bye_emoji = discord.utils.get(client.get_all_emojis(), name='byedog')
    user = ctx.message.author
    if req_role.casefold()=="Active".casefold():
        role = discord.utils.get(user.server.roles, name="Active")
        if role==None:
            await client.say("No Active role defined.")
        if role in user.roles:
            await client.remove_roles(user, role)
            await client.add_reaction(ctx.message,bye_emoji)
        else:
            await client.add_roles(user, role)
            await client.say("Remember, spamming 1v1s is punishable by death.")
    elif req_role.casefold()=="Smithy".casefold():
        role = discord.utils.get(user.server.roles, name="Smithy ⚔️")
        if role==None:
            await client.say("No Smithy role defined.")
        if role in user.roles:
            await client.remove_roles(user, role)
            await client.add_reaction(ctx.message,bye_emoji)
        else:
            await client.add_roles(user, role)
            await client.say("Welcome to the Smithy.")
            
    elif req_role.casefold()=="RED".casefold():
        role = discord.utils.get(user.server.roles, name="RED")
        opprole= discord.utils.get(user.server.roles, name="BLUE")
        if role==None:
            await client.say("No RED role defined.")
        if opprole in user.roles:
            await client.say("Oy! No peeking, you cheeky fuck!")
            return
        if role in user.roles:
            await client.remove_roles(user, role)
            await client.add_reaction(ctx.message,bye_emoji)
        else:
            await client.add_roles(user, role)
            await client.add_reaction(ctx.message,"\U00002666")
            await client.say("Go Team Red Star!")
            
    elif req_role.casefold()=="BLUE".casefold():
        role = discord.utils.get(user.server.roles, name="BLUE")
        opprole= discord.utils.get(user.server.roles, name="RED")
        if role==None:
            await client.say("No BLUE role defined.")
        if opprole in user.roles:
            await client.say("Oy! No peeking, you cheeky fuck!")
            return
        if role in user.roles:
            await client.remove_roles(user, role)
            await client.add_reaction(ctx.message,bye_emoji)
        else:
            await client.add_roles(user, role)
            await client.add_reaction(ctx.message,"\U0001f6e1")
            await client.say("Go Team Blue Shield!")
            
    elif req_role.casefold()=="oet".casefold():
        role = discord.utils.get(user.server.roles, name="OET")
        if role==None:
            await client.say("No OET role defined.")
        if role in user.roles:
            await client.remove_roles(user, role)
            await client.add_reaction(ctx.message,bye_emoji)
        else:
            await client.add_roles(user, role)
            await client.say("Welcome to Operation Elizabeth Tower.")
    elif req_role.casefold()=="interlude".casefold():
        role = discord.utils.get(user.server.roles, name="Interlude")
        if role==None:
            await client.say("No Interlude role defined.")
        if role in user.roles:
            await client.remove_roles(user, role)
            await client.add_reaction(ctx.message,bye_emoji)
        else:
            await client.add_roles(user, role)
            await client.say("You can now post in #interludes. Role will be automatically revoked after an hour.")
            await asyncio.sleep(60*60*1)
            await client.remove_roles(user, role)
            
           
    
#Rolls wounds off of the Weaverdice wound table.
@client.command(pass_context=True,aliases=["Bash","Pierce","Cut","Freeze","Shock","Rend","Burn","bash","pierce","cut","freeze","shock","rend","burn","Wound","Poison","poison"],
                description="You like hurting people, huh? Use this to roll your wound effect. >Damage_Type Severity [Aim] [Number]"
                 " Use >wound 'Hit Vitals' to find specfic wounds.")
async def wound(ctx, severity="Moderate", aim="Any", repeats=1,**typus):
    if aim.isdigit():
        repeats=int(aim)
        aim="Any"
    if severity.isdigit():
        repeats=int(severity)
        severity="Moderate"
    if repeats>8:
        if ctx.message.author.id not in owner:
            await client.say("/metalgearchittychittybangbang")
            return
    if ctx.invoked_with.casefold() == "Bash".casefold():
        typ="Bash"
    elif ctx.invoked_with.casefold() == "Pierce".casefold():
        typ="Pierce"
    elif ctx.invoked_with.casefold() == "Cut".casefold():
        typ="Cut"
    elif ctx.invoked_with.casefold() == "Freeze".casefold():
        typ="Freeze"
    elif ctx.invoked_with.casefold() == "Shock".casefold():
        typ="Shock"
    elif ctx.invoked_with.casefold() == "Rend".casefold():
        typ="Rend"
    elif ctx.invoked_with.casefold() == "Burn".casefold():
        typ="Burn"
    elif ctx.invoked_with.casefold() == "Poison".casefold():
        typ="Poison"
    if "typus" in typus: #kwarg
        typ=typus['typus']
    elif (ctx.invoked_with.casefold() == "Wound".casefold()) or (ctx.invoked_with.casefold() == "tag".casefold()):
        for i in feed:
            if i[3].casefold()==severity.casefold(): #severity is actually the wound we're looking for here
                await client.say(f"**{i[3]}**: {i[4]} *({i[0]}, {i[1]}, {i[2]})*")
                return True
        return
    elif "typ" not in locals():
        await client.add_reaction(ctx.message,"❌")
        return
    #shorthand code
    repeatlist=[]
    severitylist=[]
    shorthand=re.compile("\d[cml]")
    sm=shorthand.findall(severity)
    #what if nothing is found?
    if len(sm)!=0:
        for i in range(0,len(sm)):
            repeatlist.append(int(sm[i][0]))
            severitylist.append(sm[i][1])
    else:
        repeatlist.append(repeats)
        severitylist.append(severity)
        sm=["def"]
    for j in range(0,len(sm)):
        severity= await severity_short(severitylist[j].casefold())
        exclusive=False
        limbaim=False
        if "x" in aim:
            exclusive=True
            aimt=aim[1:]
        else:
            aimt=aim
        if aimt.upper() not in ["ANY","HEAD","TORSO","ARM","LEGS"]:
            if aimt.casefold() not in ["h","t","a","l"]:
                if aimt.casefold() == "limbs":
                    limbaim=True
                else:
                    await client.add_reaction(ctx.message,"❌")
                    return
            elif aimt.casefold()=="h":
                aimt="Head"
            elif aimt.casefold()=="t":
                aimt="Torso"
            elif aimt.casefold()=="a":
                aimt="Arm"
            elif aimt.casefold()=="l":
                aimt="Legs"
        typlist=[]
        for i in feed:
            if i[0].casefold()==typ.casefold():
                if i[1].casefold()==severity.casefold():
                    if exclusive==True:
                        if (i[2].casefold()==aimt.casefold()):
                            typlist.append(i)
                    elif limbaim==True:
                        if i[2].casefold() in ["arm","legs"]:
                            typlist.append(i)
                    elif (i[2].casefold()==aimt.casefold()) or (aimt=="Any") or (i[2]=="Any"):
                        typlist.append(i)
        embed=[]
        if "title" in typus:
             embed = discord.Embed(title=typus["title"],colour=discord.Colour(typ_colours[typ]))
        else:
            embed = discord.Embed(colour=discord.Colour(typ_colours[typ]))
        if "tag" in typus:
            embed.set_footer(text=f"Rolled for {ctx.message.author.name} | {typus['tag']}",icon_url=ctx.message.author.avatar_url)
        else:
            embed.set_footer(text=f"Rolled for {ctx.message.author.name} | {severity} {aim.casefold()} {repeatlist[j]}",icon_url=ctx.message.author.avatar_url)
        damages=[]
        for _ in range(0,repeatlist[j]):
             luck=random.randint(0,len(typlist)-1)
             damages.append(typlist[luck])
             embed.add_field(name=typlist[luck][3], value=f"{typlist[luck][4]}\n*Location: {typlist[luck][2]}, Stage: {typlist[luck][1]}*", inline=False)
        await client.say(embed=embed)
        for i in damages:
            if i[3] in specWounds:
                 await specialWounds(client,ctx,i[3])
             #embed.add_field(name="Severity", value=severity, inline=True)
             #embed.add_field(name="Aim", value=aim, inline=True)
    return True


#dice rolling.
#TODO: Add memorized rolls, roll series, independent dice
@client.command(pass_context=True,description="See >tag roll for help",aliases=["r","R"])
async def roll(ctx,formula="3d20+4",*comment):
    formula_in=formula
    #print(comment)
    #print(type(comment))
    if comment==():
        comment=""
    if formula[0]=="#":
        comment2=(formula[1:],)
        if comment!="":
            comment=comment2+comment
        else:
            comment=comment2
        formula="3d20+4"
    loc=ctx.message.server.id
    if (loc=="283841245975937034") and (formula=="3d20+4"):
        formula="3d20+6"
    if "d" in formula.casefold():
        d_pattern=re.compile("(d|D)(\d)*")
        d_match=d_pattern.search(formula)
        if d_match.group()[0]=="D":
            keep=False
        else:
            keep=True
        dice=int(d_match.group()[1:])   
    else:
        dice=20
        keep=True
    #print(f"dice: {dice}")
    
    if ("+" in formula) or ("-" in formula):
        if ("++" in formula) or ("--" in formula):
            mod_pattern=re.compile("(\+\+|\-\-)(\d)*")
            mod_match=mod_pattern.search(formula)
            modifier=int(mod_match.group()[1:]) 
            if loc=="283841245975937034":
                modifier=6+modifier
            else:
                modifier=4+modifier
        else:
            mod_pattern=re.compile("(\+|\-)+(\d)*")
            mod_match=mod_pattern.search(formula)
            modifier=int(mod_match.group())
    else:
        if dice==20:
            if loc=="283841245975937034":
                modifier=6
            else:
                modifier=4
        else:
            modifier=0
    #print(f"modifier: {modifier}")
    
    brief=False
    if "b" in formula:
        brief=True
    if "x" in formula:
        if "xb" in formula:
            brief=True
            x_pattern=re.compile("xb(\d)*")
            x_match=x_pattern.search(formula)
            if x_match:
                repeats=int(x_match.group()[2:])
        else:
            brief=False
            x_pattern=re.compile("x(\d)*")
            x_match=x_pattern.search(formula)
            if x_match:
                repeats=int(x_match.group()[1:])
    else:
        repeats=1
    #print(f"repeats: {repeats}")
    
    i_pattern=re.compile("(\A)(\d)*")
    i_match=i_pattern.search(formula)
    if i_match:
        try:
            i=int(i_match.group())
        except ValueError:
            if dice==20:
                if formula_in[0]=="d":
                    if "d20" in formula_in:
                        i=1
                else:
                    i=3
            else:
                i=1
            #print("ValueError")
    else:
        print("i-error in roll!")
        return
    #print(f"die #s: {i}")
          
    if "!" in formula:
        explode=True
    else:
        explode=False
    
    requester=ctx.message.author.name
    out_roll=[f"{requester}: ("]
    
    for j in range(0,repeats):
        if (j!=0):
            out_roll.append(", (")
        result=[]
        for x in range(0,i):
            result.append(random.randint(1,dice))
        if explode==True:
            loops=len(result)
            k=0
            while (k < loops):
                #print(k)
                if result[k]==dice:
                    result.append(random.randint(1,dice))
                    loops=len(result)
                k=k+1
                if k>100: #save us from inifinite loops
                    break
        result_i= [int(i) for i in result]
        
        if keep==True:
            highest=max(result_i)
        else:
            highest=sum(result)
        #print(keep)
        if keep==True:
            for x in range(0,len(result_i)):
                if result_i[x]!=highest:
                    if keep==True:
                        out_roll.append("~~")
                        out_roll.append(str(result_i[x]))
                        out_roll.append("~~")
                    else:
                        out_roll.append(str(result_i[x]))
                else:
                    out_roll.append(str(result_i[x]))
                if x!=len(result_i)-1:
                    out_roll.append("+")
        else:
            highest=sum(result)
            for x in range(0,len(result_i)):
                    out_roll.append(str(result_i[x]))
                    if x!=len(result_i)-1:
                        out_roll.append("+")
        out_roll.append(")")
        if modifier>0:
            out_roll.append("+")
        if dice==20 and highest==20:
            if modifier != 0:
                out_roll.append(f"{modifier}=__**{highest+modifier}**__")
            else:
                out_roll.append(f"=__**{highest+modifier}**__")
        elif modifier==0:
            out_roll.append(f"=**{highest}**")
        else:
            out_roll.append(f"{modifier}=**{highest+modifier}**")
        #print(out_roll)
    if brief==True:
        out_saved=out_roll
        out_roll=[f"{requester}: "]
        brief_pattern=re.compile("\*\*\d+\*\*")
        brief_match=brief_pattern.findall(''.join(out_saved))
        for k in range(0,len(brief_match)):
            if k==len(brief_match)-1:
                critcheck=brief_match[k].replace("*","")
                if (int(critcheck)-modifier)==dice:
                    out_roll.append(f"__{brief_match[k]}__")
                else:
                    out_roll.append(f"{brief_match[k]}")
            else:
                critcheck=brief_match[k].replace("*","")
                if (int(critcheck)-modifier)==dice:
                    out_roll.append(f"__{brief_match[k]}__, ")
                else:
                    out_roll.append(f"{brief_match[k]}, ")
    if comment!="":
        out_roll.append(f" #{' '.join(comment)}")
    await client.say(''.join(out_roll))


tag_muted=False #global

#tags are text blocks, useful for re-posting common infomration like character appearance etc. Also memes. So many memes.
@client.command(pass_context=True,description="Memorize Texts. Add a tag by writing >tag create title content; update by >tag update title newcontent; delete by >tag delete title",aliases=["effect","Effect","Tag"])
@commands.check(no_pm)
async def tag(ctx, tag=None, content1=None, *,content2=None):
    global tags
    if (tag==None) or (tag.casefold()=="empty"):
        await client.add_reaction(ctx.message,"❌")
    elif tag.casefold()=="create".casefold():
        global tag_muted
        if tag_muted==True:
            await client.say("Disabled until you fuckers calm down.")
            return
        elif (content1==None) or (content2==None):
            await client.say("Need a name and content for the tag.")
            return
        elif any(e[0].casefold() == content1.casefold() for e in tags):
            await client.say("Name already taken.")
            return
        gc = gspread.authorize(credentials)
        RefSheet = gc.open_by_key('1LOZkywwxIWR41e8h-xIMFGNGMe7Ro2cOYBez_xWm6iU')
        tagsSheet = RefSheet.worksheet("Tags")
        new_tag=tagsSheet.find("empty")
        tagsSheet.update_cell(new_tag.row,new_tag.col, content1.casefold())
        tagsSheet.update_cell(new_tag.row,new_tag.col+1, content2)
        tagsSheet.update_cell(new_tag.row,new_tag.col+2, ctx.message.author.id)
        tagsSheet.update_cell(new_tag.row+1,new_tag.col, "empty")
        tags = tagsSheet.get_all_values()
        await client.say(f"{content1} has been created.")
    elif tag_muted==False:
        if tag.casefold()=="list":
            await client.say("List of all current tags: https://docs.google.com/spreadsheets/d/e/2PACX-1vRjroKacZBQrkIEayrhHuFtA_5mAL_C48Y-4taCjZ5k0mNXAPTi5diZAiZ-7l-Uai5xvbNomF_s1-0m/pubhtml")
        elif tag.casefold()=="owner":
            gc = gspread.authorize(credentials)
            RefSheet = gc.open_by_key('1LOZkywwxIWR41e8h-xIMFGNGMe7Ro2cOYBez_xWm6iU')
            tagsSheet = RefSheet.worksheet("Tags")
            target_tag=tagsSheet.find(content1.casefold())
            ownerID=tagsSheet.cell(target_tag.row,target_tag.col+2).value
            print(ownerID)
            print(type(ownerID))
            print(client.get_all_members())
            tagowner=discord.utils.get(client.get_all_members(), id=str(ownerID))
            if tagowner is None:
                await client.say(f"{content1} is owned by an unknown user.")
                return
            await client.say(f"{content1} is owned by {tagowner.name}.")
            return
        elif tag.casefold()=="delete":
            gc = gspread.authorize(credentials)
            RefSheet = gc.open_by_key('1LOZkywwxIWR41e8h-xIMFGNGMe7Ro2cOYBez_xWm6iU')
            tagsSheet = RefSheet.worksheet("Tags")
            target_tag=tagsSheet.find(content1.casefold())
            if ctx.message.author.id==tagsSheet.cell(target_tag.row, target_tag.col+2).value or ctx.message.author.id=="138340069311381505":
                tagsSheet.delete_row(target_tag.row)
                tags = tagsSheet.get_all_values()
                await client.say(f"{content1} deleted.")
            else:
                await client.say("Not your tag!")
        elif tag.casefold()=="update":
            gc = gspread.authorize(credentials)
            RefSheet = gc.open_by_key('1LOZkywwxIWR41e8h-xIMFGNGMe7Ro2cOYBez_xWm6iU')
            tagsSheet = RefSheet.worksheet("Tags")
            target_tag=tagsSheet.find(content1.casefold()) #change to findall, discard non-titles
            print(f"{target_tag.row},{target_tag.col}")
            if target_tag.col!=1:
                print("tag column error!")
                return
            if ctx.message.author.id==tagsSheet.cell(target_tag.row, target_tag.col+2).value or ctx.message.author.id=="138340069311381505":
                tagsSheet.update_cell(target_tag.row,target_tag.col+1, content2)
                tags = tagsSheet.get_all_values()
                await client.say(f"{content1} updated.")
            else:
                await client.say("Not your tag!")
        elif any(e[0] == tag.casefold() for e in tags):
            for i in tags:
                if i[0]==tag.casefold():
                    await client.say(i[1])
        else:
            if not (await ctx.invoke(wound,severity=str(tag))):
                await client.add_reaction(ctx.message,"❌")

#Can use this to stop tag abuse
@client.command(pass_context=True,hidden=True)
async def tagToggle(ctx):
    global tag_muted
    if ctx.message.author.id not in owner:
        await client.say("🌚")
        return
    if tag_muted==False:
        tag_muted=True
        await client.add_reaction(ctx.message,"🔥")
    elif tag_muted==True:
        tag_muted=False
        await client.add_reaction(ctx.message,"🌊")
    else:
        await client.say("Beep Boop. Error.")

#convert from inches to cm. Very, very basic. 
@client.command(pass_context=True,aliases=["conv"],description="Fuck the Imperial System.")
async def convert(ctx, inches):
    ft_symbol="'"
    ft = inches.find(ft_symbol)
    if ft != -1:
        inch=12*int(inches[:ft])
        if not inches.endswith(ft_symbol):
            inch=inch+int(inches[ft+1:])
    else:
        inch=int(inches)
    await client.say(f"{inches} is equal to {inch*2.54}cm")

#TODO: Replace with trueSkill
#GLICKO MODUlE
#defining parameters for the glicko system
scale=173.7178
tau=0.3
#name, rating, rd
#-------------
test="test"

@client.group(pass_context=True)
async def rank(ctx):
    if ctx.invoked_subcommand is None:
        await client.say('Available commands: show, make, update')
        
@rank.command(pass_context=True)
async def ladder(ctx, mode="lax"):
    loc=ctx.message.server.id        
    with open(f"glicko{loc}.txt") as f:
        rankings = json.load(f)
    sort_rank=sorted(rankings,key=operator.itemgetter(1), reverse=True)
    ladder_names=[]
    if mode.casefold()=="strict":
        RD_cutoff=100
    elif mode.casefold()=="lax":
        RD_cutoff=200    
    else:
        try:
            RD_cutoff=int(mode)
        except ValueError:
            RD_cutoff=200 #lax
    for i in sort_rank:
        if i[2]<RD_cutoff:
            ladder_names.append([i[0],int(round(i[1],0))])
    ladder_list=list(enumerate(ladder_names,1))
    ladder_str=[f"Ladder for {ctx.message.server}"+os.linesep]
    for x in ladder_list:
        pos = await int_to_roman(x[0])
        ladder_str+=((f"**{pos}**. {x[1][0]}  *{x[1][1]}*"+os.linesep))
    ladder_str=''.join(ladder_str)
    ladder_str+=f"_Only capes under {RD_cutoff} RD are included here. NB this only reflects 1v1 performance._"
    await client.say(ladder_str)

        
        
    
@rank.command(pass_context=True)
async def show(ctx, cape=None):
    loc=ctx.message.server.id
    if cape==None:
        await client.say(f"Forgot something? Maybe your name, {ctx.message.author.nick}?")
    with open(f"glicko{loc}.txt") as f:
        rankings = json.load(f)
    #print(rankings)
    for i in rankings:
        if i[0]==cape.casefold():
            await client.say(f"{cape} - Rating: {round(i[1],1)}, RD: {round(i[2],1)}, sigma: {round(i[3],3)}")
            return
    await client.say(f"{cape} not found.")
    #print(rankings)
    
@rank.command(pass_context=True,name="help")
async def _help(ctx,cape=None):
    await client.say("To enter your cape into the database, use "">rank make halcyon"". If you finish a fight, use "">rank update luke vader win"". In this one, luke won against vader. If luke had lost, you would write "">rank update luke vader loss"". Only one person needs to do this, the other's rank is updated automatically. You can see your rating by using "">rank show halcyon"". This is still a pretty early build, so expect bugs and shit. Consider this a beta that will probably get wiped at some point.")
    

@rank.command(pass_context=True)
async def make(ctx,cape=None):
    loc=ctx.message.server.id
    if cape==None:
        await client.say("I do need a name for you if this is going to work.")
    entry=[]
    cape=cape.casefold()
    entry.append(cape)
    entry.append(1500) #default values. Rating, Rating deviation, volatility
    entry.append(350)
    entry.append(0.06)
    if os.path.isfile(f"glicko{loc}.txt"):
        with open(f"glicko{loc}.txt",mode="r+") as f:
            rankings = json.load(f)
            if cape in sum(rankings,[]):
                await client.say("Duplicate name.")
                return
            f.seek(0)
            f.truncate()
            rankings.append(entry)
            json.dump(rankings,f)
    else:
         with open(f"glicko{loc}.txt",mode="w+") as f:
             rankings=[]
             f.seek(0)
             f.truncate()
             rankings.append(entry)
             json.dump(rankings,f)
    await client.say(f"{cape} added to database. Rating: 1500")
    #print(rankings)
    
@rank.command(pass_context=True)
async def odds(ctx,cape1,cape2):
    loc=ctx.message.server.id
    with open(f"glicko{loc}.txt") as f:
        rankings = json.load(f)
    c1=False
    c2=False
    for i in rankings:
        if i[0]==cape1.casefold():
            c1=i
        if i[0]==cape2.casefold():
            c2=i
    if c1==False:
        await client.say(f"Cannot find {cape1}.")
        return
    elif  c2==False:
        await client.say(f"Cannot find {cape2}.")
        return
    rating_cape=c1[1]
    rd_cape=c1[2]
    rating_opponent=c2[1]
    rd_opponent=c2[2]
    def g(rd):
        q=math.log(10)/400
        return 1/math.sqrt(1+3*(q**2)*(rd**2)/(math.pi**2))
    #print(g(math.sqrt(rd_cape**2+rd_opponent**2)))
    e=1/(1+10**(-g(math.sqrt(rd_cape**2+rd_opponent**2))*(rating_cape-rating_opponent)/400))
    prob=round(e*100,0)
    dec_odds=round(100/prob,2)
    dec_odds_loss=round(100/(100-prob),2)
    await client.say(f"{cape1} beats {cape2} with {prob}% chance. This represents odds of {dec_odds} for a win. ({dec_odds_loss} if you bet on {cape2}).")
    #print(e)


@rank.command(aliases=["u"],pass_context=True)
async def update(ctx,cape, opponent, outcome,inv=False):
    loc=ctx.message.server.id
    if type(outcome)==str:
        if outcome=="win":
            outcome=1
        elif outcome=="loss":
            outcome=0
        else:
            outcome=int(outcome)
    #print(f"Start: {outcome}, {inv}, {cape}, {opponent}")
    with open(f"glicko{loc}.txt") as f:
        rankings = json.load(f)
    c1=False
    c2=False
    for i in rankings:
        if i[0]==cape.casefold():
            c1=i
        elif i[0]==opponent.casefold():
            c2=i
    if c1==False:
        await client.say(f"Cannot find {cape}.")
        return
    elif  c2==False:
        await client.say(f"Cannot find {opponent}.")
        return
    rating_cape=(c1[1]-1500)/scale
    rd_cape=c1[2]/scale
    vola_cape=c1[3]
    rating_opponent=(c2[1]-1500)/scale
    rd_opponent=c2[2]/scale
    g_phi_op=g_phi(rd_opponent)
    #print(f"g phi of opponent: {g_phi_op}")
    e=1/(1+math.exp((-g_phi_op)*(rating_cape-rating_opponent)))

    #print(f"E: {e} by {-g_phi_op}*({rating_cape}-{rating_opponent})")
    variance=1/((g_phi_op**2*e*(1-e)))
    #print(f"variance is {variance}")
    
    if variance>6:
        #print(f"variance corrected from {variance}")
        variance=6
        
    
    
    #change in rating, based on outcomes only
    delta=variance*(g_phi_op*(outcome-e))
    #print(f"delta is {delta} via {variance}*({g_phi_op}*({outcome}-{e}))")
    
    #new sigma
    a=math.log(vola_cape**2)
    epsilon=0.000001
    def f(x):
        result=(math.exp(x)*(delta**2-rd_cape**2-variance-math.exp(x))/2*(rd_cape**2+variance+math.exp(x))**2)-((x-a)/tau**2)
        return result
    alpha=a
    #print(f"delta squared: {delta**2}")
    #print(f"RD times variance: {rd_cape**2+variance}")
    if ((delta**2)>(rd_cape**2+variance)):
        b=math.log(delta**2-rd_cape**2-variance)
        #print("big delta")
    elif((delta**2)<=(rd_cape**2+variance)):
        k=1
        #print("smol delta")
        while (f(a-k*tau)<0):
            k+=1
            print(k)
        b=a-k*tau  
    else:
        print("ERROR in volatility update")
        return
    f_a,f_b = f(alpha),f(b)
    while (abs(b-alpha)>epsilon):
        c=alpha+(alpha-b)*f_a/(f_b-f_a)
        f_c=f(c)
        if (f_c*f_b<0):
            alpha=b
            f_a=f_b
        else:
            f_a=f_a/2
        b=c
        f_b=f_c
    sigma_new=math.exp(alpha/2)
    
    rd_period=math.sqrt(rd_cape**2+sigma_new**2)
    rd_new=1/(math.sqrt((1/rd_period**2)+(1/variance)))
    rating_new=rating_cape+((rd_new**2)*(g_phi_op*(outcome-e)))

    rd_new=scale*rd_new
    rating_new=(scale*rating_new)+1500
    up_func=client.get_command("rank update")
    
    if inv==False:
        await ctx.invoke(up_func,cape=opponent,opponent=cape,outcome=abs(1-outcome),inv=True)
    #capename, ranking, RD, volatility
    
    #is RD is over 350, reset to the maximum of 350
    if rd_new>350:
        rd_new=350
    
    with open(f"glicko{loc}.txt") as f:
        rankings = json.load(f)
    for i in rankings:
        if i[0]==cape.casefold():
            i[1]=rating_new
            i[2]=rd_new
            i[3]=sigma_new
            #print(f" {cape} Rating, RD, sigma:{rating_new}, {rd_new}, {sigma_new}")
    
    with open(f"glicko{loc}.txt",mode="r+") as f:
        f.seek(0)
        f.truncate()
        json.dump(rankings,f)
    
    if inv==False:
        for i in rankings:
            if i[0]==opponent.casefold():
                op_rating=round(i[1],1)
        await client.say(f"Ratings updated. New rating for {cape}: {round(rating_new,1)} New rating for {opponent}: {op_rating}")
        

def g_phi(rd_cape):
    g_phi_r=1/(math.sqrt(1+(3*(rd_cape**2)/math.pi**2)))
    return g_phi_r

@client.group(pass_context=True,description="Available commands: show, make, update, income. Show your balance, Make an account, Update your balance, Increase your weekly income.")
async def account(ctx):
    if ctx.invoked_subcommand is None:
        await client.say('Available commands: show, make, update, income. Show your balance, Make an account, Update your balance, Increase your weekly income.')

@account.command(pass_context=True,description="Check how many more donuts you can afford.")
async def show(ctx, cape=None):
    loc=ctx.message.server.id
    with open(f"cash{loc}.txt") as f:
        accounts = json.load(f)
    #print(accounts)
    for i in accounts:
        if i[0]==cape.casefold():
            await client.say(f"Balance for {cape}: {i[1]}$. Income: {i[2]}$.")
    #print(accounts)

@account.command(pass_context=True,description="Use this to add your cape to the database and gain access to the other commands. Your cape name is your 'key'.")
async def make(ctx,cape=None,amount=0,income=0):
    loc=ctx.message.server.id
    if (ctx.message.channel.id != "478240151987027978") and (ctx.message.channel.id != "435874236297379861") and (ctx.message.channel.id != "537152965375688719"):
        await client.say("BoK only operates in #faction-actions!")
        return
    if cape==None:
        await client.say("I do need a name for you if this is going to work.")
    entry=[]
    entry.append(cape.casefold()) 
    entry.append(int(amount))
    entry.append(int(income))
    if os.path.isfile(f"cash{loc}.txt"):
        with open(f"cash{loc}.txt",mode="r+") as f:
            accounts = json.load(f)
            if cape.casefold() in sum(accounts,[]):
                await client.say("Duplicate name.")
                return
            f.seek(0)
            f.truncate()
            accounts.append(entry)
            json.dump(accounts,f)
    else:
         with open(f"cash{loc}.txt",mode="w+") as f:
             accounts=[]
             f.seek(0)
             f.truncate()
             accounts.append(entry)
             json.dump(accounts,f)
    await client.say(f"Account opened for {cape}. Amount: {amount}$. Income: {income}$. Welcome to Bank of Kingfisher!")
    
@account.command(aliases=["u"],pass_context=True,description="Keep track of expenses and gains with this.")
async def update(ctx,cape, amount):
    loc=ctx.message.server.id
    if (ctx.message.channel.id != "478240151987027978") and (ctx.message.channel.id != "435874236297379861") and (ctx.message.channel.id != "537152965375688719"):
        await client.say("BoK only operates in #faction-actions!")
        return
    with open(f"cash{loc}.txt") as f:
        accounts = json.load(f)
    c1=False
    for i in accounts:
        if i[0]==cape.casefold():
            c1=i
    if c1==False:
        await client.say(f"Cannot find {cape}.")
    for i in accounts:
        if i[0]==cape.casefold():
            i[1]=i[1]+int(amount)
            await client.say(f"New balance for {cape}: {i[1]}$")
    with open(f"cash{loc}.txt",mode="r+") as f:
        f.seek(0)
        f.truncate()
        json.dump(accounts,f)
        
@account.command(aliases=["s"],pass_context=True,description="Send money to another account.")
async def send(ctx,cape,target, amount):        
    loc=ctx.message.server.id
    if (ctx.message.channel.id != "478240151987027978") and (ctx.message.channel.id != "435874236297379861") and (ctx.message.channel.id != "537152965375688719"):
        await client.say("BoK only operates in #faction-actions!")
        return
    with open(f"cash{loc}.txt") as f:
        accounts = json.load(f)
    c1=False
    for i in accounts:
        if i[0]==cape.casefold():
            c1=i
        if i[0]==target.casefold():
            c2=i
    if c1==False:
        await client.say(f"Cannot find sender {cape}.")
    if c2==False:
        await client.say(f"Cannot find receiver {target}.")
    for i in accounts:
        if i[0]==cape.casefold():
            i[1]=i[1]+int(amount)*-1
            await client.say(f"New balance for {cape}: {i[1]}$")
        if i[0]==target.casefold():
            i[1]=i[1]+int(amount)
            await client.say(f"New balance for {target}: {i[1]}$")
    with open(f"cash{loc}.txt",mode="r+") as f:
        f.seek(0)
        f.truncate()
        json.dump(accounts,f)    

@account.command(aliases=["i"],pass_context=True,description="Adjust your periodic income here. Use the weekly amount.")
async def income(ctx,cape, amount):
    loc=ctx.message.server.id
    if (ctx.message.channel.id != "478240151987027978") and (ctx.message.channel.id != "435874236297379861") and (ctx.message.channel.id != "537152965375688719"):
        await client.say("BoK only operates in #faction-actions!")
        return
    with open(f"cash{loc}.txt") as f:
        accounts = json.load(f)
    c1=False
    for i in accounts:
        if i[0]==cape.casefold():
            c1=i
    if c1==False:
        await client.say(f"Cannot find {cape}.")
    for i in accounts:
        if i[0]==cape.casefold():
            i[2]=i[2]+int(amount)
            await client.say(f"New income for {cape}: {i[2]}$")
    with open(f"cash{loc}.txt",mode="r+") as f:
        f.seek(0)
        f.truncate()
        json.dump(accounts,f)
        
    

async def account_decay():
        loc="465651565089259521"
        decay=0.9**(1/7) #10% decay per week
        #gh loc="465651565089259521"
        #vanwiki loc="434729592352276480"
        channel = client.get_channel("478240151987027978") # channel ID goes here
        #GH 478240151987027978
        #vanwiki 435874236297379861
        last_updated=[]
        while True:
            if os.path.isfile(f"decay{loc}.txt"):
                with open(f"decay{loc}.txt",mode="r+") as f:
                    last_updated = json.load(f)
                    if last_updated[0]-time.time()<-60*60*24:
                        if os.path.isfile(f"cash{loc}.txt"):
                            with open(f"cash{loc}.txt",mode="r+") as g:
                                accounts = json.load(g)
                                g.seek(0)
                                g.truncate()
                                wealth=0
                                for i in accounts:
                                    i[1]=round(i[1]*decay)
                                    i[1]=i[1]+round((i[2]/7))
                                    wealth+=i[1]
                                json.dump(accounts,g)
                            await client.send_message(channel,f"Daily Expenses computed. Total accrued wealth: {wealth}$")
                        else:
                            client.client.send_message(channel,"No accounts on file.")
                        f.seek(0)
                        f.truncate()
                        last_updated=[]
                        last_updated.append(time.time())
                        json.dump(last_updated,f)
            else:
                with open(f"decay{loc}.txt",mode="w+") as f:
                    f.seek(0)
                    f.truncate()
                    last_updated=[]
                    last_updated.append(time.time())
                    json.dump(last_updated,f)
            await asyncio.sleep(60*60*3) # task runs every 3 hours
        

async def rank_decay():
        c= 60 # c = 60, assuming a rating decay period of a month, and a typical rating of 150
        # c is the result of 350=sqroot(typical rating**2+rating decay period*c)
        loc="465651565089259521"
        #gh loc="465651565089259521"
        #vanwiki loc="434729592352276480"
        channel = client.get_channel("478240151987027978") # channel ID goes here
        #GH 478240151987027978 facacs
        #vanwiki 435874236297379861 testing
        last_updated=[]
        while True:
            if os.path.isfile(f"glicko_decay{loc}.txt"):
                with open(f"glicko_decay{loc}.txt",mode="r+") as f:
                    last_updated = json.load(f)
                    if last_updated[0]-time.time()<-60*60*24:
                        if os.path.isfile(f"glicko{loc}.txt"):
                            with open(f"glicko{loc}.txt",mode="r+") as g:
                                ranks = json.load(g)
                                g.seek(0)
                                g.truncate()
                                avg_rank=0
                                avg_rd=0
                                for i in ranks:
                                    if i[2]>150:
                                        i[2]=min(round(math.sqrt(i[2]**2+c**2),2),350)
                                    else:
                                        i[2]=min(round(math.sqrt(i[2]**2+(c/2)**2),2),350)
                                    avg_rank+=i[1]
                                    avg_rd+=i[2]
                                json.dump(ranks,g)
                            await client.send_message(channel,f"Daily RD decay computed. Average Rating: {round(avg_rank/len(ranks),0)} Average RD: {round(avg_rd/len(ranks),0)}")
                        else:
                            client.client.send_message(channel,"No ranks existing!")
                        f.seek(0)
                        f.truncate()
                        last_updated=[]
                        last_updated.append(time.time())
                        json.dump(last_updated,f)
            else:
                with open(f"glicko_decay{loc}.txt",mode="w+") as f:
                    f.seek(0)
                    f.truncate()
                    last_updated=[]
                    last_updated.append(time.time())
                    json.dump(last_updated,f)
            await asyncio.sleep(60*60*3) # task runs every 3 hours      
        

###Bot runs here
with open("Token.txt", 'r') as f:
        token=f.read()
client.run(token)
